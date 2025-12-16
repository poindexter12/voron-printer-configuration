"""Utility functions for G-code processing and testing."""

import difflib
import os
import re
from jinja2 import Environment


# Klipper uses a custom Jinja2 environment with single braces for expressions
# See: https://www.klipper3d.org/Command_Templates.html
KLIPPER_ENV = Environment('{%', '%}', '{', '}')

# Add Python built-ins that Klipper's Jinja2 environment provides
KLIPPER_ENV.globals['str'] = str
KLIPPER_ENV.globals['int'] = int
KLIPPER_ENV.globals['float'] = float
KLIPPER_ENV.globals['range'] = range
KLIPPER_ENV.globals['len'] = len
KLIPPER_ENV.globals['abs'] = abs
KLIPPER_ENV.globals['min'] = min
KLIPPER_ENV.globals['max'] = max
KLIPPER_ENV.globals['round'] = round


def extract_macro_gcode(file_path, macro_name):
    """Extract the gcode section from a Klipper macro file.

    Args:
        file_path: Path to the .cfg file containing the macro
        macro_name: Name of the macro (e.g., '_DRAW_DIGIT')

    Returns:
        String containing just the gcode section of the macro
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find the macro section
    macro_pattern = rf'\[gcode_macro\s+{re.escape(macro_name)}\]'
    macro_match = re.search(macro_pattern, content, re.IGNORECASE)
    if not macro_match:
        raise ValueError(f"Macro '{macro_name}' not found in {file_path}")

    # Get content after the macro header
    after_header = content[macro_match.end():]

    # Find the gcode: section
    gcode_match = re.search(r'^gcode:\s*\n', after_header, re.MULTILINE)
    if not gcode_match:
        raise ValueError(f"No 'gcode:' section found in macro '{macro_name}'")

    gcode_start = gcode_match.end()

    # Find where the gcode section ends (next [section] or end of file)
    next_section = re.search(r'^\[', after_header[gcode_start:], re.MULTILINE)
    if next_section:
        gcode_content = after_header[gcode_start:gcode_start + next_section.start()]
    else:
        gcode_content = after_header[gcode_start:]

    return gcode_content


def render_macro_gcode(file_path, macro_name, params):
    """Extract and render gcode from a Klipper macro with given parameters.

    Args:
        file_path: Path to the .cfg file containing the macro
        macro_name: Name of the macro (e.g., '_DRAW_DIGIT')
        params: Dictionary of parameters to pass to the template

    Returns:
        Rendered gcode as a string
    """
    gcode_template = extract_macro_gcode(file_path, macro_name)
    template = KLIPPER_ENV.from_string(gcode_template)
    return template.render(params=params)


def clean_gcode_string(content):
    """Clean a G-code string for comparison.

    Args:
        content: String containing G-code

    Returns:
        List of cleaned G-code lines
    """
    lines = content.splitlines()
    cleaned = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.startswith('[') or line.startswith(';') or line.startswith('#'):
            continue
        if '{%' in line:
            continue
        # Skip Klipper parameter lines but not G-code with inline comments
        if ':' in line and not line.startswith(('G', 'M', '_')):
            continue
        # Strip inline comments from G-code for comparison
        if ';' in line:
            line = line.split(';')[0].strip()
        if line:
            cleaned.append(line)
    return cleaned


def run_macro_comparison_test(results_dir, expected_file, macro_file, macro_name, params, test_name):
    """Compare output of a Klipper macro against expected G-code.

    Args:
        results_dir: Directory to save test results
        expected_file: Path to the expected G-code file
        macro_file: Path to the .cfg file containing the macro
        macro_name: Name of the macro to test (e.g., '_DRAW_DIGIT')
        params: Parameters to pass to the macro
        test_name: Name for the test (used in output files)

    Returns:
        diff_count: Number of differences found
    """
    expected_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'tests', expected_file)
    macro_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), macro_file)

    # Load expected G-code
    expected_cleaned = clean_gcode_file(expected_path)

    # Render and clean macro output
    rendered = render_macro_gcode(macro_path, macro_name, params)
    rendered_cleaned = clean_gcode_string(rendered)

    # Save cleaned files
    rendered_path = os.path.join(results_dir, f'{test_name}_rendered.gcode')
    with open(rendered_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(rendered_cleaned) + '\n')

    expected_clean_path = os.path.join(results_dir, f'{test_name}_expected.gcode')
    with open(expected_clean_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(expected_cleaned) + '\n')

    # Generate HTML diff
    html_diff = diff_with_html(
        expected_cleaned,
        rendered_cleaned,
        os.path.basename(expected_path),
        f"{macro_name} output"
    )

    # Count differences
    unified = list(difflib.unified_diff(expected_cleaned, rendered_cleaned, lineterm=''))
    diff_count = sum(1 for line in unified if (line.startswith('+') or line.startswith('-'))
                     and not line.startswith('+++') and not line.startswith('---'))

    # Save HTML diff
    html_diff_path = os.path.join(results_dir, f'{test_name}_diff.html')
    with open(html_diff_path, 'w', encoding='utf-8') as f:
        f.write(html_diff)

    # Log results
    log_path = os.path.join(results_dir, f'{test_name}_test.log')
    with open(log_path, 'w', encoding='utf-8') as f:
        f.write(f"{test_name.title().replace('_', ' ')} Test Results\n")
        f.write(f"Expected: {expected_file}\n")
        f.write(f"Macro: {macro_name} from {macro_file}\n")
        f.write(f"Total differences: {diff_count}\n")

    if diff_count > 0:
        print(f"{test_name}: {diff_count} differences found")
        print(f"See {os.path.relpath(html_diff_path)} for details")

    return diff_count


def clean_gcode_file(path, render_jinja=False, params=None):
    """Read a file, optionally render as Jinja2 with given parameters,
    and return cleaned lines.

    Uses Klipper's Jinja2 environment (single braces for expressions).
    """
    if params is None:
        params = {}
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
        if render_jinja:
            template = KLIPPER_ENV.from_string(content)
            content = template.render(params=params)
        lines = content.splitlines()
    cleaned = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.startswith('[') or line.startswith(';') or line.startswith('#'):
            continue
        if '{%' in line:
            continue
        # Skip Klipper parameter lines (e.g., "DIGIT: 3") but not G-code with inline comments
        # G-code lines start with G or M, so only check for : in non-gcode lines
        if ':' in line and not line.startswith(('G', 'M')):
            continue
        # Strip inline comments from G-code for comparison
        if ';' in line:
            line = line.split(';')[0].strip()
        if line:  # Make sure we still have content after stripping comment
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

    # Count actual differences using unified diff (more reliable than parsing HTML)
    unified = list(difflib.unified_diff(orig_cleaned, render_cleaned, lineterm=''))
    # Count lines starting with + or - (excluding the +++ and --- header lines)
    diff_count = sum(1 for line in unified if (line.startswith('+') or line.startswith('-')) and not line.startswith('+++') and not line.startswith('---'))

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
