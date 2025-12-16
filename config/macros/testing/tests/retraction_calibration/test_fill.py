"""Test suite for the _FILL macro.

Tests verify that the actual macro from fill.cfg
produces expected G-code output.
"""

import pytest
from utils.gcode_helpers import run_macro_comparison_test

# Path to the actual macro file (relative to testing directory)
MACRO_FILE = '../retraction_calibration/fill.cfg'
MACRO_NAME = '_FILL'

# Test data for fill macro - diagonal fill pattern
fill_test_data = {
    'expected_file': '../fixtures/expected_gcode/retraction_calibration/fill.gcode',
    'params': {
        'MIN_X': 134.5341,
        'MAX_X': 195.0038,
        'MIN_Y': 192.8319,
        'MAX_Y': 200.5535,
        'STEP_SIZE': 0.7161,
        'PRINT_SPEED': 1800,
        'TRAVEL_SPEED': 7200,
        'EXTRUSION_PER_MM': 0.05577
    }
}


@pytest.mark.retraction_calibration
@pytest.mark.fill
def test_fill_macro(results_dir):
    """Test _FILL macro produces correct diagonal fill pattern."""
    diff_count = run_macro_comparison_test(
        results_dir,
        fill_test_data['expected_file'],
        MACRO_FILE,
        MACRO_NAME,
        fill_test_data['params'],
        'fill_macro'
    )
    assert diff_count == 0, f"Fill macro test failed with {diff_count} differences"
