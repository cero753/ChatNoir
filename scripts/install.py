#!/usr/bin/env python3
"""Copy ChatNoir into a project's skill directory without replacing existing files."""
import argparse
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
LOCATIONS = {"codex": ".agents/skills", "claude": ".claude/skills", "cursor": ".cursor/skills", "agents": ".agents/skills"}


def install(harness: str, project: Path) -> Path:
    project = project.resolve(strict=True)
    if not project.is_dir():
        raise ValueError("project must be an existing directory")
    source = ROOT / "skills/chatnoir"
    parent = project
    for component in Path(LOCATIONS[harness]).parts:
        parent = parent / component
        if parent.is_symlink():
            raise ValueError("refusing a linked destination directory")
        parent.mkdir(exist_ok=True)
    dest = parent / "chatnoir"
    # mkdir is exclusive, including for dangling links. No --force operation.
    dest.mkdir()
    for item in source.rglob("*"):
        if item.is_symlink():
            raise ValueError("refusing linked package content")
    shutil.copytree(source, dest, dirs_exist_ok=True, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    return dest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--harness", choices=LOCATIONS, required=True)
    parser.add_argument("--project", type=Path, required=True)
    args = parser.parse_args()
    try:
        dest = install(args.harness, args.project)
    except FileNotFoundError:
        print(f"Install failed: project folder not found: {args.project}", file=sys.stderr)
        print("Pass --project the path of an existing project folder, for example the folder you open in your agent. Nothing was installed.", file=sys.stderr)
        return 2
    except FileExistsError:
        existing = Path(LOCATIONS[args.harness]) / "chatnoir"
        print(f"Install failed: ChatNoir is already installed at {existing} in this project. The existing skill was kept unchanged.", file=sys.stderr)
        print("To update it, follow docs/compatibility.md#skill-only-installation.", file=sys.stderr)
        return 2
    except (OSError, ValueError) as error:
        print(f"Install failed ({type(error).__name__}); existing skills were not replaced.", file=sys.stderr)
        return 2
    print(f"Installed ChatNoir: {dest}")
    print("Open a fresh agent session in the target project and ask it to use ChatNoir.")
    print("First review: Use ChatNoir's guided first review on this project. Keep it read-only.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
