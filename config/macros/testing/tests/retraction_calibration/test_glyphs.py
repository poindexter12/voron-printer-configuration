"""Test suite for the glyph drawing macros in glyphs.cfg.

These tests verify that the actual _DRAW_DIGIT and _DRAW_PERIOD macros
produce the expected G-code output matching the original.gcode patterns.
"""

import pytest
from utils.gcode_helpers import run_macro_comparison_test

# Path to the actual macro file (relative to testing directory)
MACRO_FILE = '../retraction_calibration/glyphs.cfg'

# Common values used for all glyphs
GLYPH_EXTRUSION = 0.07174
PERIOD_EXTRUSION = 0.0269
PRINT_SPEED = 1800
TRAVEL_SPEED = 7200


# Test data for each digit macro
# START_X and START_Y are chosen to produce output matching expected gcode files
digit_test_data = {
    '0': {
        'expected_file': '../fixtures/expected_gcode/retraction_calibration/digit_0.gcode',
        'params': {
            'DIGIT': '0',
            'START_X': 133.9217,
            'START_Y': 191.8832,
            'EXTRUSION': GLYPH_EXTRUSION,
            'PRINT_SPEED': PRINT_SPEED,
            'TRAVEL_SPEED': TRAVEL_SPEED
        }
    },
    '1': {
        'expected_file': '../fixtures/expected_gcode/retraction_calibration/digit_1.gcode',
        'params': {
            'DIGIT': '1',
            'START_X': 141.1245,
            'START_Y': 198.8832,
            'EXTRUSION': GLYPH_EXTRUSION,
            'PRINT_SPEED': PRINT_SPEED,
            'TRAVEL_SPEED': TRAVEL_SPEED
        }
    },
    '2': {
        'expected_file': '../fixtures/expected_gcode/retraction_calibration/digit_2.gcode',
        'params': {
            'DIGIT': '2',
            'START_X': 148.3273,
            'START_Y': 198.8832,
            'EXTRUSION': GLYPH_EXTRUSION,
            'PRINT_SPEED': PRINT_SPEED,
            'TRAVEL_SPEED': TRAVEL_SPEED
        }
    },
    '3': {
        'expected_file': '../fixtures/expected_gcode/retraction_calibration/digit_3.gcode',
        'params': {
            'DIGIT': '3',
            'START_X': 155.5301,
            'START_Y': 198.8832,
            'EXTRUSION': GLYPH_EXTRUSION,
            'PRINT_SPEED': PRINT_SPEED,
            'TRAVEL_SPEED': TRAVEL_SPEED
        }
    },
    '4': {
        'expected_file': '../fixtures/expected_gcode/retraction_calibration/digit_4.gcode',
        'params': {
            'DIGIT': '4',
            'START_X': 162.7329,
            'START_Y': 198.8832,
            'EXTRUSION': GLYPH_EXTRUSION,
            'PRINT_SPEED': PRINT_SPEED,
            'TRAVEL_SPEED': TRAVEL_SPEED
        }
    },
    '5': {
        'expected_file': '../fixtures/expected_gcode/retraction_calibration/digit_5.gcode',
        'params': {
            'DIGIT': '5',
            'START_X': 169.9357,
            'START_Y': 200.8832,  # Note: digit 5 uses y-2 pattern, so START_Y is upper position
            'EXTRUSION': GLYPH_EXTRUSION,
            'PRINT_SPEED': PRINT_SPEED,
            'TRAVEL_SPEED': TRAVEL_SPEED
        }
    },
    '6': {
        'expected_file': '../fixtures/expected_gcode/retraction_calibration/digit_6.gcode',
        'params': {
            'DIGIT': '6',
            'START_X': 177.1384,
            'START_Y': 200.8832,  # Note: digit 6 uses y-2 pattern
            'EXTRUSION': GLYPH_EXTRUSION,
            'PRINT_SPEED': PRINT_SPEED,
            'TRAVEL_SPEED': TRAVEL_SPEED
        }
    },
    '7': {
        'expected_file': '../fixtures/expected_gcode/retraction_calibration/digit_7.gcode',
        'params': {
            'DIGIT': '7',
            'START_X': 184.3412,
            'START_Y': 198.8832,
            'EXTRUSION': GLYPH_EXTRUSION,
            'PRINT_SPEED': PRINT_SPEED,
            'TRAVEL_SPEED': TRAVEL_SPEED
        }
    },
    '8': {
        'expected_file': '../fixtures/expected_gcode/retraction_calibration/digit_8.gcode',
        'params': {
            'DIGIT': '8',
            'START_X': 191.544,
            'START_Y': 198.8832,
            'EXTRUSION': GLYPH_EXTRUSION,
            'PRINT_SPEED': PRINT_SPEED,
            'TRAVEL_SPEED': TRAVEL_SPEED
        }
    },
}

period_test_data = {
    'expected_file': '../fixtures/expected_gcode/retraction_calibration/period.gcode',
    'params': {
        'START_X': 145.1245,
        'START_Y': 194.8832,
        'EXTRUSION': PERIOD_EXTRUSION,
        'PRINT_SPEED': PRINT_SPEED
    }
}


@pytest.mark.retraction_calibration
@pytest.mark.glyphs
@pytest.mark.parametrize("digit", ['0', '1', '2', '3', '4', '5', '6', '7', '8'])
def test_draw_digit_macro(results_dir, digit):
    """Test _DRAW_DIGIT macro produces correct output for each digit."""
    data = digit_test_data[digit]
    diff_count = run_macro_comparison_test(
        results_dir,
        data['expected_file'],
        MACRO_FILE,
        '_DRAW_DIGIT',
        data['params'],
        f'digit_{digit}_macro'
    )
    assert diff_count == 0, f"_DRAW_DIGIT macro for digit {digit} failed with {diff_count} differences"


@pytest.mark.retraction_calibration
@pytest.mark.glyphs
def test_draw_period_macro(results_dir):
    """Test _DRAW_PERIOD macro produces correct output."""
    diff_count = run_macro_comparison_test(
        results_dir,
        period_test_data['expected_file'],
        MACRO_FILE,
        '_DRAW_PERIOD',
        period_test_data['params'],
        'period_macro'
    )
    assert diff_count == 0, f"_DRAW_PERIOD macro failed with {diff_count} differences"
