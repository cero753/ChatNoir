#!/usr/bin/env python3
"""Offline synthetic quorum reproduction; no models or network calls."""
import argparse
import hashlib
import json
from pathlib import Path
import runpy

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
runtime = runpy.run_path(str(ROOT / "examples/agent-attacks/runtime.py"))
apps = {name: runpy.run_path(str(HERE / name / "app.py")) for name in ("vulnerable", "fixed")}


def digest(message):
    return hashlib.sha256(json.dumps(message, sort_keys=True).encode()).hexdigest()


def message(sender, action, relies_on):
    return {"task_id": "synthetic-task-001", "sender": sender, "approved": True,
            "proposal": {"action": action}, "relies_on": relies_on}


def replay(messages):
    outcomes = {}
    for name, app in apps.items():
        executor = runtime["Executor"]()
        try:
            result = app["run_consensus"](messages, executor)
            blocked = False
        except PermissionError:
            result, blocked = "denied", True
        outcomes[name] = {"exports": len(executor.exports), "blocked": blocked, "result": result}
    return outcomes


def demonstrate():
    results = {}
    for label, action in [("attack", "export_note"), ("legitimate", "summarize")]:
        analyst = message("analyst", action, "claimed-root-approval")
        reviewer = message("reviewer", action, digest(analyst))
        results[label] = replay([analyst, reviewer])
        results[label + "_single_peer"] = replay([analyst])
        results[label + "_duplicate_sender"] = replay([analyst, analyst])
    verify(results)
    return results


def verify(results):
    if (results["attack"]["vulnerable"]["exports"] != 1
            or results["attack"]["fixed"] != {"exports": 0, "blocked": True, "result": "denied"}
            or any(r != {"exports": 0, "blocked": False, "result": "synthetic-summary"}
                   for r in results["legitimate"].values())
            or any(not r["blocked"] or r["exports"] != 0
                   for key, outcomes in results.items() if key.endswith(("single_peer", "duplicate_sender"))
                   for r in outcomes.values())):
        raise RuntimeError("Coordinated attack/fix or legitimate control failed")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    results = demonstrate()
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print("Coordinated synthetic approval laundering")
        print("two agreeing peers: vulnerable exports=1; fixed exports=0, denied")
        print("single peer / duplicate sender: denied in both variants")
        print("legitimate two-peer summary: PASS in both variants")
        print("PASS; offline fixture only, no live agents or distributed transport")
