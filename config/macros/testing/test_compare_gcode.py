import unittest
import os
from datetime import datetime

def clean_gcode_lines(lines):
    cleaned = []
    in_gcode = False
    for line in lines:
        line = line.strip()
        if not in_gcode:
            if line.lower() == 'gcode:':
                in_gcode = True
            continue
        if line and (line.startswith('[') and line.endswith(']')):
            break
        if line and ':' in line and not line.startswith(';'):
            continue
        if not line or line.startswith(';') or line.startswith('#'):
            continue
        if '{%' in line or '%}' in line:
            continue
        if ';' in line:
            line = line.split(';', 1)[0].strip()
        cleaned.append(line)
    return cleaned

class TestGcodeComparison(unittest.TestCase):
    file_pairs = [
        ('../calibration_tower/original.old', '../calibration_tower/calibration_tower.cfg'),
        # Add more pairs here
    ]

    def test_gcode_files_equal(self):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        results_dir = os.path.join(os.path.dirname(__file__), 'test_results', f'test_run{timestamp}')
        os.makedirs(results_dir, exist_ok=True)
        log_path = os.path.join(results_dir, 'diff_log.txt')
        for orig, render in self.file_pairs:
            orig_path = os.path.join(os.path.dirname(__file__), orig)
            render_path = os.path.join(os.path.dirname(__file__), render)
            with open(orig_path, 'r') as f:
                orig_lines = f.readlines()
            with open(render_path, 'r') as f:
                render_lines = f.readlines()
            # Clean both after rendering
            orig_cleaned = clean_gcode_lines(orig_lines)
            render_cleaned = clean_gcode_lines(render_lines)
            # Save cleaned rendered template
            render_clean_path = os.path.join(results_dir, f'rendered_clean_{os.path.basename(render)}')
            with open(render_clean_path, 'w') as rc:
                rc.write('\n'.join(render_cleaned) + '\n')
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
                print(f"SUMMARY: Total differences: {len(diffs)} (see {log_path})")
            self.assertFalse(diffs, "Differences found, see log file for details.")

if __name__ == '__main__':
    unittest.main()
