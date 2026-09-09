#!/usr/bin/env python3
"""Install the bundle without overwriting existing skills or changing MCP settings."""
import argparse
import os
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]


def install(target, project=None, dry_run=False):
    base = Path(project).expanduser().resolve() if project else None
    if target == "codex":
        dest = base / ".agents" if base else Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex")))
    else:
        dest = (base if base else Path.home()) / ".claude"
    operations = [(src, dest / "skills" / src.name) for src in sorted((ROOT / "skills").iterdir()) if src.is_dir()]
    if target == "claude":
        operations.append((ROOT / "agents" / "cnki-researcher.md", dest / "agents" / "cnki-researcher.md"))
    for src, path in operations:
        if path.exists() or path.is_symlink():
            raise FileExistsError("Refusing to overwrite: " + str(path))
        if src.is_dir() and not (src / "SKILL.md").is_file():
            raise ValueError("Invalid skill: " + str(src))
    for src, path in operations:
        print(("Would install " if dry_run else "Installing ") + str(path))
        if not dry_run:
            path.parent.mkdir(parents=True, exist_ok=True)
            if src.is_dir():
                shutil.copytree(src, path, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
            else:
                shutil.copyfile(src, path)
    return len(operations)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", choices=("codex", "claude"), required=True)
    parser.add_argument("--project", help="Project-local install; otherwise user-local")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    try:
        install(args.target, args.project, args.dry_run)
    except (OSError, ValueError) as exc:
        parser.exit(1, str(exc) + "\n")
