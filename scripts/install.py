#!/usr/bin/env python3
"""Install the bundle with explicit, backed-up upgrades and no MCP setting changes."""
import argparse
import os
from pathlib import Path
import shutil
from datetime import datetime
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def install(target, project=None, dry_run=False, upgrade=False, with_jev=False, only_jev=False):
    if with_jev and only_jev:
        raise ValueError('Choose --with-jev or --only-jev')
    base = Path(project).expanduser().resolve() if project else None
    if target == "codex":
        dest = base / ".agents" if base else Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex")))
    elif target == "workbuddy":
        dest = (base if base else Path.home()) / ".workbuddy"
    else:
        dest = (base if base else Path.home()) / ".claude"
    sources = [src for src in sorted((ROOT / "skills").iterdir()) if src.is_dir()
               and (src.name == "cnki-jev" if only_jev else (src.name != "cnki-jev" or with_jev))]
    if only_jev:
        for name in ("cnki-screening", "cnki-resume"):
            if not (dest / "skills" / name / "SKILL.md").is_file():
                raise ValueError('Install the base bundle first; missing ' + name)
    operations = [(src, dest / "skills" / src.name) for src in sources]
    if target == "claude" and not only_jev:
        operations.append((ROOT / "agents" / "cnki-researcher.md", dest / "agents" / "cnki-researcher.md"))
    for src, path in operations:
        if path.is_symlink():
            raise FileExistsError("Refusing to replace symlink: " + str(path))
        if path.exists() and not upgrade:
            raise FileExistsError("Refusing to overwrite: " + str(path))
        if src.is_dir() and not (src / "SKILL.md").is_file():
            raise ValueError("Invalid skill: " + str(src))
    backup_root = None
    for src, path in operations:
        print(("Would upgrade/install " if dry_run else "Upgrading/installing ") + str(path))
        if dry_run:
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        # Stage the complete replacement first, preserving the original on copy failure.
        with tempfile.TemporaryDirectory(prefix=".cnki-install-", dir=str(path.parent)) as tmp:
            staged = Path(tmp) / path.name
            if src.is_dir():
                shutil.copytree(src, staged, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
            else:
                shutil.copyfile(src, staged)
            backup = None
            if path.exists():
                if backup_root is None:
                    parent = dest / "cnki-backups"
                    parent.mkdir(parents=True, exist_ok=True)
                    backup_root = Path(tempfile.mkdtemp(prefix=datetime.now().strftime("%Y%m%d-%H%M%S-"), dir=str(parent)))
                    print("Backup: " + str(backup_root))
                backup = backup_root / path.relative_to(dest)
                backup.parent.mkdir(parents=True, exist_ok=True)
                path.rename(backup)
            try:
                staged.rename(path)
            except OSError:
                if backup is not None:
                    backup.rename(path)
                raise
    return len(operations)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", choices=("codex", "claude", "workbuddy"), required=True)
    parser.add_argument("--project", help="Project-local install; otherwise user-local")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--upgrade", action="store_true", help="Replace installed bundle items with a dated backup; never follows target symlinks")
    optional = parser.add_mutually_exclusive_group()
    optional.add_argument("--with-jev", action="store_true", help="Also install the optional paid Jev adapter (disabled until configured)")
    optional.add_argument("--only-jev", action="store_true", help="Install/upgrade only Jev; requires the base screening and resume skills")
    args = parser.parse_args()
    try:
        install(args.target, args.project, args.dry_run, args.upgrade, args.with_jev, args.only_jev)
    except (OSError, ValueError) as exc:
        parser.exit(1, str(exc) + "\n")
