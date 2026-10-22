"""PDF delivery behavior, including untrusted report text and portable installs."""
import copy
import hashlib
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
installer = runpy.run_path(str(ROOT / "scripts/install.py"))


class ClientReportContractTests(unittest.TestCase):
    def test_agent_sample_binds_to_reproducible_fixture_sources(self):
        report = json.loads((ROOT / "examples/reports/agent-permissions-reviewed.json").read_text())
        cn["validate_report"](report)
        for item in report["target"]["files"]:
            self.assertEqual(hashlib.sha256((ROOT / item["path"]).read_bytes()).hexdigest(), item["sha256"])
        replay = runpy.run_path(str(ROOT / "examples/reports/replay-agent-permissions.py"))
        self.assertTrue(replay["replay"]()["checks_passed"])

    def test_summary_must_be_text_not_an_unchecked_structure(self):
        report = json.loads((ROOT / "examples/reports/sql-reviewed.json").read_text())
        report["executive_summary"] = {"unverified": "content"}
        with self.assertRaisesRegex(cn["ChatNoirError"], "executive_summary"):
            cn["validate_report"](report)

    def test_invalid_review_is_rejected_before_pdf_code_is_loaded(self):
        with patch("runpy.run_path", side_effect=AssertionError("must validate first")):
            with self.assertRaisesRegex(cn["ChatNoirError"], "unsupported report"):
                cn["client_report"]({}, Path("unused.pdf"), "Example", "")

    def test_missing_optional_dependency_has_actionable_error(self):
        report = json.loads((ROOT / "examples/reports/sql-reviewed.json").read_text())
        with patch("runpy.run_path", side_effect=ImportError("reportlab")):
            with self.assertRaisesRegex(cn["ChatNoirError"], "requires ReportLab"):
                cn["client_report"](report, Path("unused.pdf"), "Example", "")


@unittest.skipUnless(importlib.util.find_spec("reportlab"), "optional ReportLab is not installed")
class ClientReportPdfTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.report = json.loads((ROOT / "examples/reports/sql-reviewed.json").read_text())

    def export(self, report=None, name="review.pdf"):
        out = self.root / name
        cn["client_report"](report or self.report, out, "Example app", "Reviewer")
        return out.read_bytes()

    def test_pdf_preserves_sections_and_mixed_verdicts_without_new_review(self):
        fixed = copy.deepcopy(self.report["findings"][0])
        fixed.update(id="FIXED-1", status="fixed")
        pending = copy.deepcopy(fixed)
        pending.update(id="PENDING-1", status="candidate", severity="critical", proof_gaps=["Runtime check not run"],
                       validation={"method": "not_run", "result": "Not executed"})
        self.report["findings"] += [fixed, pending]
        before = copy.deepcopy(self.report)
        data = self.export()
        self.assertTrue(data.startswith(b"%PDF-"))
        for expected in (b"Executive summary", b"Scope and method", b"Detailed findings", b"Verification and remaining work",
                         b"1 confirmed open", b"1 unresolved", b"1 fixed", b"PENDING-1", b"Not executed"):
            self.assertTrue(expected in data, f"missing PDF text: {expected!r}")
        self.assertEqual(self.report, before)

    def test_report_markup_is_literal_and_cannot_load_an_image(self):
        value = '<img src="file:///must-not-be-read.png"/><a href="https://invalid.test">payload</a>'
        self.report["findings"][0]["evidence"] = [value]
        self.report["findings"][0]["title"] = value
        self.report["executive_summary"] = value
        with patch("reportlab.platypus.paraparser.ParaParser.start_img", side_effect=AssertionError("untrusted image")):
            self.assertTrue(b"must-not-be-read.png" in self.export())

    def test_unresolved_report_is_not_an_all_clear_and_reuses_remediation(self):
        finding = self.report["findings"][0]
        finding.update(status="needs_review", proof_gaps=["Production reachability untested"],
                       remediation="Update ExamplePackage; rerun its integration tests and dependency audit.")
        before = copy.deepcopy(self.report)
        data = self.export()
        for expected in (b"No open vulnerability has been confirmed", b"not an all-clear",
                         b"1 unresolved", b"Next actions", b"Recommended action and verification",
                         b"Update ExamplePackage; rerun its integration tests and dependency audit."):
            self.assertIn(expected, data)
        self.assertNotIn(b"0 confirmed open", data)
        markdown = cn["render"](self.report)
        self.assertIn("## Next actions", markdown)
        self.assertIn("Recommended action and verification", markdown)
        self.assertIn("Update ExamplePackage", markdown)
        self.assertEqual(self.report, before)

    def test_existing_output_and_symlink_are_not_overwritten(self):
        out = self.root / "review.pdf"
        out.write_bytes(b"user content")
        with self.assertRaisesRegex(cn["ChatNoirError"], "already exists"):
            self.export()
        self.assertEqual(out.read_bytes(), b"user content")
        link = self.root / "linked.pdf"
        link.symlink_to(out)
        with self.assertRaisesRegex(cn["ChatNoirError"], "already exists"):
            self.export(name="linked.pdf")
        self.assertEqual(out.read_bytes(), b"user content")

    def test_baseline_empty_export_does_not_claim_a_completed_review(self):
        self.report.update(mode="baseline", findings=[])
        self.report["coverage"].update(complete=False, reviewed=[])
        data = self.export()
        self.assertTrue(b"AUTOMATED BASELINE ONLY" in data)
        self.assertTrue(b"not a" in data and b"completed security assessment" in data)
        self.assertTrue(b"No finding-level verification was supplied" in data)

    def test_long_evidence_paginates(self):
        self.report["findings"][0]["evidence"] = ["Long evidence " * 800]
        data = self.export()
        self.assertTrue(data.rstrip().endswith(b"%%EOF"))
        self.assertGreater(data.count(b"/Type /Page\n"), 3)

    def test_long_next_action_splits_across_pages_without_losing_the_end(self):
        self.report["findings"][0]["remediation"] = (
            "Use parameter binding and verify the authorized query still works. " * 250
            + "End of long remediation."
        )
        data = self.export()
        self.assertTrue(data.rstrip().endswith(b"%%EOF"))
        self.assertIn(b"End of long remediation.", data)
        self.assertGreater(data.count(b"/Type /Page\n"), 3)

    def test_copied_skill_cli_exports_without_repository_imports(self):
        project = self.root / "project"
        project.mkdir()
        dest = installer["install"]("agents", project)
        source = self.root / "review.json"
        raw = json.dumps(self.report)
        source.write_text(raw)
        out = self.root / "client.pdf"
        result = subprocess.run([sys.executable, str(dest / "scripts/chatnoir.py"), "client-report", str(source),
                                 "--project", "Portable review", "--output", str(out)],
                                cwd=self.root, text=True, capture_output=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(json.loads(result.stdout)["review_performed"])
        self.assertTrue(out.read_bytes().startswith(b"%PDF-"))
        self.assertEqual(source.read_text(), raw)
        self.assertEqual(list(project.rglob("*.pdf")), [])


if __name__ == "__main__":
    unittest.main()
