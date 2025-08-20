"""Test suite for the _RETRACT_UNRETRACT macro functionality."""

import pytest

from utils.gcode_helpers import run_gcode_comparison_test

# Test data for retract/unretract macro
retract_unretract_test_data = {
    'name': 'retract_unretract',
    'orig_file': '../fixtures/expected_gcode/retract_unretract.gcode',
    'render_file': '../retraction_test/retract_unretract.cfg',
    'params': {
        'Z_HOP_DISTANCE': 0.35,
        'Z_HOP_RETURN': 0.25,
        'TRAVEL_SPEED': 7200,
        'RETRACT_SPEED': 2100,
        'UNRETRACT_SPEED': 2100,
        'RETRACT_DISTANCE': 0.5,
        'MOVE_X': 132.6417,
        'MOVE_Y': 190.9396
    }
}

@pytest.mark.retraction
@pytest.mark.retract_unretract
def test_retract_unretract_macro(results_dir):
    """Test the _RETRACT_UNRETRACT macro against expected output."""
    diff_count = run_gcode_comparison_test(
        results_dir,
        retract_unretract_test_data['orig_file'],
        retract_unretract_test_data['render_file'],
        retract_unretract_test_data['params'],
        retract_unretract_test_data['name']
    )
    
    assert diff_count == 0, f"Retract/unretract macro test failed with {diff_count} differences"
