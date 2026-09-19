"""Test suite for the TOWER_LAYER macro.

These tests validate that the tower layer macro correctly handles
temperature changes at section boundaries (layers 57, 107, 157, 207).
"""

import pytest
from utils.gcode_helpers import render_macro_gcode, clean_gcode_string

# Path to the actual macro file (relative to testing directory)
MACRO_FILE = '../temperature_test/tower_layer.cfg'
MACRO_NAME = 'TOWER_LAYER'

# Standard parameters for testing
tower_layer_params = {
    'HOTEND_TEMPERATURE': 215,
    'Z_HOP': 0.5,
    'Z_START': 1.120,
    'Z_DELTA': 0.16,
    'OFFSET_2': -5,
    'OFFSET_3': -10,
    'OFFSET_4': -15,
    'OFFSET_5': -20,
}


@pytest.mark.temperature_tower
def test_tower_layer_renders(results_dir):
    """Test that the tower layer macro renders without error."""
    rendered = render_macro_gcode(MACRO_FILE, MACRO_NAME, tower_layer_params)
    assert rendered is not None
    assert len(rendered) > 0

    # Save rendered output for inspection
    import os
    output_path = os.path.join(results_dir, 'tower_layer_rendered.gcode')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(rendered)


@pytest.mark.temperature_tower
def test_tower_layer_has_section_a_temp():
    """Test that section A starts with correct temperature (M109 wait)."""
    rendered = render_macro_gcode(MACRO_FILE, MACRO_NAME, tower_layer_params)

    # Section A temperature is the hotend_temp (215)
    assert 'M109 S215' in rendered or 'M109 S 215' in rendered, \
        "Missing Section A temperature M109 S215"


@pytest.mark.temperature_tower
def test_tower_layer_has_section_b_temp():
    """Test that section B has correct temperature change (210°C)."""
    rendered = render_macro_gcode(MACRO_FILE, MACRO_NAME, tower_layer_params)

    # Section B: hotend_temp + offset_2 = 215 + (-5) = 210
    assert 'M104 S210' in rendered or 'M104 S 210' in rendered, \
        "Missing Section B temperature M104 S210"


@pytest.mark.temperature_tower
def test_tower_layer_has_section_c_temp():
    """Test that section C has correct temperature change (205°C)."""
    rendered = render_macro_gcode(MACRO_FILE, MACRO_NAME, tower_layer_params)

    # Section C: hotend_temp + offset_3 = 215 + (-10) = 205
    assert 'M104 S205' in rendered or 'M104 S 205' in rendered, \
        "Missing Section C temperature M104 S205"


@pytest.mark.temperature_tower
def test_tower_layer_has_section_d_temp():
    """Test that section D has correct temperature change (200°C)."""
    rendered = render_macro_gcode(MACRO_FILE, MACRO_NAME, tower_layer_params)

    # Section D: hotend_temp + offset_4 = 215 + (-15) = 200
    assert 'M104 S200' in rendered or 'M104 S 200' in rendered, \
        "Missing Section D temperature M104 S200"


@pytest.mark.temperature_tower
def test_tower_layer_has_section_e_temp():
    """Test that section E has correct temperature change (195°C)."""
    rendered = render_macro_gcode(MACRO_FILE, MACRO_NAME, tower_layer_params)

    # Section E: hotend_temp + offset_5 = 215 + (-20) = 195
    assert 'M104 S195' in rendered or 'M104 S 195' in rendered, \
        "Missing Section E temperature M104 S195"


@pytest.mark.temperature_tower
def test_tower_layer_line_count():
    """Test that the macro produces expected number of G-code lines.

    TOWER_LAYER contains layers 8-255 (~21000 lines of raw G-code).
    """
    rendered = render_macro_gcode(MACRO_FILE, MACRO_NAME, tower_layer_params)
    cleaned = clean_gcode_string(rendered)

    # Full tower should have ~20000+ lines
    line_count = len(cleaned)
    assert line_count > 18000, f"Too few lines: {line_count} (expected >18000)"
    assert line_count < 25000, f"Too many lines: {line_count} (expected <25000)"


@pytest.mark.temperature_tower
def test_tower_layer_has_layer_markers():
    """Test that the macro has layer change markers."""
    rendered = render_macro_gcode(MACRO_FILE, MACRO_NAME, tower_layer_params)

    # Check for layer markers at section boundaries
    assert ';layer 57' in rendered, "Missing layer 57 marker (Section B start)"
    assert ';layer 107' in rendered, "Missing layer 107 marker (Section C start)"
    assert ';layer 157' in rendered, "Missing layer 157 marker (Section D start)"
    assert ';layer 207' in rendered, "Missing layer 207 marker (Section E start)"


@pytest.mark.temperature_tower
def test_tower_layer_ends_with_retraction():
    """Test that the macro ends with a retraction command."""
    rendered = render_macro_gcode(MACRO_FILE, MACRO_NAME, tower_layer_params)

    # Should end with retraction (not shutdown commands - those are in main macro)
    lines = rendered.strip().split('\n')
    # Find last non-empty line
    last_line = None
    for line in reversed(lines):
        stripped = line.strip()
        if stripped:
            last_line = stripped
            break

    assert last_line is not None, "No content in rendered output"
    assert 'E-' in last_line or 'retraction' in last_line.lower(), \
        f"Expected retraction at end, got: {last_line}"
