"""Test suite for the _RETRACT_UNRETRACT macro.

Tests verify that the actual macro from retract_unretract.cfg
produces expected G-code output.
"""

import pytest
from utils.gcode_helpers import run_macro_comparison_test

# Path to the actual macro file (relative to testing directory)
MACRO_FILE = '../retraction_calibration/retract_unretract.cfg'
MACRO_NAME = '_RETRACT_UNRETRACT'

# Test data for retract/unretract macro
retract_unretract_test_data = {
    'expected_file': '../fixtures/expected_gcode/retraction_calibration/retract_unretract.gcode',
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


@pytest.mark.retraction_calibration
@pytest.mark.retract_unretract
def test_retract_unretract_macro(results_dir):
    """Test _RETRACT_UNRETRACT macro produces correct output."""
    diff_count = run_macro_comparison_test(
        results_dir,
        retract_unretract_test_data['expected_file'],
        MACRO_FILE,
        MACRO_NAME,
        retract_unretract_test_data['params'],
        'retract_unretract'
    )
    assert diff_count == 0, f"Retract/unretract macro test failed with {diff_count} differences"
