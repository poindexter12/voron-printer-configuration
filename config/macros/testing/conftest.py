"""Pytest configuration and shared fixtures for Klipper macro testing."""

import os
import shutil
from datetime import datetime
import pytest


# Read retain_count from environment (allow override). Default to 5.
try:
    RETAIN_COUNT = int(os.environ.get('retain_count',
                                     os.environ.get('RETAIN_COUNT', '5')))
except ValueError:
    RETAIN_COUNT = 5


def cleanup_old_runs(results_root, retain_count):
    """Remove oldest test_run* directories so that after creating a new run
    there will be at most retain_count runs."""
    if not os.path.isdir(results_root):
        return
    runs = [d for d in os.listdir(results_root)
            if d.startswith('test_run') and
            os.path.isdir(os.path.join(results_root, d))]
    runs.sort()
    if len(runs) >= retain_count:
        to_keep = max(0, retain_count - 1)
        to_delete = runs[:max(0, len(runs) - to_keep)]
        for d in to_delete:
            try:
                shutil.rmtree(os.path.join(results_root, d))
            except (OSError, PermissionError) as exc:
                print(f"Warning: failed to remove {d}: {exc}")


@pytest.fixture(scope="session")
def results_dir():
    """Create and return results directory for this test session."""
    results_root = os.path.join(os.path.dirname(__file__), 'test_results')
    os.makedirs(results_root, exist_ok=True)
    # Cleanup old runs using helper
    cleanup_old_runs(results_root, RETAIN_COUNT)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    results_dir = os.path.join(results_root, f'test_run{timestamp}')
    os.makedirs(results_dir, exist_ok=True)
    return results_dir


@pytest.fixture(scope="session")
def fixtures_dir():
    """Return the fixtures directory path."""
    return os.path.join(os.path.dirname(__file__), 'fixtures')


@pytest.fixture(scope="session")
def expected_gcode_dir(fixtures_dir):
    """Return the expected G-code fixtures directory path."""
    return os.path.join(fixtures_dir, 'expected_gcode')
