"""Test suite for the PRESSURE_ADVANCE_CALIBRATION macros.

Covers the generator (_PRESSURE_ADVANCE_GENERATE) and the public wrapper
(PRESSURE_ADVANCE_CALIBRATION) that Mainsail calls.

There is no golden-render fixture here on purpose. This macro had no coverage
at all and was non-functional until 2026-09-18 (see the repo history), so a
frozen render would only have preserved broken output. These tests assert the
documented contract instead, and a fixture can be added later once the
printed result has been validated on the machine.
"""

import re

import pytest

from utils.gcode_helpers import extract_macro_gcode, render_macro_gcode

MACRO_FILE = '../pressure_advance/pressure_advance_calibration.cfg'
GENERATE_MACRO = '_PRESSURE_ADVANCE_GENERATE'
PUBLIC_MACRO = 'PRESSURE_ADVANCE_CALIBRATION'

# Defaults declared by the macro, restated here so the tests assert a contract
# rather than read it back out of the file under test.
DEFAULTS = {
    'PA_START_VALUE': 0.0,
    'PA_INCREMENT': 0.005,
    'PATTERN_COUNT': 17,
    'WALL_COUNT': 3,
    'ANCHOR_FRAME_PERIMETERS': 4,
    'NOZZLE_TEMP': 215,
    'BED_TEMP': 75,
}

# The macro targets a 350mm bed with a fixed pattern footprint.
BED_SIZE = 350.0
PATTERN_WIDTH = 84.72
PATTERN_HEIGHT = 53.99


def generate(**overrides):
    """Render the generator macro with the given parameter overrides."""
    return render_macro_gcode(MACRO_FILE, GENERATE_MACRO, dict(overrides))


def pa_values(rendered):
    """Every pressure advance value actually commanded, in order."""
    return [float(v) for v in
            re.findall(r'SET_PRESSURE_ADVANCE ADVANCE=([\d.]+)', rendered)]


@pytest.mark.pressure_advance
def test_generator_emits_gcode(results_dir):
    """The generator emits its command list rather than swallowing it.

    Regression guard: the command list used to be passed to a non-existent
    printer.save_variable() call, so the macro produced no G-code at all.
    """
    rendered = generate()
    commands = [line.strip() for line in rendered.splitlines()
                if line.strip() and not line.strip().startswith('#')]
    assert len(commands) > 100, \
        f"Generator emitted only {len(commands)} commands; it should emit the full pattern"

    import os
    with open(os.path.join(results_dir, 'pressure_advance_rendered.gcode'),
              'w', encoding='utf-8') as handle:
        handle.write(rendered)


@pytest.mark.pressure_advance
def test_public_macro_calls_the_generator_that_exists():
    """The Mainsail-facing macro must call a macro defined in this file.

    Regression guard: it previously called _PRESSURE_ADVANCE_CALIBRATION,
    which is not defined anywhere, so the command failed at runtime.
    """
    source = open(MACRO_FILE, encoding='utf-8').read()
    defined = set(re.findall(r'\[gcode_macro ([^\]]+)\]', source))

    body = extract_macro_gcode(MACRO_FILE, PUBLIC_MACRO)
    called = set(re.findall(r'^\s*(_[A-Z_]+)\s', body, re.MULTILINE))

    assert called, "Public macro does not call any helper macro"
    missing = called - defined
    assert not missing, f"Public macro calls undefined macro(s): {sorted(missing)}"


@pytest.mark.pressure_advance
def test_setup_sequence_present():
    """Heat, home, and set the coordinate/extrusion modes before printing."""
    rendered = generate()
    for command in ['M140 S', 'M190 S', 'M104 S', 'M109 S', 'G28',
                    'G21', 'G90', 'M83', 'G92 E0']:
        assert command in rendered, f"Missing setup command {command}"


@pytest.mark.pressure_advance
def test_temperatures_follow_parameters():
    """Nozzle and bed temperatures come from parameters, not literals."""
    rendered = generate(NOZZLE_TEMP=245, BED_TEMP=105)
    assert 'M140 S105' in rendered and 'M190 S105' in rendered
    assert 'M104 S245' in rendered and 'M109 S245' in rendered


@pytest.mark.pressure_advance
def test_default_pa_ladder_is_complete_and_ordered():
    """Pattern N sets PA = PA_START_VALUE + N * PA_INCREMENT, ascending."""
    values = pa_values(generate())
    assert len(values) == DEFAULTS['PATTERN_COUNT']

    expected = [DEFAULTS['PA_START_VALUE'] + i * DEFAULTS['PA_INCREMENT']
                for i in range(DEFAULTS['PATTERN_COUNT'])]
    for index, (actual, want) in enumerate(zip(values, expected)):
        assert actual == pytest.approx(want, abs=1e-6), \
            f"Pattern {index + 1}: PA {actual}, expected {want}"

    assert values == sorted(values), "PA values must ascend across the pattern"


@pytest.mark.pressure_advance
@pytest.mark.parametrize('start,increment,count', [
    (0.0, 0.005, 17),     # defaults
    (0.01, 0.01, 6),      # coarse sweep
    (0.02, 0.002, 10),    # fine sweep around a known-good value
    (0.0, 0.05, 1),       # degenerate single pattern
])
def test_pa_ladder_follows_parameters(start, increment, count):
    """The ladder is computed from start/increment/count, not hardcoded."""
    values = pa_values(generate(PA_START_VALUE=start,
                                PA_INCREMENT=increment,
                                PATTERN_COUNT=count))
    assert len(values) == count
    for index, actual in enumerate(values):
        assert actual == pytest.approx(start + index * increment, abs=1e-6)


@pytest.mark.pressure_advance
def test_every_pattern_is_labelled_for_the_operator():
    """Each pattern announces its PA value so the print can be read back."""
    rendered = generate()
    labels = re.findall(r'M117 PA ([\d.]+)', rendered)
    assert len(labels) == DEFAULTS['PATTERN_COUNT']
    assert [float(v) for v in labels] == pa_values(rendered), \
        "M117 labels must match the PA values actually commanded"


@pytest.mark.pressure_advance
@pytest.mark.parametrize('perimeters', [1, 4, 6])
def test_anchor_frame_perimeter_count(perimeters):
    """ANCHOR_FRAME_PERIMETERS controls how many frame loops are drawn."""
    rendered = generate(ANCHOR_FRAME_PERIMETERS=perimeters)
    found = re.findall(r'; Perimeter (\d+)', rendered)
    assert len(found) == perimeters
    assert [int(v) for v in found] == list(range(1, perimeters + 1))


@pytest.mark.pressure_advance
@pytest.mark.parametrize('walls', [1, 3, 5])
def test_wall_count_per_pattern(walls):
    """WALL_COUNT walls are drawn inside each pattern."""
    rendered = generate(WALL_COUNT=walls, PATTERN_COUNT=2)
    found = re.findall(r'; Wall (\d+)', rendered)
    assert len(found) == walls * 2, \
        f"Expected {walls} walls in each of 2 patterns, found {len(found)}"


@pytest.mark.pressure_advance
def test_pattern_is_centred_on_the_bed():
    """The pattern is centred on the 350mm bed it is written for."""
    rendered = generate()
    start_x = (BED_SIZE - PATTERN_WIDTH) / 2
    start_y = (BED_SIZE - PATTERN_HEIGHT) / 2
    assert f'X{start_x}' in rendered, f"Expected pattern origin X{start_x}"
    assert f'Y{start_y}' in rendered, f"Expected pattern origin Y{start_y}"


@pytest.mark.pressure_advance
def test_shuts_down_cleanly():
    """Heaters and fan are turned off at the end."""
    rendered = generate()
    for command in ['M104 S0', 'M140 S0', 'M106 S0']:
        assert command in rendered, f"Missing shutdown command {command}"
    assert 'complete' in rendered.lower()


@pytest.mark.pressure_advance
def test_pa_end_value_is_currently_advisory():
    """PA_END_VALUE is accepted but does not bound the ladder.

    Documents a known sharp edge: the sweep length is PATTERN_COUNT, so
    raising PA_END_VALUE alone changes nothing. Kept as a test so that if the
    macro is later changed to derive the count, this fails and gets updated
    rather than silently diverging from the parameter's name.
    """
    values = pa_values(generate(PA_END_VALUE=0.02))
    assert len(values) == DEFAULTS['PATTERN_COUNT']
    assert max(values) > 0.02, \
        "PA_END_VALUE now appears to bound the ladder - update this test and the docs"
