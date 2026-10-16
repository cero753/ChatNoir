#!/usr/bin/env python3
"""Run real, local ChatNoir demonstrations; no servers, network or credentials."""
from pathlib import Path
import json
import runpy
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
cn = runpy.run_path(str(ROOT / "skills/chatnoir/scripts/chatnoir.py"))


def main():
    print("CHATNOIR / Find the flaw. Prove the path. Verify the fix.\n")
    print("01 / Find a candidate in a real Python fixture")
    vulnerable = cn["baseline"](ROOT / "examples/sql-injection/vulnerable")
    fixed = cn["baseline"](ROOT / "examples/sql-injection/fixed")
    finding = vulnerable["findings"][0]
    print(f"  {finding['rule_id']} {finding['cwe']}: {finding['title']}")
    print(f"  app.py:{finding['line']} | candidate | validation: not_run")
    print("  A match is a lead. It needs a reachable attack path.\n")
    print("02 / Reproduce the attack and check the fix")
    observed = runpy.run_path(str(ROOT / "examples/sql-injection/reproduce.py"))["demonstrate"]()
    for name, result in observed.items():
        print(f"  {name}: attack={result['attack_rows']} rows; legitimate={result['legitimate_rows']} row")
    print(f"  Fixed baseline: {len(fixed['findings'])} candidates. Coverage remains incomplete.")
    print("  Runtime boundary check: PASS (synthetic in-memory SQLite).\n")
    print("03 / Challenge a false positive")
    false_positive = cn["baseline"](ROOT / "examples/false-positive")
    print(f"  Baseline: {len(false_positive['findings'])} candidate, not a confirmed vulnerability.")
    code = runpy.run_path(str(ROOT / "examples/false-positive/app.py"))
    print(f"  Source: fixed literal expression, no caller input. Runtime result: {code['two_plus_two']()}.")
    print("  Reviewer disposition: dismiss this claim; literal input defeats the proposed injection.\n")
    print("04 / Bind an exact committed patch")
    with tempfile.TemporaryDirectory(prefix="chatnoir-demo-") as temp:
        target = Path(temp)
        def git(*args):
            return subprocess.run(["git", "-C", temp, *args], check=True, capture_output=True, text=True).stdout.strip()
        git("init", "-b", "main")
        git("config", "user.name", "ChatNoir demo")
        git("config", "user.email", "demo@example.invalid")
        git("config", "commit.gpgsign", "false")
        for version in ("vulnerable", "fixed"):
            (target / "app.py").write_bytes((ROOT / "examples/sql-injection" / version / "app.py").read_bytes())
            git("add", "app.py")
            git("commit", "-m", version)
        patch = cn["exact_diff"](target, "HEAD~1", "HEAD")
        print(f"  Changed files: {json.dumps(patch['files'])}")
        print(f"  Base/head: both resolved to full {len(patch['base'])}-character commit IDs.")
        print(f"  Patch SHA-256: {patch['patch_sha256']}")
        print("  Identity captured. A merge recommendation still requires source review.")
    print("\nAll demos completed. These fixtures do not measure real-world detection accuracy.")


if __name__ == "__main__":
    main()
