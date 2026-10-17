"""Source leads plus observed synthetic action-boundary failures and controls."""
from pathlib import Path
import ast
import json
import runpy
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
DEMO_PATH = ROOT / "examples/agent-attacks/demo.py"
demo = runpy.run_path(str(DEMO_PATH))
cn = demo["cn"]
runtime = demo["runtime"]


class AgentSecurityTests(unittest.TestCase):
    def candidates(self, source):
        return cn["python_candidates"]("application.py", source)

    def test_all_three_attacks_reproduce_and_fixes_preserve_controls(self):
        result = demo["demonstrate"]()
        self.assertEqual(result["scanner_candidates"]["vulnerable"], ["CN006", "CN007", "CN008"])
        self.assertEqual(result["scanner_candidates"]["fixed"], [])
        for case in result["cases"].values():
            self.assertEqual(case["before"]["exports"], 1)
            self.assertEqual(case["after"]["exports"], 0)
            self.assertTrue(all(c["result"] == "synthetic-summary" for c in case["legitimate"].values()))

    def test_fixed_prompt_denies_export_even_when_model_is_hostile(self):
        app = runpy.run_path(str(ROOT / "examples/agent-attacks/fixed/app.py"))
        result = demo["exercise"](app, "prompt_injection", attack=True, adversarial_model=True)
        self.assertEqual(result, {"exports": 0, "blocked": True, "result": "denied"})

    def test_fixed_tool_output_rejects_malformed_and_unauthorized_proposals(self):
        app = runpy.run_path(str(ROOT / "examples/agent-attacks/fixed/app.py"))
        for text in ["not json", "[]", "null", '{}', '{"action":"export_note"}',
                     '{"action":"summarize","capabilities":["export_note"]}', '{"action":["summarize"]}']:
            with self.subTest(text=text):
                executor = runtime["Executor"]()
                with self.assertRaises((ValueError, PermissionError)):
                    app["run_tool_output"](text, executor)
                self.assertEqual(executor.exports, [])

    def test_fixed_peer_cannot_impersonate_coordinator_or_expand_root_permissions(self):
        app = runpy.run_path(str(ROOT / "examples/agent-attacks/fixed/app.py"))
        for sender in ["researcher", "coordinator", "system"]:
            executor = runtime["Executor"]()
            with self.assertRaises(PermissionError):
                app["run_peer_message"]({"sender": sender, "capabilities": ["*", "export_note"],
                                         "proposal": {"action": "export_note"}}, executor)
            self.assertEqual(executor.allowed_actions, frozenset({"summarize"}))
            self.assertEqual(executor.exports, [])

    def test_demo_fails_when_shared_authorization_gate_is_bypassed(self):
        with patch.object(runtime["Executor"], "authorize", lambda self, proposal: proposal):
            with self.assertRaisesRegex(RuntimeError, "Attack/fix proof failed for tool_output"):
                demo["demonstrate"]()

    def test_privileged_role_dynamic_content_is_lead_with_provenance_gap(self):
        for role in ["system", "developer"]:
            findings = self.candidates(f'def build(snippet):\n    return [{{"role":"{role}","content":snippet}}]\n')
            self.assertEqual([f["rule_id"] for f in findings], ["CN006"])
            self.assertEqual(findings[0]["status"], "candidate")
            self.assertEqual(findings[0]["validation"]["method"], "not_run")
            # Trusted configuration also matches: provenance is intentionally not inferred.
            trusted = self.candidates('def build(trusted_policy):\n    return {"role":"system","content":trusted_policy}\n')
            self.assertEqual(trusted[0]["rule_id"], "CN006")

    def test_static_policy_data_roles_comments_and_strings_do_not_match(self):
        source = '''policy = "Summarize only."
messages = [{"role":"system", "content":policy}, {"role":"user", "content":document}]
# capabilities.update(message["permissions"])
example = 'execute_action(json.loads(tool_output))'
'''
        self.assertEqual(self.candidates(source), [])

    def test_json_dispatch_matches_aliases_local_bindings_and_keyword_arguments(self):
        for call in ["executor.execute_action(proposal)", "dispatch_action(action=proposal)"]:
            source = f'from json import loads as decode\ndef route(text):\n    proposal=decode(text)\n    return {call}\n'
            self.assertEqual([f["rule_id"] for f in self.candidates(source)], ["CN007"])

    def test_validated_proposals_reassignment_and_other_function_bindings_do_not_match(self):
        source = '''import json
def one(text):
    action=json.loads(text)
    action=authorize(action)
    return execute_action(action)
def two(action):
    return execute_action(action)
def three(text):
    action=json.loads(text)
    action={"action":"summarize"}
    return execute_action(action)
'''
        self.assertEqual(self.candidates(source), [])

    def test_permission_merges_match_aliases_union_and_compound_update(self):
        for expression in ['permissions.update(claims)', 'allowed_tools.union(claims)', 'capabilities |= claims']:
            source = f'def route(envelope):\n    claims=envelope["permissions"]\n    {expression}\n'
            self.assertEqual([f["rule_id"] for f in self.candidates(source)], ["CN008"])
        self.assertEqual(self.candidates('data.update(message["description"])\npermissions.intersection(message["permissions"])\n'), [])

    def test_scan_never_executes_fixture_source_or_echoes_payload(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            marker = root / "executed"
            (root / "app.py").write_text(f'from pathlib import Path\nPath({str(marker)!r}).touch()\n'
                'messages=[{"role":"system","content":untrusted}]\n'
                'payload="SYNTHETIC-PAYLOAD-DO-NOT-ECHO"\n')
            report = cn["baseline"](root)
            self.assertFalse(marker.exists())
            self.assertNotIn("SYNTHETIC-PAYLOAD-DO-NOT-ECHO", json.dumps(report))
            self.assertEqual(report["findings"][0]["rule_id"], "CN006")
            cn["validate_report"](report)
            self.assertEqual(cn["sarif"](report)["runs"][0]["results"][0]["kind"], "review")

    def test_cli_json_contains_measured_results(self):
        result = subprocess.run([sys.executable, str(DEMO_PATH), "--json"], check=True,
                                capture_output=True, text=True, timeout=15)
        measured = json.loads(result.stdout)
        self.assertEqual(len(measured["cases"]), 3)
        self.assertTrue(all(len(value) == 64 for value in measured["source_sha256"].values()))

    def test_repeated_unresolved_names_do_not_rescan_all_prior_statements(self):
        for statement in ['messages.append({"role":"system","content":value})',
                          'executor.execute_action(value)', 'capabilities.update(value)']:
            with self.subTest(statement=statement):
                source = 'def route(messages, executor, capabilities, value):\n' + ('    ' + statement + '\n') * 200
                node_count = sum(1 for _ in ast.walk(ast.parse(source)))
                walk = ast.walk
                visited = 0

                def count_walk(node):
                    nonlocal visited
                    for child in walk(node):
                        visited += 1
                        if visited > node_count * 12:
                            self.fail('Repeated local lookup rescanned prior statement trees')
                        yield child

                with patch.object(ast, 'walk', count_walk):
                    self.candidates(source)

    def test_control_flow_and_compound_writes_remain_lookup_barriers(self):
        source = '''import json
def route(text, condition):
    proposal=json.loads(text)
    if condition:
        proposal=authorize(proposal)
    execute_action(proposal)
    proposal=json.loads(text)
    proposal |= {"extra":True}
    execute_action(proposal)
'''
        self.assertEqual(self.candidates(source), [])


if __name__ == "__main__":
    unittest.main()
