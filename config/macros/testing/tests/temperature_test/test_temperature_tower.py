"""Test suite for the TEMPERATURE_TOWER macro.

These tests validate the temperature tower macro produces expected output
and contains the correct temperature change commands.
"""

import pytest
import re
from utils.gcode_helpers import render_macro_gcode, clean_gcode_string

# Path to the actual macro file (relative to testing directory)
MACRO_FILE = '../temperature_test/temperature_tower.cfg'
MACRO_NAME = 'TEMPERATURE_TOWER'

# Parameters that match the original.old reference output
# Original has: bed=75, hotend=215, starting=165
temperature_tower_params = {
    'HOTEND_TEMPERATURE': 215,
    'BED_TEMPERATURE': 75,
    'LAYERS': 5,
    'OFFSET_1': 0,
    'OFFSET_2': -5,
    'OFFSET_3': -10,
    'OFFSET_4': -15,
    'OFFSET_5': -20,
}


@pytest.mark.temperature_tower
def test_temperature_tower_renders(results_dir):
    """Test that the temperature tower macro renders without error."""
    rendered = render_macro_gcode(MACRO_FILE, MACRO_NAME, temperature_tower_params)
    assert rendered is not None
    assert len(rendered) > 0

    # Save rendered output for inspection
    import os
    output_path = os.path.join(results_dir, 'temperature_tower_rendered.gcode')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(rendered)


@pytest.mark.temperature_tower
def test_temperature_tower_has_bed_temp(results_dir):
    """Test that the macro sets correct bed temperature."""
    rendered = render_macro_gcode(MACRO_FILE, MACRO_NAME, temperature_tower_params)

    # Should have M140 S75 and M190 S75
    assert 'M140 S75' in rendered, "Missing bed temp set command M140 S75"
    assert 'M190 S75' in rendered, "Missing bed temp wait command M190 S75"


@pytest.mark.temperature_tower
def test_temperature_tower_has_starting_temp():
    """Test that the macro sets correct starting temperature (hotend - 50)."""
    rendered = render_macro_gcode(MACRO_FILE, MACRO_NAME, temperature_tower_params)

    # Starting temp should be 215 - 50 = 165
    assert 'M104 S165' in rendered, "Missing starting temp command M104 S165"


@pytest.mark.temperature_tower
def test_temperature_tower_has_base_layer_temp():
    """Test that the macro sets correct base layer temperature."""
    rendered = render_macro_gcode(MACRO_FILE, MACRO_NAME, temperature_tower_params)

    # Base layer temp with offset[1]=0 should be 215
    assert 'M109 S215' in rendered or 'M109 S 215' in rendered, \
        "Missing base layer temp command M109 S215"


@pytest.mark.temperature_tower
def test_temperature_tower_calls_tower_layer():
    """Test that the macro calls TOWER_LAYER for the main print."""
    rendered = render_macro_gcode(MACRO_FILE, MACRO_NAME, temperature_tower_params)

    # The TEMPERATURE_TOWER macro sets up then calls TOWER_LAYER
    assert 'TOWER_LAYER' in rendered, "Missing TOWER_LAYER call"
    assert 'HOTEND_TEMPERATURE=' in rendered, "Missing HOTEND_TEMPERATURE parameter in TOWER_LAYER call"


@pytest.mark.temperature_tower
def test_temperature_tower_has_homing():
    """Test that the macro includes homing and leveling commands."""
    rendered = render_macro_gcode(MACRO_FILE, MACRO_NAME, temperature_tower_params)

    assert 'G28' in rendered, "Missing homing command G28"
    assert 'QUAD_GANTRY_LEVEL' in rendered, "Missing QGL command"
    assert 'BED_MESH_CALIBRATE' in rendered, "Missing bed mesh command"


@pytest.mark.temperature_tower
def test_temperature_tower_line_count():
    """Test that the macro produces expected number of G-code lines.

    Note: TEMPERATURE_TOWER only prints the first 7 layers (~1500 lines),
    then calls TOWER_LAYER for the rest of the print.
    """
    rendered = render_macro_gcode(MACRO_FILE, MACRO_NAME, temperature_tower_params)
    cleaned = clean_gcode_string(rendered)

    # The setup macro has ~1500 lines (first 7 layers + setup)
    line_count = len(cleaned)
    assert line_count > 1000, f"Too few lines: {line_count} (expected >1000)"
    assert line_count < 3000, f"Too many lines: {line_count} (expected <3000)"


@pytest.mark.temperature_tower
def test_temperature_tower_ends_correctly():
    """Test that the macro ends with proper shutdown commands."""
    rendered = render_macro_gcode(MACRO_FILE, MACRO_NAME, temperature_tower_params)

    # Should turn off hotend at end
    assert 'M104 S0' in rendered, "Missing hotend off command M104 S0"
