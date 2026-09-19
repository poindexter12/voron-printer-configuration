"""Test suite for the STRINGING_TEST macro.

Two kinds of coverage here:

1. A frozen golden-render comparison, which catches any unintended change to
   the emitted G-code.
2. Behavioural tests that assert the macro implements its documented contract
   independently of the golden file, so a deliberate re-render cannot silently
   bless a broken retraction ladder or bad pillar geometry.
"""

import math
import re

import pytest
from utils.gcode_helpers import render_macro_gcode, run_macro_comparison_test

MACRO_FILE = '../stringing_test/stringing_test.cfg'
MACRO_NAME = 'STRINGING_TEST'

stringing_test_data = {
    'name': 'stringing_test',
    'orig_file': '../fixtures/expected_gcode/stringing_test/stringing_test.gcode',
    'render_file': '../stringing_test/stringing_test.cfg',
    'macro_name': MACRO_NAME,
    'params': {'PREP': 0}
}

# Macro defaults, mirrored here so the tests state the contract rather than
# read it back out of the macro they are checking.
DEFAULTS = {
    'CENTER_X': 175.0,
    'CENTER_Y': 175.0,
    'PILLAR_SIZE': 15.0,
    'PILLAR_SPACING': 90.0,
    'BAND_COUNT': 5,
    'LAYERS_PER_BAND': 10,
    'RETRACT_START': 0.2,
    'RETRACT_INCREMENT': 0.2,
    'LAYER_HEIGHT': 0.2,
    'LINE_WIDTH': 0.4,
    'FILAMENT_DIAMETER': 1.75,
    'EXTRUSION_MULTIPLIER': 1.0,
}

PREP_COMMANDS = ['M140', 'M190', 'G28', 'QUAD_GANTRY_LEVEL',
                 'BED_MESH_CALIBRATE', 'M109']


def render(**overrides):
    """Render STRINGING_TEST with PREP off unless a test says otherwise."""
    params = {'PREP': 0}
    params.update(overrides)
    return render_macro_gcode(MACRO_FILE, MACRO_NAME, params)


def expected_e_per_mm(line_width, layer_height, filament_diameter, multiplier):
    """The extrusion model the macro documents: line area over filament area."""
    line_area = ((line_width - layer_height) * layer_height
                 + math.pi * (layer_height / 2) ** 2)
    filament_area = math.pi * (filament_diameter / 2) ** 2
    return (line_area / filament_area) * multiplier


@pytest.mark.stringing
def test_stringing_test_macro(results_dir):
    """Test the stringing test macro against the frozen reference render."""
    diff_count = run_macro_comparison_test(
        results_dir,
        stringing_test_data['orig_file'],
        stringing_test_data['render_file'],
        stringing_test_data['macro_name'],
        stringing_test_data['params'],
        stringing_test_data['name']
    )
    assert diff_count == 0, f"Macro test failed with {diff_count} differences"


@pytest.mark.stringing
def test_renders_non_empty():
    """The macro renders and produces G-code."""
    rendered = render()
    assert rendered
    assert 'G1' in rendered


@pytest.mark.stringing
def test_prep_commands_included_when_prep_set():
    """PREP=1 emits the heat/home/level/mesh preamble."""
    rendered = render(PREP=1)
    for command in PREP_COMMANDS:
        assert command in rendered, f"PREP=1 should emit {command}"


@pytest.mark.stringing
def test_prep_commands_omitted_when_prep_clear():
    """PREP=0 assumes the printer is ready and skips the preamble.

    G28 is the load-bearing one: homing mid-test would ruin the tower.
    """
    rendered = render(PREP=0)
    for command in ['M190', 'G28', 'QUAD_GANTRY_LEVEL', 'BED_MESH_CALIBRATE']:
        assert command not in rendered, f"PREP=0 should not emit {command}"


@pytest.mark.stringing
def test_uses_relative_extrusion_and_absolute_positioning():
    """Retraction maths assume M83 relative E and G90 absolute XYZ."""
    rendered = render()
    assert 'M83' in rendered, "Missing relative extrusion mode"
    assert 'G90' in rendered, "Missing absolute positioning mode"


@pytest.mark.stringing
def test_band_markers_report_documented_retraction_ladder():
    """Band N retraction is RETRACT_START + N * RETRACT_INCREMENT.

    This is how the operator reads the printed tower, so the M117 label has to
    match the retraction actually commanded in that band.
    """
    rendered = render()
    labels = re.findall(r'M117 Band (\d+)/(\d+): retract ([\d.]+)mm', rendered)
    assert len(labels) == DEFAULTS['BAND_COUNT'], \
        f"Expected {DEFAULTS['BAND_COUNT']} band markers, got {len(labels)}"

    for index, (band_number, band_total, retract) in enumerate(labels):
        expected = DEFAULTS['RETRACT_START'] + index * DEFAULTS['RETRACT_INCREMENT']
        assert int(band_number) == index + 1
        assert int(band_total) == DEFAULTS['BAND_COUNT']
        assert float(retract) == pytest.approx(expected, abs=0.005), \
            f"Band {index + 1} labelled {retract}mm, expected {expected}mm"


@pytest.mark.stringing
@pytest.mark.parametrize('band_count,layers_per_band', [(1, 1), (3, 5), (8, 2)])
def test_band_and_layer_counts_follow_parameters(band_count, layers_per_band):
    """BAND_COUNT and LAYERS_PER_BAND drive the tower's structure."""
    rendered = render(BAND_COUNT=band_count, LAYERS_PER_BAND=layers_per_band)

    markers = re.findall(r'M117 Band \d+/\d+', rendered)
    assert len(markers) == band_count

    # Each layer commands one Z move per pillar pass, preceded by a single
    # Z positioning move; count distinct Z heights instead of raw moves.
    z_values = {float(z) for z in re.findall(r'G1 Z([\d.]+) F1200', rendered)}
    # layers + the first-layer skirt Z + the final park Z
    assert len(z_values) >= band_count * layers_per_band, \
        f"Expected at least {band_count * layers_per_band} distinct layer heights"


@pytest.mark.stringing
def test_retraction_values_match_band_ladder():
    """Every retraction commanded is one of the ladder values, and all appear."""
    rendered = render()
    expected = {
        round(DEFAULTS['RETRACT_START'] + i * DEFAULTS['RETRACT_INCREMENT'], 5)
        for i in range(DEFAULTS['BAND_COUNT'])
    }
    commanded = {round(float(v), 5)
                 for v in re.findall(r'G1 E-([\d.]+) F', rendered)}
    assert commanded == expected, \
        f"Retractions {sorted(commanded)} do not match ladder {sorted(expected)}"


@pytest.mark.stringing
def test_pillars_sit_either_side_of_centre():
    """Pillar centres are CENTER_X +/- PILLAR_SPACING/2, each PILLAR_SIZE wide."""
    rendered = render()
    half = DEFAULTS['PILLAR_SIZE'] / 2
    left = DEFAULTS['CENTER_X'] - DEFAULTS['PILLAR_SPACING'] / 2
    right = DEFAULTS['CENTER_X'] + DEFAULTS['PILLAR_SPACING'] / 2

    for edge in (left - half, left + half, right - half, right + half):
        assert f"X{edge:.3f}" in rendered, f"Missing pillar edge at X{edge:.3f}"


@pytest.mark.stringing
def test_pillar_extrusion_matches_documented_area_model():
    """Each pillar edge extrudes e_per_mm * PILLAR_SIZE."""
    rendered = render()
    e_per_mm = expected_e_per_mm(
        DEFAULTS['LINE_WIDTH'], DEFAULTS['LAYER_HEIGHT'],
        DEFAULTS['FILAMENT_DIAMETER'], DEFAULTS['EXTRUSION_MULTIPLIER'])
    expected = f"E{e_per_mm * DEFAULTS['PILLAR_SIZE']:.5f}"
    assert expected in rendered, \
        f"Expected pillar edge extrusion {expected} from the area model"


@pytest.mark.stringing
def test_parks_above_the_finished_tower():
    """The final move clears the tower by 5mm so the nozzle does not sit on it."""
    rendered = render()
    tower_height = (DEFAULTS['BAND_COUNT'] * DEFAULTS['LAYERS_PER_BAND']
                    * DEFAULTS['LAYER_HEIGHT'])
    assert f"G1 Z{tower_height + 5:.3f}" in rendered, \
        f"Expected final park at Z{tower_height + 5:.3f}"
    assert 'M117 Stringing test done' in rendered
