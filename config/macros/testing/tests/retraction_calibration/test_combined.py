"""Test suite for combined component integration.

These tests verify that all component macros work correctly with
parameters used in their individual test files. Uses the same
run_macro_comparison_test method as individual tests.
"""

import pytest
from utils.gcode_helpers import run_macro_comparison_test

# Import test data and macro info from individual test files
from tests.retraction_calibration.test_fill import (
    fill_test_data, MACRO_FILE as FILL_MACRO_FILE, MACRO_NAME as FILL_MACRO_NAME
)
from tests.retraction_calibration.test_perimeter import (
    first_layer_test_data as perimeter_test_data,
    MACRO_FILE as PERIMETER_MACRO_FILE, MACRO_NAME as PERIMETER_MACRO_NAME
)
from tests.retraction_calibration.test_retract_unretract import (
    retract_unretract_test_data as retract_test_data,
    MACRO_FILE as RETRACT_MACRO_FILE, MACRO_NAME as RETRACT_MACRO_NAME
)


@pytest.mark.retraction_calibration
@pytest.mark.combined
def test_fill_component_working(results_dir):
    """Test _FILL macro with parameters from fill test."""
    diff_count = run_macro_comparison_test(
        results_dir,
        fill_test_data['expected_file'],
        FILL_MACRO_FILE,
        FILL_MACRO_NAME,
        fill_test_data['params'],
        'fill_component_test'
    )
    assert diff_count == 0, f"Fill component test failed with {diff_count} differences"


@pytest.mark.retraction_calibration
@pytest.mark.combined
def test_perimeter_component_working(results_dir):
    """Test _DRAW_PERIMETER_LAYER macro with parameters from perimeter test."""
    diff_count = run_macro_comparison_test(
        results_dir,
        perimeter_test_data['expected_file'],
        PERIMETER_MACRO_FILE,
        PERIMETER_MACRO_NAME,
        perimeter_test_data['params'],
        'perimeter_component_test'
    )
    assert diff_count == 0, f"Perimeter component test failed with {diff_count} differences"


@pytest.mark.retraction_calibration
@pytest.mark.combined
def test_retract_unretract_component_working(results_dir):
    """Test _RETRACT_UNRETRACT macro with parameters from retract test."""
    diff_count = run_macro_comparison_test(
        results_dir,
        retract_test_data['expected_file'],
        RETRACT_MACRO_FILE,
        RETRACT_MACRO_NAME,
        retract_test_data['params'],
        'retract_unretract_component_test'
    )
    assert diff_count == 0, f"Retract_unretract component test failed with {diff_count} differences"
