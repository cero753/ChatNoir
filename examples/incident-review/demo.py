#!/usr/bin/env python3
"""Offline incident-report demonstration. No real provider or runtime is assessed."""
import argparse
from datetime import date
import json
from pathlib import Path
import runpy

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = Path(__file__).resolve().parent / "fixtures"
cn = runpy.run_path(str(ROOT / "skills/chatnoir/scripts/chatnoir.py"))


class SyntheticService:
    """A local stand-in for a deployed service, not an actual vulnerable runtime."""
    def __init__(self, version):
        self.version = version

    def health(self):
        return {"status": "ok", "runtime": "DemoRuntime", "version": self.version}


def demonstrate():
    scenario = json.loads((FIXTURES / "scenario.json").read_text())
    advisory = scenario["advisory"]
    today = date.today().isoformat()
    service = SyntheticService(scenario["before_version"])
    reports = {}
    for stage in ("before", "after"):
        if stage == "after":
            service.version = scenario["after_version"]
        observed = service.health()
        assert observed["status"] == "ok"
        fixed = observed["version"] in advisory["fixed_versions"]
        affected = observed["version"] in advisory["affected_versions"]
        status = "not_affected" if fixed else "potentially_affected" if affected else "undetermined"
        report = cn["baseline"](Path(__file__).resolve().parent)
        report.update(mode="verify" if stage == "after" else "triage", findings=[])
        report["executive_summary"] = "Synthetic incident exercise only: a local service stand-in exposes a version response; no real runtime is patched or provider queried."
        report["coverage"].update(complete=False, reviewed=["demo.py", "fixtures/scenario.json"], deferred=[], limitations=[
            "Known synthetic fixture, not a customer assessment, live incident investigation or vulnerability reproduction.",
            "Advisory is a supplied fictional snapshot, not checked online. Its checked date is historical; service observation date is the exercise date.",
            "The health response is an executed in-process stub. No real package, deployment, credential, provider account or application security boundary is verified.",
            "Background worker is unobserved and stays undetermined after the web-service control. No whole-project all-clear is possible."])
        report["incident_review"] = {
            "advisories": [{key: advisory[key] for key in ("id", "title", "url", "checked_at")}],
            "assets": [
                {"id": "web", "name": "synthetic-web", "environment": "offline teaching stub",
                 "advisory_ids": [advisory["id"]], "status": status, "observed_at": today,
                 "evidence": [f"Executed SyntheticService.health(): {observed}; compared the reported version against the exact lists in scenario.json, not a generic version-range engine."],
                 "proof_gaps": [] if fixed or affected else ["Version is not covered by the supplied advisory lists."]},
                {"id": "worker", "name": scenario["unobserved_service"], "environment": "unobserved teaching asset",
                 "advisory_ids": [advisory["id"]], "status": "undetermined", "observed_at": None,
                 "evidence": [], "proof_gaps": ["No running-service observation or vendor package evidence is available."]}],
            "actions": [
                {"id": "update-web", "asset_id": "web", "description": "Use the fixture's fixed version and recheck the synthetic service's health/version response.",
                 "status": "verified" if fixed else "planned", "checked_at": today if fixed else None,
                 "verification": {"method": "runtime" if fixed else "not_run",
                     "result": "Executed local stub: fixed-version response and legitimate health check passed. This is a synthetic state change, not a real software update." if fixed else "Update control has not run; version matches the fixture's affected list."}},
                {"id": "observe-worker", "asset_id": "worker", "description": "Obtain a sanitized running build observation before deciding applicability.",
                 "status": "blocked", "checked_at": None,
                 "verification": {"method": "not_run", "result": "Worker observation unavailable; no remediation or unaffected conclusion is claimed."}}]}
        cn["validate_report"](report)
        reports[stage] = report
    assert reports["before"]["incident_review"]["assets"][0]["status"] == "potentially_affected"
    assert reports["after"]["incident_review"]["assets"][0]["status"] == "not_affected"
    return reports


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True, help="New directory outside the fixture; never overwrite existing output")
    args = parser.parse_args()
    output = args.output_dir.resolve()
    if output.is_relative_to(Path(__file__).resolve().parent):
        parser.error("choose output outside the incident example")
    reports = demonstrate()
    output.mkdir(parents=True, exist_ok=False, mode=0o700)
    for stage, report in reports.items():
        for suffix, content in (("json", json.dumps(report, indent=2) + "\n"), ("md", cn["render"](report))):
            with (output / f"{stage}.{suffix}").open("x") as stream:
                stream.write(content)
    print("Synthetic incident report: web potentially_affected -> not_affected for the fictional advisory only.")
    print("Update action: planned -> verified in local stub; legitimate health check passed.")
    print("Worker: undetermined -> undetermined; observation action remains blocked.")
    print("No network, secrets, real deployment, breach investigation or general security claim.")
    print(f"Reports saved in {output}")


if __name__ == "__main__":
    main()
