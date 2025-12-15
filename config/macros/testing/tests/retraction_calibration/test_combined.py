"""Test suite for the combined retraction_test macro functionality.

These tests verify that all component macros work correctly with the same
parameters used in their individual test files.
"""

import pytest
from utils.gcode_helpers import run_gcode_comparison_test

# Import test data from individual test files to ensure consistency
from tests.retraction_calibration.test_fill import fill_test_data
from tests.retraction_calibration.test_perimeter import first_layer_test_data as perimeter_test_data
from tests.retraction_calibration.test_retract_unretract import retract_unretract_test_data as retract_test_data


@pytest.mark.retraction
@pytest.mark.combined
def test_fill_component_working(results_dir):
    """Test that the fill component works with the same parameters as the fill test."""
    diff_count = run_gcode_comparison_test(
        results_dir,
        fill_test_data['orig_file'],
        fill_test_data['render_file'],
        fill_test_data['params'],
        'fill_component_test'
    )
    assert diff_count == 0, f"Fill component test failed with {diff_count} differences"


@pytest.mark.retraction
@pytest.mark.combined
def test_perimeter_component_working(results_dir):
    """Test that the perimeter component works with the same parameters as the perimeter test."""
    diff_count = run_gcode_comparison_test(
        results_dir,
        perimeter_test_data['orig_file'],
        perimeter_test_data['render_file'],
        perimeter_test_data['params'],
        'perimeter_component_test'
    )
    assert diff_count == 0, f"Perimeter component test failed with {diff_count} differences"


@pytest.mark.retraction
@pytest.mark.combined
def test_retract_unretract_component_working(results_dir):
    """Test that the retract_unretract component works with the same parameters as the retract test."""
    diff_count = run_gcode_comparison_test(
        results_dir,
        retract_test_data['orig_file'],
        retract_test_data['render_file'],
        retract_test_data['params'],
        'retract_unretract_component_test'
    )
    assert diff_count == 0, f"Retract_unretract component test failed with {diff_count} differences"
