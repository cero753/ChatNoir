"""Incident verdict consistency and report/export behavior on synthetic evidence."""
import copy
import importlib.util
import json
from pathlib import Path
import runpy
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills/chatnoir/scripts/chatnoir.py"
cn = runpy.run_path(str(SCRIPT))
demo = runpy.run_path(str(ROOT / "examples/incident-review/demo.py"))


class IncidentReviewTests(unittest.TestCase):
    def setUp(self):
        self.reports = demo["demonstrate"]()
        self.report = self.reports["after"]

    def invalid(self, report):
        with self.assertRaises(cn["ChatNoirError"]):
            cn["validate_report"](report)

    def test_before_after_observations_preserve_unknown_worker(self):
        before, after = self.reports["before"], self.report
        self.assertEqual(before["incident_review"]["assets"][0]["status"], "potentially_affected")
        self.assertEqual(after["incident_review"]["assets"][0]["status"], "not_affected")
        self.assertEqual(after["incident_review"]["actions"][0]["status"], "verified")
        for report in (before, after):
            self.assertEqual(report["incident_review"]["assets"][1]["status"], "undetermined")
            self.assertEqual(report["incident_review"]["actions"][1]["status"], "blocked")
            self.assertFalse(report["coverage"]["complete"])
            self.assertEqual(report["findings"], [])

    def test_unobserved_or_gapped_asset_cannot_be_unaffected(self):
        for change in ({"observed_at": None}, {"evidence": []}, {"proof_gaps": ["No running build proof"]}):
            report = copy.deepcopy(self.report)
            report["incident_review"]["assets"][0].update(change)
            self.invalid(report)
        report = copy.deepcopy(self.report)
        report["incident_review"]["assets"][1]["proof_gaps"] = []
        self.invalid(report)
        report = copy.deepcopy(self.report)
        report["coverage"]["complete"] = True
        self.invalid(report)

    def test_reported_completion_is_distinct_from_verified_action(self):
        action = self.report["incident_review"]["actions"][0]
        action["verification"] = {"method": "not_run", "result": "Operator says complete; no independent check."}
        action["status"] = "completed"
        cn["validate_report"](self.report)
        action["status"] = "verified"
        self.invalid(self.report)
        action["verification"]["method"] = "runtime"
        action["checked_at"] = None
        self.invalid(self.report)

    def test_invalid_references_dates_and_extra_secret_fields_rejected(self):
        mutations = [
            lambda x: x["assets"][0].update(advisory_ids=["missing"]),
            lambda x: x["actions"][0].update(asset_id="missing"),
            lambda x: x["advisories"].append(copy.deepcopy(x["advisories"][0])),
            lambda x: x["assets"].append(copy.deepcopy(x["assets"][0])),
            lambda x: x["actions"].append(copy.deepcopy(x["actions"][0])),
            lambda x: x["advisories"][0].update(checked_at="2026-02-30"),
            lambda x: x["advisories"][0].update(url="file:///private-record"),
            lambda x: x["advisories"][0].update(url="https://user:secret@example.invalid"),
            lambda x: x["assets"][0].update(environment_values={"APP_API_KEY": "synthetic-value"}),
            lambda x: x["assets"][0].update(status=[]),
            lambda x: x["actions"][0]["verification"].update(method=[]),
        ]
        for mutate in mutations:
            with self.subTest(mutation=mutate):
                report = copy.deepcopy(self.report)
                mutate(report["incident_review"])
                self.invalid(report)

    def test_markdown_and_sarif_keep_incident_evidence_without_invented_findings(self):
        self.report["executive_summary"] = 'Synthetic summary <img src="file:///no-read.png">'
        before = copy.deepcopy(self.report)
        text = cn["render"](self.report)
        self.assertIn("## Executive summary", text)
        self.assertIn("Synthetic summary", text)
        self.assertNotIn('<img src="file:', text)
        for expected in ("Incident exposure and actions", "potentially", "blocked", "not\u0020observed", "Gap:"):
            if expected == "potentially":
                self.assertIn(expected, cn["render"](self.reports["before"]))
            else:
                self.assertIn(expected, text)
        output = cn["sarif"](self.report)
        self.assertEqual(output["runs"][0]["results"], [])
        self.assertEqual(output["runs"][0]["properties"]["incident_review"], self.report["incident_review"])
        self.assertEqual(self.report, before)

    def test_cli_demo_preserves_existing_output_and_validates_saved_reports(self):
        with tempfile.TemporaryDirectory() as temp:
            out = Path(temp) / "new-reports"
            args = [sys.executable, "-B", str(ROOT / "examples/incident-review/demo.py"), "--output-dir", str(out)]
            first = subprocess.run(args, capture_output=True, text=True, timeout=20)
            self.assertEqual(first.returncode, 0, first.stderr)
            old = (out / "after.json").read_bytes()
            for stage in ("before", "after"):
                report = json.loads((out / f"{stage}.json").read_text())
                cn["validate_report"](report)
            second = subprocess.run(args, capture_output=True, text=True, timeout=20)
            self.assertNotEqual(second.returncode, 0)
            self.assertEqual((out / "after.json").read_bytes(), old)

    @unittest.skipUnless(importlib.util.find_spec("reportlab"), "ReportLab optional")
    def test_pdf_preserves_gaps_and_treats_incident_text_as_literal(self):
        self.report["incident_review"]["assets"][1]["evidence"] = ['<img src="file:///do-not-read.png"/> APP_API_KEY name only']
        with tempfile.TemporaryDirectory() as temp:
            out = Path(temp) / "incident.pdf"
            with patch("reportlab.platypus.paraparser.ParaParser.start_img", side_effect=AssertionError("untrusted image")):
                cn["client_report"](self.report, out, "Synthetic incident exercise", "")
            data = out.read_bytes()
            for expected in (b"Incident exposure and actions", b"undetermined", b"blocked", b"APP_API_KEY", b"do-not-read.png"):
                self.assertIn(expected, data)


if __name__ == "__main__":
    unittest.main()
