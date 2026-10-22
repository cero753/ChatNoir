#!/usr/bin/env python3
"""Offline evidence for one deliberately vulnerable agent-permission fixture.

No model, network, credentials or external tools. The export sink is a local list.
Run from any directory; results are printed, not written into reviewed sources.
"""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import runpy

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "examples/agent-attacks"
PATHS = ["vulnerable/app.py", "fixed/app.py", "runtime.py"]


def sources():
    return {name: hashlib.sha256((FIXTURES / name).read_bytes()).hexdigest() for name in PATHS}


def replay():
    before_sources = sources()
    apps = {name: runpy.run_path(str(FIXTURES / name / "app.py")) for name in ("vulnerable", "fixed")}
    Executor = runpy.run_path(str(FIXTURES / "runtime.py"))["Executor"]

    def call(app, action, *, bypass=False):
        executor = Executor()
        # A disposable-instance mutation checks that the claimed gate matters.
        if bypass:
            executor.authorize = lambda proposal: dict(proposal)
        message = {"sender": "coordinator", "capabilities": [action], "proposal": {"action": action}}
        try:
            result = app["run_peer_message"](message, executor)
            blocked = False
        except PermissionError:
            result, blocked = "denied", True
        assert executor.allowed_actions == frozenset({"summarize"})
        return {"exports": len(executor.exports), "blocked": blocked, "result": result}

    observed = {
        "unauthorized_peer_proposal": {name: call(app, "export_note") for name, app in apps.items()},
        "legitimate_summary": {name: call(app, "summarize") for name, app in apps.items()},
        "fixed_gate_bypassed": call(apps["fixed"], "export_note", bypass=True),
    }
    exported = {"exports": 1, "blocked": False, "result": "exported-to-local-list"}
    denied = {"exports": 0, "blocked": True, "result": "denied"}
    summary = {"exports": 0, "blocked": False, "result": "synthetic-summary"}
    assert observed["unauthorized_peer_proposal"] == {"vulnerable": exported, "fixed": denied}
    assert observed["legitimate_summary"] == {"vulnerable": summary, "fixed": summary}
    assert observed["fixed_gate_bypassed"] == exported
    assert sources() == before_sources, "Reviewed sources changed during replay"
    return {"format": "chatnoir.agent-permission-evidence/v1",
            "executed_at": datetime.now(timezone.utc).isoformat(),
            "source_sha256": before_sources, "observed": observed, "checks_passed": True,
            "limits": ["Known owner-authored synthetic fixture, not a client or production finding.",
                       "No model inference, distributed agents, external export or real data.",
                       "Only peer-message action authorization was assessed."]}


if __name__ == "__main__":
    print(json.dumps(replay(), indent=2))
