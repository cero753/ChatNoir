"""First-review setup uses safe inventory and stays separate from review verdicts."""
import importlib.util
import os
from pathlib import Path
import runpy
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills/chatnoir/scripts/chatnoir.py"
spec = importlib.util.spec_from_file_location("first_review_chatnoir", SCRIPT)
cn = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cn)
install = runpy.run_path(str(ROOT / "scripts/install.py"))["install"]


class FirstReviewTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve() / "app with spaces"
        self.root.mkdir()
        environment = patch.dict(os.environ, {"GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull})
        environment.start()
        self.addCleanup(environment.stop)

    def test_setup_does_not_execute_target_or_inspect_credentials(self):
        marker = self.root / "executed"
        (self.root / "app.py").write_text(f"from pathlib import Path\nPath({str(marker)!r}).touch()\neval(value)\n")
        (self.root / ".env").write_text("SECRET=synthetic-do-not-print\n")
        before = {p.name: p.read_bytes() for p in self.root.iterdir()}
        plan = cn.first_review(self.root, None)
        self.assertEqual(plan["state"], "choose_scope")
        self.assertIsNone(plan["review_request"])
        self.assertFalse(plan["review_performed"])
        self.assertEqual(plan["host_access"], "not_checked")
        self.assertEqual([p["path"] for p in plan["inventory"]["files"]], ["app.py"])
        self.assertEqual(plan["inventory"]["skipped"], [{"path": ".env", "reason": "credential file excluded"}])
        self.assertNotIn("synthetic-do-not-print", cn.render_first_review(plan))
        self.assertEqual(before, {p.name: p.read_bytes() for p in self.root.iterdir()})
        self.assertFalse(marker.exists())

    def test_selected_scopes_preserve_snapshot_and_defer_review(self):
        (self.root / "app.py").write_text("eval(value)\n")
        snapshot = cn.collect(self.root)[0]["snapshot_sha256"]
        for focus in ("auth", "data", "agents"):
            with self.subTest(focus=focus):
                plan = cn.first_review(self.root, focus)
                self.assertEqual(plan["state"], "ready_for_source_review")
                self.assertEqual(plan["focus"], focus)
                self.assertIn(cn.FIRST_REVIEW_SCOPES[focus], plan["review_request"])
                self.assertEqual(plan["inventory"]["snapshot_sha256"], snapshot)
                self.assertFalse(plan["review_performed"])
                self.assertNotIn("findings", plan)

    def test_installed_copy_works_from_an_unrelated_directory(self):
        (self.root / "app.py").write_text("eval(value)\n")
        for harness in ("codex", "claude", "cursor", "agents"):
            with self.subTest(harness=harness):
                project = self.root.parent / harness
                project.mkdir()
                skill = install(harness, project)
                self.assertTrue((skill / "references/first-review.md").is_file())
                result = subprocess.run([sys.executable, str(skill / "scripts/chatnoir.py"),
                                         "first-review", str(self.root), "--focus", "data"],
                                        cwd=self.root.parent, capture_output=True, text=True, timeout=15)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn(str(skill), result.stdout)
                self.assertIn("1 readable files; 0 skipped", result.stdout)
                self.assertFalse((self.root / ".chatnoir").exists())

    def test_invalid_empty_or_incomplete_setup_fails(self):
        for target in (self.root, self.root / "missing"):
            result = subprocess.run([sys.executable, str(SCRIPT), "first-review", str(target),
                                     "--focus", "auth"], capture_output=True, text=True, timeout=15)
            self.assertEqual(result.returncode, 2)
            self.assertEqual(result.stdout, "")
        (self.root / "app.py").write_text("pass\n")
        project = self.root.parent / "incomplete"
        project.mkdir()
        skill = install("agents", project)
        (skill / "references/evidence.md").unlink()
        result = subprocess.run([sys.executable, str(skill / "scripts/chatnoir.py"),
                                 "first-review", str(self.root), "--focus", "agents"],
                                capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode, 2)
        self.assertIn("incomplete skill installation", result.stderr)
        self.assertEqual(result.stdout, "")

    def test_explicit_git_ignored_target_explains_inventory_gap(self):
        subprocess.run(["git", "init", "-q", str(self.root)], check=True, capture_output=True)
        (self.root / ".gitignore").write_text("private/\n")
        ignored = self.root / "private"
        ignored.mkdir()
        (ignored / "app.py").write_text("eval(value)\n")
        result = subprocess.run([sys.executable, str(SCRIPT), "first-review", str(ignored),
                                 "--focus", "data"], capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode, 2)
        self.assertIn("Git ignores", result.stderr)
        self.assertEqual(result.stdout, "")
        self.assertEqual(cn.collect(ignored)[0]["files"], [])


if __name__ == "__main__":
    unittest.main()
