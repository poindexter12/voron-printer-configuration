"""Test suite for the _PRESSURE_ADVANCE_LOOP macro functionality."""

import pytest

from utils.gcode_helpers import run_gcode_comparison_test

# Test data for outer loop macro
outer_loop_test_data = {
    'name': 'outer_loop_basic',
    'orig_file': '../fixtures/expected_gcode/outer_loop_basic.gcode',
    'render_file': '../retraction_test/outer_loop.cfg',
    'params': {
        'START_ADVANCE': 0.0,
        'END_ADVANCE': 0.01,
        'INCREMENT': 0.005,
        'START_X': 138.3898,
        'START_Y': 149.8992,
        'STEP_DISTANCE': 0.5757,
        'GROUP_SPACING': 2.5853,
        'PRINT_SPEED': 1800,
        'TRAVEL_SPEED': 7200,
        'Z_HOP_DISTANCE': 0.35,
        'Z_HOP_RETURN': 0.25,
        'RETRACT_SPEED': 2100,
        'UNRETRACT_SPEED': 2100,
        'RETRACT_DISTANCE': 0.5
    }
}

@pytest.mark.retraction
@pytest.mark.outer_loop
def test_basic_pressure_advance_loop(results_dir):
    """Test basic pressure advance loop with minimal values."""
    diff_count = run_gcode_comparison_test(
        results_dir,
        outer_loop_test_data['orig_file'],
        outer_loop_test_data['render_file'],
        outer_loop_test_data['params'],
        outer_loop_test_data['name']
    )
    
    assert diff_count == 0, f"Outer loop macro test failed with {diff_count} differences"

if __name__ == '__main__':
    pytest.main([__file__])
