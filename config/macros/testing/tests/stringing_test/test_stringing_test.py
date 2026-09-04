"""Test suite for the STRINGING_TEST macro."""

import pytest
from utils.gcode_helpers import run_macro_comparison_test

stringing_test_data = {
    'name': 'stringing_test',
    'orig_file': '../fixtures/expected_gcode/stringing_test/stringing_test.gcode',
    'render_file': '../stringing_test/stringing_test.cfg',
    'macro_name': 'STRINGING_TEST',
    'params': {'PREP': 0}
}


@pytest.mark.stringing
def test_stringing_test_macro(results_dir):
    """Test the stringing test macro against the frozen reference render."""
    diff_count = run_macro_comparison_test(
        results_dir,
        stringing_test_data['orig_file'],
        stringing_test_data['render_file'],
        stringing_test_data['macro_name'],
        stringing_test_data['params'],
        stringing_test_data['name']
    )
    assert diff_count == 0, f"Macro test failed with {diff_count} differences"
