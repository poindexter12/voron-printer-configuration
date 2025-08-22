"""Test suite for the fill macro functionality."""

import pytest
from utils.gcode_helpers import run_gcode_comparison_test

# Test data for fill macro
fill_test_data = {
    'name': 'fill_macro',
    'orig_file': '../fixtures/expected_gcode/retraction_calibration/fill.gcode',
    'render_file': '../retraction_calibration/fill.cfg',
    'params': {
        'START_X': 161.9007,
        'END_X': 195.0038,
        'Y1': 192.8319,
        'Y2': 200.5535,
        'STEP_SIZE': 0.7166,
        'PRINT_SPEED': 1800,
        'TRAVEL_SPEED': 7200,
        'EXTRUSION_MULTIPLIER': 0.85
    }
}

@pytest.mark.retraction
@pytest.mark.fill
def test_fill_macro(results_dir):
    """Test the fill macro against expected output."""
    diff_count = run_gcode_comparison_test(
        results_dir,
        fill_test_data['orig_file'],
        fill_test_data['render_file'],
        fill_test_data['params'],
        fill_test_data['name']
    )
    
    assert diff_count == 0, f"Fill macro test failed with {diff_count} differences"
