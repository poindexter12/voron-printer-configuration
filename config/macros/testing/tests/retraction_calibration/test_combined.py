"""Test suite for the combined retraction_test macro functionality."""

import pytest
from utils.gcode_helpers import run_gcode_comparison_test

# Test data for testing individual components together
# We'll test the fill component as a representative example
fill_test_data = {
    'name': 'fill_component_test',
    'orig_file': '../fixtures/expected_gcode/retraction_calibration/fill.gcode',
    'render_file': '../retraction_calibration/fill.cfg',
    'params': {
        'START_X': 10.0,
        'END_X': 30.0,
        'Y1': 10.0,
        'Y2': 30.0,
        'STEP_SIZE': 2.0,
        'PRINT_SPEED': 60.0,
        'TRAVEL_SPEED': 120.0,
        'EXTRUSION_MULTIPLIER': 1.0
    }
}

@pytest.mark.retraction
@pytest.mark.combined
def test_fill_component_working(results_dir):
    """Test that the fill component works with the same parameters as other tests."""
    diff_count = run_gcode_comparison_test(
        results_dir,
        fill_test_data['orig_file'],
        fill_test_data['render_file'],
        fill_test_data['params'],
        fill_test_data['name']
    )
    
    assert diff_count == 0, f"Fill component test failed with {diff_count} differences"

# Test data for testing perimeter component
perimeter_test_data = {
    'name': 'perimeter_component_test',
    'orig_file': '../fixtures/expected_gcode/retraction_calibration/perimeter_first_layer.gcode',
    'render_file': '../retraction_calibration/draw_perimeter_layer.cfg',
    'params': {
        'START_X': 10.0,
        'START_Y': 10.0,
        'WIDTH': 20.0,
        'HEIGHT': 20.0,
        'LINE_WIDTH': 0.4,
        'LAYER_HEIGHT': 0.2,
        'NUM_PERIMETERS': 3,
        'STEP_DISTANCE': 2.0,
        'PRINT_SPEED': 60.0,
        'TRAVEL_SPEED': 120.0,
        'FILAMENT_DIAMETER': 1.75,
        'EXTRUSION_MULTIPLIER': 1.0
    }
}

@pytest.mark.retraction
@pytest.mark.combined
def test_perimeter_component_working(results_dir):
    """Test that the perimeter component works with the same parameters as other tests."""
    diff_count = run_gcode_comparison_test(
        results_dir,
        perimeter_test_data['orig_file'],
        perimeter_test_data['render_file'],
        perimeter_test_data['params'],
        perimeter_test_data['name']
    )
    
    assert diff_count == 0, f"Perimeter component test failed with {diff_count} differences"

# Test data for testing retract_unretract component
retract_test_data = {
    'name': 'retract_unretract_component_test',
    'orig_file': '../fixtures/expected_gcode/retraction_calibration/retract_unretract.gcode',
    'render_file': '../retraction_calibration/retract_unretract.cfg',
    'params': {
        'Z_HOP_DISTANCE': 0.5,
        'Z_HOP_RETURN': 0.2,
        'TRAVEL_SPEED': 120.0,
        'RETRACT_SPEED': 25.0,
        'UNRETRACT_SPEED': 25.0,
        'RETRACT_DISTANCE': 0.8,
        'MOVE_X': 15.0,
        'MOVE_Y': 15.0
    }
}

@pytest.mark.retraction
@pytest.mark.combined
def test_retract_unretract_component_working(results_dir):
    """Test that the retract_unretract component works with the same parameters as other tests."""
    diff_count = run_gcode_comparison_test(
        results_dir,
        retract_test_data['orig_file'],
        retract_test_data['render_file'],
        retract_test_data['params'],
        retract_test_data['name']
    )
    
    assert diff_count == 0, f"Retract_unretract component test failed with {diff_count} differences"
