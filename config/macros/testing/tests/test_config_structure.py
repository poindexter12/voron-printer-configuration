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

# Sections this repo redeclares on purpose to override a third-party default.
# Klipper takes last-wins, so the overriding file has to be included AFTER the
# file it overrides; an override that loads first is silently dead, which is
# what test_intentional_overrides_win_on_load_order guards.
# Keyed by normalized section name (see normalized_section).
INTENTIONAL_OVERRIDES = {
    'gcode_macro _lazy_home_inner': {
        'overrides': 'klipper-macros/kinematics.cfg',
        'winner': 'homing.cfg',
        'why': 'sets reduced TMC currents around homing, then restores them (#17)',
    },
}

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


def normalized_section(header):
    """The key Klipper effectively compares a section header on.

    `[gcode_macro pause]` and `[gcode_macro PAUSE]` are two sections to
    configparser but one command to Klipper, which upper-cases a macro's name
    when it registers it. Comparing the headers as written misses the
    collision entirely - that is how three real duplicates between
    klipper-macros and mainsail.cfg went unreported (see #14).
    """
    return ' '.join(header.split()).lower()


def is_include(header):
    """True for an [include ...] header, whatever its casing."""
    parts = header.split()
    return bool(parts) and parts[0].lower() == 'include'


def section_headers(cfg_path):
    """Yield every [section] header in a file, excluding includes."""
    text = cfg_path.read_text(encoding='utf-8')
    return [h.strip() for h in re.findall(r'^\[([^\]]+)\]', text, re.MULTILINE)
            if not is_include(h.strip())]


def duplicate_sections(cfg_files, relative_to):
    """Map each section declared in >1 file to where it was declared.

    Keyed on the normalized header so case and spacing differences still
    collide, but reports the spelling each file actually uses - without that,
    a report of `[gcode_macro pause]` twice looks like a bug in the test.
    """
    seen = {}
    duplicates = {}
    for cfg in cfg_files:
        rel = str(cfg.relative_to(relative_to))
        for header in section_headers(cfg):
            key = normalized_section(header)
            where = f"{rel} as [{header}]"
            if key in seen and seen[key][0] != rel:
                duplicates.setdefault(key, {seen[key][1]}).add(where)
            else:
                seen.setdefault(key, (rel, where))
    return duplicates


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


def load_order():
    """Map each config file to its position in Klipper's load order."""
    return {str(f.relative_to(CONFIG_ROOT)): i
            for i, f in enumerate(local_config_files())}


def is_declared_override(key, files):
    """True when this collision is exactly the override we declared."""
    declared = INTENTIONAL_OVERRIDES.get(key)
    if declared is None:
        return False
    # `files` holds "<path> as [<header>]" strings; compare on the paths.
    paths = {entry.split(' as [')[0] for entry in files}
    return paths == {declared['overrides'], declared['winner']}


@pytest.mark.config
def test_no_section_declared_in_two_files():
    """Klipper takes last-wins on a duplicated section, without warning.

    Declared overrides in INTENTIONAL_OVERRIDES are exempt, but only for the
    exact file pair they name - a third file declaring the same section, or
    the override moving, still fails.
    """
    duplicates = {k: v for k, v in duplicate_sections(local_config_files(), CONFIG_ROOT).items()
                  if not is_declared_override(k, v)}
    assert not duplicates, "Sections declared in more than one file: " + ", ".join(
        f"[{key}] in {sorted(files)}" for key, files in sorted(duplicates.items()))


@pytest.mark.config
def test_intentional_overrides_win_on_load_order():
    """An override included before the file it overrides is dead code.

    Klipper takes the last declaration, so getting this backwards leaves the
    upstream version active with no error - the exact silence these checks
    exist to remove.
    """
    order = load_order()
    wrong = []
    for key, decl in INTENTIONAL_OVERRIDES.items():
        winner, loser = decl['winner'], decl['overrides']
        if winner not in order or loser not in order:
            continue  # not resolvable in this checkout; other tests cover that
        if order[winner] < order[loser]:
            wrong.append(f"[{key}] {winner} loads before {loser}, so the override never applies")
    assert not wrong, "; ".join(wrong)


@pytest.mark.config
def test_intentional_overrides_are_still_real():
    """Keeps the allowlist from outliving the collision it excuses."""
    duplicates = duplicate_sections(local_config_files(), CONFIG_ROOT)
    order = load_order()
    stale = []
    for key, decl in INTENTIONAL_OVERRIDES.items():
        if decl['overrides'] not in order:
            continue  # submodule not checked out
        if key not in duplicates:
            stale.append(f"[{key}] is allowlisted but no longer declared in two files")
    assert not stale, "; ".join(stale)


@pytest.mark.config
def test_every_feature_macro_is_actually_included():
    """A macro folder nobody wired up loads nothing, silently.

    Klipper globs are not recursive, so every macros/<feature>/ needs its own
    [include] line in printer.cfg. Forget one and the macros are simply absent
    at runtime - no error, no warning. test_every_include_resolves catches the
    inverse (an include pointing at a folder that is gone); this catches the
    folder that exists but was never wired up.

    Asserting the .cfg files end up in the resolved load set, rather than
    matching the include text, also catches a typo'd or too-narrow glob.
    """
    loaded = {f.resolve() for f in local_config_files()}
    missing = []
    for feature_dir in sorted(MACROS_ROOT.iterdir()):
        if (not feature_dir.is_dir() or feature_dir.name.startswith('.')
                or feature_dir.name in NON_FEATURE_MACRO_DIRS):
            continue
        for cfg in sorted(feature_dir.glob('*.cfg')):
            if cfg.resolve() not in loaded:
                missing.append(str(cfg.relative_to(CONFIG_ROOT)))
    assert not missing, (
        "Macro files that no [include] in printer.cfg loads: "
        f"{missing}. Add [include macros/<feature>/*.cfg] for each.")


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


def write_cfgs(tmp_path, **files):
    """Write {name: text} as .cfg files and return them in a stable order."""
    for name, text in files.items():
        (tmp_path / f'{name}.cfg').write_text(text, encoding='utf-8')
    return sorted(tmp_path.glob('*.cfg'))


@pytest.mark.config
def test_duplicate_sections_catches_case_mismatch(tmp_path):
    """The regression behind #14.

    klipper-macros writes `[gcode_macro pause]`, mainsail.cfg writes
    `[gcode_macro PAUSE]`. Klipper upper-cases both to one command; comparing
    the headers as written treats them as unrelated and passes green.
    """
    cfgs = write_cfgs(tmp_path,
                      a='[gcode_macro pause]\ngcode:\n    M117 a\n',
                      b='[gcode_macro PAUSE]\ngcode:\n    M117 b\n')
    duplicates = duplicate_sections(cfgs, tmp_path)
    assert 'gcode_macro pause' in duplicates


@pytest.mark.config
def test_duplicate_sections_reports_the_spelling_each_file_uses(tmp_path):
    """A report showing the same header twice reads as a bug in the test."""
    cfgs = write_cfgs(tmp_path,
                      a='[gcode_macro pause]\n',
                      b='[gcode_macro PAUSE]\n')
    where = duplicate_sections(cfgs, tmp_path)['gcode_macro pause']
    assert where == {'a.cfg as [gcode_macro pause]', 'b.cfg as [gcode_macro PAUSE]'}


@pytest.mark.config
def test_duplicate_sections_collides_on_spacing_too(tmp_path):
    """`config.get_name().split()` makes inner spacing irrelevant to Klipper."""
    cfgs = write_cfgs(tmp_path,
                      a='[gcode_macro  PAUSE]\n',
                      b='[gcode_macro PAUSE]\n')
    assert 'gcode_macro pause' in duplicate_sections(cfgs, tmp_path)


@pytest.mark.config
def test_duplicate_sections_ignores_includes_whatever_the_casing(tmp_path):
    """An [Include] is a directive, not a section that can collide.

    Matching the prefix case-sensitively made a capitalised include look like
    an ordinary section, so two files including the same file were reported as
    a duplicate declaration - a false failure with nothing to fix.
    """
    cfgs = write_cfgs(tmp_path,
                      a='[Include shared.cfg]\n[respond]\n',
                      b='[Include shared.cfg]\n')
    assert duplicate_sections(cfgs, tmp_path) == {}


@pytest.mark.config
def test_duplicate_sections_ignores_a_repeat_inside_one_file(tmp_path):
    """Only cross-file collisions are in scope; one file is the author's business."""
    cfgs = write_cfgs(tmp_path, a='[respond]\n[respond]\n')
    assert duplicate_sections(cfgs, tmp_path) == {}
