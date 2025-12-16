"""Test suite for the _PRESSURE_ADVANCE_LOOP macro.

Tests verify that the actual macro from outer_loop.cfg
produces expected G-code output.
"""

import pytest
from utils.gcode_helpers import run_macro_comparison_test

# Path to the actual macro file (relative to testing directory)
MACRO_FILE = '../retraction_calibration/outer_loop.cfg'
MACRO_NAME = '_PRESSURE_ADVANCE_LOOP'

# Test data for outer loop macro - parameters extracted from original.gcode
outer_loop_test_data = {
    'expected_file': '../fixtures/expected_gcode/retraction_calibration/outer_loop_basic.gcode',
    'params': {
        'START_ADVANCE': 0.0,
        'END_ADVANCE': 0.08,
        'INCREMENT': 0.005,
        'START_X': 137.2384,
        'START_Y': 149.8992,
        'Y_START': 188.5408,
        'Y_END': 169.22,
        'E_INCREMENT': 1.19281,
        'X_WALL_OFFSET': 19.3208,
        'STEP_DISTANCE': 0.5757,
        'GROUP_SPACING': 1.8743,
        'PRINT_SPEED': 1800,
        'TRAVEL_SPEED': 7200,
        'Z_HOP_DISTANCE': 0.35,
        'Z_HOP_RETURN': 0.25,
        'RETRACT_SPEED': 2100,
        'UNRETRACT_SPEED': 2100,
        'RETRACT_DISTANCE': 0.5
    }
}


@pytest.mark.retraction_calibration
@pytest.mark.outer_loop
def test_basic_pressure_advance_loop(results_dir):
    """Test _PRESSURE_ADVANCE_LOOP macro produces correct output."""
    diff_count = run_macro_comparison_test(
        results_dir,
        outer_loop_test_data['expected_file'],
        MACRO_FILE,
        MACRO_NAME,
        outer_loop_test_data['params'],
        'outer_loop_basic'
    )
    assert diff_count == 0, f"Outer loop macro test failed with {diff_count} differences"
