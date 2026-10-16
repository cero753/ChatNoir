"""Behavioral checks for the public CLI, containment boundaries and demonstrations."""
import copy
import importlib.util
import json
import os
from pathlib import Path
import runpy
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills/chatnoir/scripts/chatnoir.py"
spec = importlib.util.spec_from_file_location("chatnoir", SCRIPT)
cn = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cn)
installer = runpy.run_path(str(ROOT / "scripts/install.py"))


class ChatNoirTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name).resolve()

    def tearDown(self):
        self.temp.cleanup()

    def write(self, name, content):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
        return path

    def cmd(self, *args):
        return subprocess.run([sys.executable, str(SCRIPT), *map(str, args)], capture_output=True, text=True, timeout=15)

    def report(self):
        self.write("app.py", "def run(value):\n    return eval(value)\n")
        return cn.baseline(self.root)

    def git(self, *args):
        return subprocess.run(["git", "-C", str(self.root), *args], check=True, capture_output=True).stdout.decode().strip()

    def init_git(self):
        self.git("init", "-b", "main")
        self.git("config", "user.name", "Fixture")
        self.git("config", "user.email", "fixture@example.invalid")
        self.git("config", "commit.gpgsign", "false")

    def commit(self):
        self.git("add", ".")
        self.git("commit", "-m", "fixture")
        return self.git("rev-parse", "HEAD")

    def test_fixture_baseline_distinguishes_parameter_binding(self):
        vulnerable = cn.baseline(ROOT / "examples/sql-injection/vulnerable")
        fixed = cn.baseline(ROOT / "examples/sql-injection/fixed")
        self.assertEqual([f["rule_id"] for f in vulnerable["findings"]], ["CN004"])
        self.assertEqual(fixed["findings"], [])
        self.assertFalse(fixed["coverage"]["complete"])

    def test_real_sqlite_reproduction_and_legitimate_control(self):
        demo = runpy.run_path(str(ROOT / "examples/sql-injection/reproduce.py"))["demonstrate"]()
        self.assertEqual(demo, {"vulnerable": {"attack_rows": 2, "legitimate_rows": 1}, "fixed": {"attack_rows": 0, "legitimate_rows": 1}})

    def test_rules_and_import_aliases(self):
        source = "import subprocess as sp\nfrom pickle import loads as decode\nimport requests\nsp.run(value, shell=True)\ndecode(value)\neval(value)\ncursor.execute(f'SELECT {value}')\nrequests.get(url, verify=False)\n"
        findings = cn.python_candidates("app.py", source)
        self.assertEqual([x["rule_id"] for x in findings], ["CN002", "CN003", "CN001", "CN004", "CN005"])
        self.assertTrue(all(x["status"] == "candidate" and x["severity"] == "unknown" for x in findings))

    def test_safe_controls_do_not_match(self):
        source = "import yaml\nfrom yaml import SafeLoader as SL\nimport subprocess\nimport requests\nyaml.safe_load(value)\nyaml.load(value, Loader=SL)\nsubprocess.run(['echo', value], shell=False)\nrequests.get(url, verify=True)\ncursor.execute('SELECT ?',(value,))\n"
        self.assertEqual(cn.python_candidates("app.py", source), [])

    def test_comments_and_strings_do_not_trigger_python_ast_rules(self):
        self.assertEqual(cn.python_candidates("app.py", "# eval(value)\nx = 'eval(value)'\n"), [])

    def test_unsafe_yaml_defaults_and_positional_loader(self):
        items = cn.python_candidates("app.py", "import yaml\nyaml.load(x)\nyaml.load(x, yaml.Loader)\nyaml.load(x, yaml.SafeLoader)\n")
        self.assertEqual(len(items), 2)

    def test_false_positive_is_a_candidate(self):
        report = cn.baseline(ROOT / "examples/false-positive")
        self.assertEqual(report["findings"][0]["status"], "candidate")
        self.assertEqual(report["findings"][0]["validation"]["method"], "not_run")

    def test_never_executes_scanned_code(self):
        marker = self.root / "executed"
        self.write("app.py", f"from pathlib import Path\nPath({str(marker)!r}).touch()\neval(value)\n")
        self.assertEqual(len(cn.baseline(self.root)["findings"]), 1)
        self.assertFalse(marker.exists())

    def test_secret_file_and_values_not_in_output(self):
        self.write(".env", "SECRET=must-not-appear")
        self.write("app.py", "eval('secret-value-must-not-appear')\n")
        report = cn.baseline(self.root)
        output = json.dumps(report)
        self.assertNotIn("must-not-appear", output)
        self.assertEqual(report["target"]["skipped"][0]["reason"], "credential file excluded")

    def test_symlink_is_skipped(self):
        outside = self.root.parent / (self.root.name + "-outside.py")
        try:
            outside.write_text("eval(secret)\n")
            (self.root / "linked.py").symlink_to(outside)
            report = cn.baseline(self.root)
            self.assertEqual(report["findings"], [])
            self.assertIn("symlink", str(report["target"]["skipped"]))
        finally:
            outside.unlink(missing_ok=True)

    def test_directory_symlink_not_followed(self):
        (self.root / "outside").symlink_to(self.root.parent, target_is_directory=True)
        report = cn.baseline(self.root)
        self.assertEqual(report["target"]["files"], [])

    @unittest.skipUnless(hasattr(os, "mkfifo"), "POSIX only")
    def test_fifo_does_not_hang_or_get_read(self):
        os.mkfifo(self.root / "pipe.py")
        report = cn.baseline(self.root)
        self.assertEqual(report["target"]["skipped"][0]["reason"], "not a regular file")

    def test_binary_size_and_encoding_gaps(self):
        (self.root / "image.py").write_bytes(b"\0binary")
        (self.root / "large.py").write_bytes(b"x" * (cn.MAX_FILE + 1))
        (self.root / "invalid.py").write_bytes(b"\xff")
        report = cn.baseline(self.root)
        self.assertEqual(len(report["target"]["skipped"]), 3)
        self.assertFalse(report["coverage"]["complete"])

    def test_syntax_error_and_other_language_are_deferred(self):
        self.write("broken.py", "def (\n")
        self.write("app.rs", "fn main() {}")
        self.assertEqual(len(cn.baseline(self.root)["coverage"]["deferred"]), 2)

    def test_javascript_lexical_scope_is_explicit(self):
        self.write("app.ts", "// eval(value)\n")
        report = cn.baseline(self.root)
        self.assertEqual(len(report["findings"]), 1)
        self.assertIn("lexical", report["coverage"]["deferred"][0]["reason"])
        self.assertIn("comment", report["findings"][0]["evidence"][0])

    def test_digest_changes_with_content_not_absolute_path(self):
        self.write("app.py", "x=1\n")
        first = cn.collect(self.root)[0]["snapshot_sha256"]
        self.write("app.py", "x=2\n")
        self.assertNotEqual(first, cn.collect(self.root)[0]["snapshot_sha256"])

    def test_git_ignores_untracked_but_keeps_tracked_ignored_files(self):
        self.init_git()
        self.write("tracked.py", "x=1\n")
        self.commit()
        self.write(".gitignore", "*.py\n")
        self.write("ignored.py", "eval(value)\n")
        report = cn.baseline(self.root)
        self.assertIn("tracked.py", report["coverage"]["reviewed"])
        self.assertNotIn("ignored.py", report["coverage"]["reviewed"])
        self.assertTrue(report["target"]["dirty"])

    def test_git_fsmonitor_not_executed(self):
        self.init_git()
        self.write("app.py", "x=1\n")
        self.commit()
        hook = self.write("monitor.sh", "#!/bin/sh\ntouch '" + str(self.root / "executed") + "'\n")
        hook.chmod(0o755)
        self.git("config", "core.fsmonitor", str(hook))
        cn.collect(self.root)
        self.assertFalse((self.root / "executed").exists())

    def test_committed_diff_retains_deleted_file_and_unusual_path(self):
        self.init_git()
        self.write("old\nname.py", "eval(value)\n")
        before = self.commit()
        (self.root / "old\nname.py").unlink()
        self.write("new file.py", "x=1\n")
        after = self.commit()
        result = cn.exact_diff(self.root, before, after)
        self.assertEqual(result["base"], before)
        self.assertEqual(result["head"], after)
        self.assertIn({"status": "D", "path": "old\nname.py"}, result["files"])
        self.assertEqual(len(result["patch_sha256"]), 64)

    def test_diff_rejects_option_injection(self):
        self.init_git()
        with self.assertRaises(cn.ChatNoirError):
            cn.exact_diff(self.root, "--help", "HEAD")

    def test_candidate_cannot_be_promoted_without_evidence(self):
        report = self.report()
        report["findings"][0]["status"] = "confirmed"
        with self.assertRaises(cn.ChatNoirError):
            cn.validate_report(report)

    def test_complete_baseline_rejected(self):
        report = self.report()
        report["coverage"]["complete"] = True
        with self.assertRaises(cn.ChatNoirError):
            cn.validate_report(report)

    def test_report_rejects_inventory_changed_without_rebinding_digest(self):
        report = self.report()
        report["target"]["files"][0]["sha256"] = "0" * 64
        with self.assertRaises(cn.ChatNoirError):
            cn.validate_report(report)

    def test_dismissal_requires_counterevidence(self):
        report = self.report()
        report["findings"][0]["status"] = "dismissed"
        with self.assertRaises(cn.ChatNoirError):
            cn.validate_report(report)
        report["findings"][0]["counterevidence"] = ["All input is a fixed literal in this function."]
        cn.validate_report(report)
        self.assertEqual(cn.sarif(report)["runs"][0]["results"], [])

    def test_duplicate_and_unsafe_locations_rejected(self):
        for mutation in ("duplicate", "traversal", "absolute", "windows", "line"):
            with self.subTest(mutation=mutation):
                report = self.report()
                f = report["findings"][0]
                if mutation == "duplicate":
                    report["findings"].append(copy.deepcopy(f))
                elif mutation == "line":
                    f["line"] = 0
                else:
                    f["path"] = {"traversal": "../secret.py", "absolute": "/etc/passwd", "windows": "C:/private.py"}[mutation]
                with self.assertRaises(cn.ChatNoirError):
                    cn.validate_report(report)

    def test_malformed_gaps_rejected_without_traceback(self):
        report = self.report()
        report["coverage"]["deferred"] = ["bad"]
        saved = self.write("report.json", json.dumps(report))
        result = self.cmd("render", saved)
        self.assertEqual(result.returncode, 2)
        self.assertNotIn("Traceback", result.stderr)

    def test_sarif_leads_are_reviews_not_confirmed_errors(self):
        report = self.report()
        result = cn.sarif(report)["runs"][0]["results"][0]
        self.assertEqual((result["kind"], result["level"]), ("review", "note"))

    def test_sarif_encodes_path_characters(self):
        report = self.report()
        report["findings"][0]["path"] = "app #1.py"
        result = cn.sarif(report)["runs"][0]["results"][0]
        self.assertEqual(result["locations"][0]["physicalLocation"]["artifactLocation"]["uri"], "app%20%231.py")

    def test_markdown_escapes_imported_html_and_links(self):
        report = self.report()
        report["findings"][0]["title"] = '<script>bad</script> [click](https://bad.invalid)'
        output = cn.render(report)
        self.assertNotIn("<script>", output)
        self.assertIn("\\[click\\]", output)

    def test_cli_exit_codes_and_roundtrip(self):
        self.write("app.py", "eval(value)\n")
        self.assertEqual(self.cmd("scan", self.root).returncode, 0)
        result = self.cmd("scan", self.root, "--fail-on-candidates")
        self.assertEqual(result.returncode, 1)
        saved = self.write("result.json", result.stdout)
        self.assertEqual(self.cmd("validate", saved).returncode, 0)
        self.assertIn("ChatNoir", self.cmd("render", saved).stdout)
        self.assertEqual(json.loads(self.cmd("sarif", saved).stdout)["version"], "2.1.0")
        self.assertEqual(self.cmd("scan", self.root / "missing").returncode, 2)

    def test_cli_invalid_json(self):
        path = self.write("bad.json", "{broken")
        result = self.cmd("validate", path)
        self.assertEqual(result.returncode, 2)
        self.assertNotIn("Traceback", result.stderr)

    def test_installs_self_contained_skill_for_each_harness(self):
        for harness in ("codex", "claude", "cursor", "agents"):
            with self.subTest(harness=harness):
                project = self.root / harness
                project.mkdir()
                dest = installer["install"](harness, project)
                self.assertTrue((dest / "SKILL.md").is_file())
                result = subprocess.run([sys.executable, str(dest / "scripts/chatnoir.py"), "scan", str(ROOT / "examples/sql-injection/vulnerable")], capture_output=True, text=True)
                self.assertEqual(result.returncode, 0)
                self.assertEqual(json.loads(result.stdout)["findings"][0]["rule_id"], "CN004")

    def test_installer_refuses_overwrite(self):
        dest = installer["install"]("codex", self.root)
        marker = dest / "SKILL.md"
        marker.write_text("user edits")
        with self.assertRaises(FileExistsError):
            installer["install"]("codex", self.root)
        self.assertEqual(marker.read_text(), "user edits")

    def test_installer_refuses_linked_destination(self):
        (self.root / ".agents").symlink_to(self.root.parent, target_is_directory=True)
        with self.assertRaises(ValueError):
            installer["install"]("codex", self.root)


if __name__ == "__main__":
    unittest.main()
