#!/usr/bin/env python3
"""Repository convenience entrypoint; the portable implementation lives in the skill."""
from pathlib import Path
import runpy

if __name__ == "__main__":
    runpy.run_path(str(Path(__file__).parent / "skills/chatnoir/scripts/chatnoir.py"), run_name="__main__")
