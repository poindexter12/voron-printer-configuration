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

# Test data for digit 3 glyph macro
digit_3_test_data = {
    'name': 'digit_3_glyph',
    'orig_file': '../fixtures/expected_gcode/retraction_calibration/digit_3.gcode',
    'render_file': '../retraction_calibration/glyphs.cfg',
    'params': {
        'DIGIT': '3',
        'START_X': 155.5301,
        'START_Y': 200.8832,
        'WIDTH_EXTRUSION': 0.07174,
        'HEIGHT_EXTRUSION': 0.07174,
        'PRINT_SPEED': 1800
    }
}

# Test data for digit 4 glyph macro
digit_4_test_data = {
    'name': 'digit_4_glyph',
    'orig_file': '../fixtures/expected_gcode/retraction_calibration/digit_4.gcode',
    'render_file': '../retraction_calibration/glyphs.cfg',
    'params': {
        'DIGIT': '4',
        'START_X': 164.7329,
        'START_Y': 200.8832,
        'WIDTH_EXTRUSION': 0.07174,
        'HEIGHT_EXTRUSION': 0.07174,
        'PRINT_SPEED': 1800
    }
}

# Test data for digit 5 glyph macro
digit_5_test_data = {
    'name': 'digit_5_glyph',
    'orig_file': '../fixtures/expected_gcode/retraction_calibration/digit_5.gcode',
    'render_file': '../retraction_calibration/glyphs.cfg',
    'params': {
        'DIGIT': '5',
        'START_X': 169.9357,
        'START_Y': 198.8832,
        'WIDTH_EXTRUSION': 0.07174,
        'HEIGHT_EXTRUSION': 0.07174,
        'PRINT_SPEED': 1800
    }
}

# Test data for digit 6 glyph macro
digit_6_test_data = {
    'name': 'digit_6_glyph',
    'orig_file': '../fixtures/expected_gcode/retraction_calibration/digit_6.gcode',
    'render_file': '../retraction_calibration/glyphs.cfg',
    'params': {
        'DIGIT': '6',
        'START_X': 177.1384,
        'START_Y': 198.8832,
        'WIDTH_EXTRUSION': 0.07174,
        'HEIGHT_EXTRUSION': 0.07174,
        'PRINT_SPEED': 1800
    }
}

# Test data for digit 7 glyph macro
digit_7_test_data = {
    'name': 'digit_7_glyph',
    'orig_file': '../fixtures/expected_gcode/retraction_calibration/digit_7.gcode',
    'render_file': '../retraction_calibration/glyphs.cfg',
    'params': {
        'DIGIT': '7',
        'START_X': 184.3412,
        'START_Y': 200.8832,
        'WIDTH_EXTRUSION': 0.07174,
        'HEIGHT_EXTRUSION': 0.07174,
        'PRINT_SPEED': 1800
    }
}

# Test data for digit 8 glyph macro
digit_8_test_data = {
    'name': 'digit_8_glyph',
    'orig_file': '../fixtures/expected_gcode/retraction_calibration/digit_8.gcode',
    'render_file': '../retraction_calibration/glyphs.cfg',
    'params': {
        'DIGIT': '8',
        'START_X': 193.544,
        'START_Y': 198.8832,
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

@pytest.mark.retraction_calibration
@pytest.mark.glyphs
def test_digit_3_glyph(results_dir):
    """Test the digit 3 glyph macro against expected output."""
    diff_count = run_gcode_comparison_test(
        results_dir,
        digit_3_test_data['orig_file'],
        digit_3_test_data['render_file'],
        digit_3_test_data['params'],
        digit_3_test_data['name']
    )

    assert diff_count == 0, f"Digit 3 glyph test failed with {diff_count} differences"

@pytest.mark.retraction_calibration
@pytest.mark.glyphs
def test_digit_4_glyph(results_dir):
    """Test the digit 4 glyph macro against expected output."""
    diff_count = run_gcode_comparison_test(
        results_dir,
        digit_4_test_data['orig_file'],
        digit_4_test_data['render_file'],
        digit_4_test_data['params'],
        digit_4_test_data['name']
    )

    assert diff_count == 0, f"Digit 4 glyph test failed with {diff_count} differences"

@pytest.mark.retraction_calibration
@pytest.mark.glyphs
def test_digit_5_glyph(results_dir):
    """Test the digit 5 glyph macro against expected output."""
    diff_count = run_gcode_comparison_test(
        results_dir,
        digit_5_test_data['orig_file'],
        digit_5_test_data['render_file'],
        digit_5_test_data['params'],
        digit_5_test_data['name']
    )

    assert diff_count == 0, f"Digit 5 glyph test failed with {diff_count} differences"

@pytest.mark.retraction_calibration
@pytest.mark.glyphs
def test_digit_6_glyph(results_dir):
    """Test the digit 6 glyph macro against expected output."""
    diff_count = run_gcode_comparison_test(
        results_dir,
        digit_6_test_data['orig_file'],
        digit_6_test_data['render_file'],
        digit_6_test_data['params'],
        digit_6_test_data['name']
    )

    assert diff_count == 0, f"Digit 6 glyph test failed with {diff_count} differences"

@pytest.mark.retraction_calibration
@pytest.mark.glyphs
def test_digit_7_glyph(results_dir):
    """Test the digit 7 glyph macro against expected output."""
    diff_count = run_gcode_comparison_test(
        results_dir,
        digit_7_test_data['orig_file'],
        digit_7_test_data['render_file'],
        digit_7_test_data['params'],
        digit_7_test_data['name']
    )

    assert diff_count == 0, f"Digit 7 glyph test failed with {diff_count} differences"

@pytest.mark.retraction_calibration
@pytest.mark.glyphs
def test_digit_8_glyph(results_dir):
    """Test the digit 8 glyph macro against expected output."""
    diff_count = run_gcode_comparison_test(
        results_dir,
        digit_8_test_data['orig_file'],
        digit_8_test_data['render_file'],
        digit_8_test_data['params'],
        digit_8_test_data['name']
    )

    assert diff_count == 0, f"Digit 8 glyph test failed with {diff_count} differences"
