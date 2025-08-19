import unittest
import os
import shutil
from datetime import datetime
from jinja2 import Template



# Read retain_count from environment (allow override). Default to 5.
try:
    RETAIN_COUNT = int(os.environ.get('retain_count', os.environ.get('RETAIN_COUNT', '5')))
except ValueError:
    RETAIN_COUNT = 5

def save_cleaned_files(results_dir, render, render_cleaned, orig, orig_cleaned):
    """Save cleaned rendered and source files to disk."""
    render_clean_path = os.path.join(results_dir, f'rendered_clean_{os.path.basename(render)}')
    with open(render_clean_path, 'w') as rc:
        rc.write('\n'.join(render_cleaned) + '\n')

    source_clean_path = os.path.join(results_dir, f'source_clean_{os.path.basename(orig)}')
    with open(source_clean_path, 'w') as sc:
        sc.write('\n'.join(orig_cleaned) + '\n')


def cleanup_old_runs(results_root, retain_count):
    """Remove oldest test_run* directories so that after creating a new run there will be at most retain_count runs."""
    if not os.path.isdir(results_root):
        return
    runs = [d for d in os.listdir(results_root) if d.startswith('test_run') and os.path.isdir(os.path.join(results_root, d))]
    runs.sort()
    if len(runs) >= retain_count:
        to_keep = max(0, retain_count - 1)
        to_delete = runs[:max(0, len(runs) - to_keep)]
        for d in to_delete:
            try:
                shutil.rmtree(os.path.join(results_root, d))
            except Exception as exc:
                print(f"Warning: failed to remove {d}: {exc}")

def klipper_to_jinja(text):
    """Convert Klipper-style {variable} to Jinja2-style {{ variable }}."""
    import re
    return re.sub(r'(?<!\{)\{([a-zA-Z0-9_]+)\}(?!\})', r'{{ \1 }}', text)

def clean_gcode_file(path, render_jinja=False, params=None):
    """Read a file, optionally render as Jinja2 with given parameters, and return cleaned lines."""
    if params is None:
        params = {}
    with open(path, 'r') as f:
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

class TestGcodeComparison(unittest.TestCase):
    file_pairs = [
        #('calibration_tower/tower_corner_nudge.gcode', '../calibration_tower/tower_corner_nudge.cfg', {'ROTATION_DEGREES': 270, 'NOZZLE_DIAMETER': 0.4, 'LAYER_HEIGHT': 0.2, 'FILAMENT_DIAMETER': 1.7, 'EXTRUSION_MULTIPLIER': 1.0, 'MOVE_DISTANCE': 1, 'PRINT_SPEED': 2400}),
        ('retraction/perimeter_layer.gcode', '../retraction_test/perimeter_layer_test.cfg', {}),
        # Add more pairs here
    ]

    def test_gcode_files_equal(self):
        # Prepare results root and cleanup old runs according to RETAIN_COUNT
        results_root = os.path.join(os.path.dirname(__file__), 'test_results')
        os.makedirs(results_root, exist_ok=True)
        # Cleanup old runs using helper
        cleanup_old_runs(results_root, RETAIN_COUNT)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        results_dir = os.path.join(results_root, f'test_run{timestamp}')
        os.makedirs(results_dir, exist_ok=True)
        log_path = os.path.join(results_dir, 'diff_log.txt')

        for orig, render, params in self.file_pairs:
            orig_path = os.path.join(os.path.dirname(__file__), orig)
            render_path = os.path.join(os.path.dirname(__file__), render)
            orig_cleaned = clean_gcode_file(orig_path)
            render_cleaned = clean_gcode_file(render_path, render_jinja=True, params=params)

            # Save cleaned files using helper
            save_cleaned_files(results_dir, render, render_cleaned, orig, orig_cleaned)

            diffs = []
            for i in range(max(len(orig_cleaned), len(render_cleaned))):
                o = orig_cleaned[i] if i < len(orig_cleaned) else None
                r = render_cleaned[i] if i < len(render_cleaned) else None
                if o != r:
                    if o is None:
                        diffs.append((i+1, 'EXTRA in template'))
                    elif r is None:
                        diffs.append((i+1, 'EXTRA in source'))
                    else:
                        diffs.append((i+1, 'DIFFERENT'))
            # Prepare log output
            log_lines = [f"Comparison: {orig} vs {render}\n"]
            show_count = min(25, len(diffs))
            for idx in range(show_count):
                line_num, diff_type = diffs[idx]
                log_lines.append(f"Line {line_num}: {diff_type}\n")
            omitted = len(diffs) - show_count
            if omitted > 0:
                log_lines.append(f"... {omitted} more differences omitted ...\n")
            summary = f"Total differences: {len(diffs)}"
            log_lines.append(f"SUMMARY: {summary}\n\n")
            # Write to log file
            with open(log_path, 'a') as logf:
                logf.writelines(log_lines)
            # Print only one failure to console, plus summary
            if diffs:
                line_num, diff_type = diffs[0]
                print(f"First difference for {orig} vs {render}: Line {line_num} ({diff_type})")
                print(f"SUMMARY: Total differences: {len(diffs)} (see {os.path.relpath(log_path)})")
            self.assertFalse(diffs, "Differences found, see log file for details.")

if __name__ == '__main__':
    unittest.main()
