"""Utility functions for G-code processing and testing."""

import os
import re
from jinja2 import Template


def klipper_to_jinja(text):
    """Convert Klipper-style {variable} to Jinja2-style {{ variable }}."""
    converted = re.sub(r'(?<!\{)\{([a-zA-Z0-9_]+)\}(?!\})', r'{{ \1 }}', text)
    return converted


def clean_gcode_file(path, render_jinja=False, params=None):
    """Read a file, optionally render as Jinja2 with given parameters,
    and return cleaned lines."""
    if params is None:
        params = {}
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
        if render_jinja:
            content = klipper_to_jinja(content)
            content = Template(content).render(params=params)
        lines = content.splitlines()
    cleaned = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.startswith('[') or line.startswith(';') or line.startswith('#'):
            continue
        if '{%' in line or ':' in line:
            continue
        cleaned.append(line)
    return cleaned


def save_cleaned_files(results_dir, render, render_cleaned, orig, orig_cleaned):
    """Save cleaned rendered and source files to disk."""
    # Ensure rendered output gets .gcode extension since it contains G-code
    render_basename = os.path.basename(render)
    if render_basename.endswith('.cfg'):
        render_basename = render_basename[:-4] + '.gcode'

    render_clean_path = os.path.join(
        results_dir, f'rendered_clean_{render_basename}')
    with open(render_clean_path, 'w', encoding='utf-8') as rc:
        rc.write('\n'.join(render_cleaned) + '\n')

    source_clean_path = os.path.join(
        results_dir, f'source_clean_{os.path.basename(orig)}')
    with open(source_clean_path, 'w', encoding='utf-8') as sc:
        sc.write('\n'.join(orig_cleaned) + '\n')


def diff_with_html(original_lines, generated_lines, original_name="original", generated_name="generated"):
    """Use difflib to generate an HTML diff between two sets of lines.

    Args:
        original_lines: List of strings from the original/reference file
        generated_lines: List of strings from the generated file
        original_name: Name to use for the original file in diff output
        generated_name: Name to use for the generated file in diff output

    Returns:
        HTML string with formatted diff
    """
    import difflib
    html_diff = difflib.HtmlDiff()
    return html_diff.make_file(original_lines, generated_lines, original_name, generated_name)


def run_gcode_comparison_test(results_dir, orig_file, render_file, params, test_name):
    """Common method to run G-code comparison tests with given file names and parameters.

    This function handles all common output logic including HTML diff saving and logging.
    It can be used by any test that needs to compare G-code files.

    Args:
        results_dir: Directory to save test results
        orig_file: Path to the original/expected G-code file
        render_file: Path to the template file to render
        params: Parameters to pass to the Jinja2 template
        test_name: Name for the test (used in output files)

    Returns:
        diff_count: Number of differences found
    """
    orig_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'tests', orig_file)
    render_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), render_file)

    orig_cleaned = clean_gcode_file(orig_path)
    render_cleaned = clean_gcode_file(render_path, render_jinja=True, params=params)

    # Save cleaned files using helper
    save_cleaned_files(results_dir, render_path, render_cleaned, orig_path,
                      orig_cleaned)

    # Generate HTML diff for easier viewing
    html_diff = diff_with_html(
        orig_cleaned,
        render_cleaned,
        os.path.basename(orig_path),
        os.path.basename(render_path)
    )

    # Count actual differences (lines that start with + or -)
    diff_count = sum(1 for line in html_diff.split('\n') if line.startswith('<td class="diff_add">') or line.startswith('<td class="diff_sub">'))

    # Save HTML diff for easier viewing
    html_diff_path = os.path.join(results_dir, f'{test_name}_diff.html')
    with open(html_diff_path, 'w', encoding='utf-8') as htmlf:
        htmlf.write(html_diff)

    # Log results
    log_path = os.path.join(results_dir, f'{test_name}_test.log')
    with open(log_path, 'w', encoding='utf-8') as logf:
        logf.write(f"{test_name.title().replace('_', ' ')} Test Results\n")
        logf.write(f"Expected: {orig_file}\n")
        logf.write(f"Generated: {render_file}\n")
        logf.write(f"Total differences: {diff_count}\n")
        logf.write(f"HTML diff: {os.path.basename(html_diff_path)}")

    # Print console output if there are differences
    if diff_count > 0:
        print(f"{test_name.title().replace('_', ' ')} Test: {diff_count} differences found")
        print(f"See {os.path.relpath(log_path)} for details")
        print(f"HTML diff: {os.path.relpath(html_diff_path)}")

    return diff_count
