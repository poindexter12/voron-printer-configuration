"""Structural checks on the Klipper config tree itself.

These are not macro-rendering tests. They guard the wiring that has broken
before: include globs left pointing at renamed folders, a section declared in
two files so Klipper silently takes last-wins, macro folders whose test
directory drifted out of sync, and pytest markers used but never registered.
"""

import configparser
import re
from pathlib import Path

import pytest

TESTING_ROOT = Path(__file__).resolve().parents[1]
CONFIG_ROOT = TESTING_ROOT.parents[1]
MACROS_ROOT = CONFIG_ROOT / 'macros'
PRINTER_CFG = CONFIG_ROOT / 'printer.cfg'

# Includes that only resolve on the printer. mainsail.cfg is a symlink into
# ~/mainsail-config, which does not exist on a dev machine or in CI.
EXTERNAL_INCLUDES = {'mainsail.cfg'}

# Folders under macros/ that hold tooling rather than Klipper macros.
NON_FEATURE_MACRO_DIRS = {'testing'}

# config/klipper-macros is a git submodule. A clone without --recursive leaves
# it empty, which is a checkout problem rather than a config problem, so the
# include checks step around it instead of reporting a false failure.
SUBMODULE_ROOT = CONFIG_ROOT / 'klipper-macros'
SUBMODULE_CHECKED_OUT = any(SUBMODULE_ROOT.glob('*.cfg'))


def skipped_targets():
    """Include targets that cannot be resolved in this checkout."""
    skipped = set(EXTERNAL_INCLUDES)
    if not SUBMODULE_CHECKED_OUT:
        skipped.add('klipper-macros/*.cfg')
    return skipped


def include_targets(cfg_path):
    """Yield the raw target of every [include ...] in a config file."""
    text = cfg_path.read_text(encoding='utf-8')
    return re.findall(r'^\[include\s+(.+?)\]', text, re.MULTILINE)


def section_headers(cfg_path):
    """Yield every [section] header in a file, excluding includes."""
    text = cfg_path.read_text(encoding='utf-8')
    return [h.strip() for h in re.findall(r'^\[([^\]]+)\]', text, re.MULTILINE)
            if not h.startswith('include')]


def local_config_files():
    """Every config file Klipper loads that is readable off the printer."""
    files = [PRINTER_CFG]
    skip = skipped_targets()
    for target in include_targets(PRINTER_CFG):
        if target in skip:
            continue
        files.extend(sorted(CONFIG_ROOT.glob(target)))
    return [f for f in files if f.is_file()]


@pytest.mark.config
def test_every_include_resolves():
    """Each [include] in printer.cfg matches at least one real file.

    A glob that matches nothing is silent in Klipper, so a renamed macro
    folder disables its macros without any error at startup.
    """
    unresolved = []
    skip = skipped_targets()
    for target in include_targets(PRINTER_CFG):
        if target in skip:
            continue
        if not any(p.is_file() for p in CONFIG_ROOT.glob(target)):
            unresolved.append(target)
    assert not unresolved, \
        f"printer.cfg includes that match no file: {unresolved}"


@pytest.mark.config
def test_external_includes_are_declared_not_missing():
    """Anything in EXTERNAL_INCLUDES must still be referenced by printer.cfg.

    Keeps the allowlist from outliving the include it excuses.
    """
    targets = set(include_targets(PRINTER_CFG))
    stale = EXTERNAL_INCLUDES - targets
    assert not stale, \
        f"EXTERNAL_INCLUDES lists targets printer.cfg no longer includes: {sorted(stale)}"


@pytest.mark.config
def test_no_section_declared_in_two_files():
    """Klipper takes last-wins on a duplicated section, without warning."""
    seen = {}
    duplicates = {}
    for cfg in local_config_files():
        for header in section_headers(cfg):
            rel = str(cfg.relative_to(CONFIG_ROOT))
            if header in seen and seen[header] != rel:
                duplicates.setdefault(header, {seen[header]}).add(rel)
            else:
                seen.setdefault(header, rel)
    assert not duplicates, "Sections declared in more than one file: " + ", ".join(
        f"[{h}] in {sorted(files)}" for h, files in sorted(duplicates.items()))


@pytest.mark.config
def test_every_macro_folder_has_a_matching_test_folder():
    """CLAUDE.md requires macros/<feature>/ to mirror tests/<feature>/."""
    features = {d.name for d in MACROS_ROOT.iterdir()
                if d.is_dir() and not d.name.startswith('.')
                and d.name not in NON_FEATURE_MACRO_DIRS
                and any(d.glob('*.cfg'))}
    test_dirs = {d.name for d in (TESTING_ROOT / 'tests').iterdir()
                 if d.is_dir() and not d.name.startswith(('.', '__'))}
    missing = features - test_dirs
    assert not missing, \
        f"Macro folders with no matching tests/<feature>/ directory: {sorted(missing)}"


@pytest.mark.config
def test_all_pytest_markers_are_registered():
    """A marker used but absent from pytest.ini silently filters nothing.

    `pytest -m stringing` against an unregistered marker selects zero tests
    and exits green, which is how a whole suite can stop running unnoticed.
    """
    parser = configparser.ConfigParser()
    parser.read(TESTING_ROOT / 'pytest.ini')
    registered = {line.split(':', 1)[0].strip()
                  for line in parser['pytest']['markers'].splitlines()
                  if line.strip()}

    used = set()
    for test_file in (TESTING_ROOT / 'tests').rglob('test_*.py'):
        used.update(re.findall(r'@pytest\.mark\.(\w+)',
                               test_file.read_text(encoding='utf-8')))
    used -= {'parametrize', 'skip', 'skipif', 'xfail', 'usefixtures'}

    unregistered = used - registered
    assert not unregistered, \
        f"Markers used in tests but missing from pytest.ini: {sorted(unregistered)}"
