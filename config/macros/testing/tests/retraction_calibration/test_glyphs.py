"""Test suite for the glyph drawing macros functionality."""

import pytest
from utils.gcode_helpers import run_gcode_comparison_test

# Test data for period glyph macro
period_test_data = {
    'name': 'period_glyph',
    'orig_file': '../fixtures/expected_gcode/retraction_calibration/period.gcode',
    'render_file': '../retraction_calibration/glyphs.cfg',
    'params': {
        'DIGIT': '.',
        'START_X': 144.3745,
        'START_Y': 194.8832,
        'WIDTH_EXTRUSION': 0.07174,
        'HEIGHT_EXTRUSION': 0.07174,
        'PRINT_SPEED': 1800
    }
}

@pytest.mark.retraction_calibration
@pytest.mark.glyphs
def test_period_glyph(results_dir):
    """Test the period glyph macro against expected output."""
    diff_count = run_gcode_comparison_test(
        results_dir,
        period_test_data['orig_file'],
        period_test_data['render_file'],
        period_test_data['params'],
        period_test_data['name']
    )
    
    assert diff_count == 0, f"Period glyph test failed with {diff_count} differences"
