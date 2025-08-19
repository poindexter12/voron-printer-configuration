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
