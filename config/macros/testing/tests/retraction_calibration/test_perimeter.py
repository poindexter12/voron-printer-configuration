"""Test suite for the _DRAW_PERIMETER_LAYER macro.

Tests verify that the actual macro from draw_perimeter_layer.cfg
produces expected G-code output.
"""

import pytest
from utils.gcode_helpers import run_macro_comparison_test

# Path to the actual macro file (relative to testing directory)
MACRO_FILE = '../retraction_calibration/draw_perimeter_layer.cfg'
MACRO_NAME = '_DRAW_PERIMETER_LAYER'

# Test data for different layer types
first_layer_test_data = {
    'expected_file': '../fixtures/expected_gcode/retraction_calibration/perimeter_first_layer.gcode',
    'params': {
        'START_X': 132.6417,
        'START_Y': 148.0068,
        'WIDTH': 84.7166,
        'HEIGHT': 42.4264,
        'LINE_WIDTH': 0.56,
        'LAYER_HEIGHT': 0.25,
        'NUM_PERIMETERS': 4,
        'STEP_DISTANCE': 0.5063495408493621,
        'PRINT_SPEED': 1800,
        'TRAVEL_SPEED': 7200,
        'FILAMENT_DIAMETER': 1.7,
        'EXTRUSION_MULTIPLIER': 1.0
    }
}

other_layers_test_data = {
    'expected_file': '../fixtures/expected_gcode/retraction_calibration/perimeter_other_layers.gcode',
    'params': {
        'START_X': 132.6417,
        'START_Y': 190.9396,
        'WIDTH': 64.2545,
        'HEIGHT': 11.5063,
        'LINE_WIDTH': 0.56,
        'LAYER_HEIGHT': 0.25,
        'NUM_PERIMETERS': 4,
        'STEP_DISTANCE': 0.5063495408493621,
        'PRINT_SPEED': 1800,
        'TRAVEL_SPEED': 7200,
        'FILAMENT_DIAMETER': 1.7,
        'EXTRUSION_MULTIPLIER': 1.0
    }
}


@pytest.mark.retraction_calibration
@pytest.mark.perimeter
def test_first_layer_perimeter(results_dir):
    """Test _DRAW_PERIMETER_LAYER macro for first layer."""
    diff_count = run_macro_comparison_test(
        results_dir,
        first_layer_test_data['expected_file'],
        MACRO_FILE,
        MACRO_NAME,
        first_layer_test_data['params'],
        'perimeter_first_layer'
    )
    assert diff_count == 0, f"First layer perimeter test failed with {diff_count} differences"


@pytest.mark.retraction_calibration
@pytest.mark.perimeter
def test_other_layers_perimeter(results_dir):
    """Test _DRAW_PERIMETER_LAYER macro for other layers."""
    diff_count = run_macro_comparison_test(
        results_dir,
        other_layers_test_data['expected_file'],
        MACRO_FILE,
        MACRO_NAME,
        other_layers_test_data['params'],
        'perimeter_other_layers'
    )
    assert diff_count == 0, f"Other layers perimeter test failed with {diff_count} differences"
