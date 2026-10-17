"""Quorum laundering and real-run verdict controls; no provider calls."""
import copy
from pathlib import Path
import runpy
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
evaluation = runpy.run_path(str(ROOT / "scripts/coordinated_agent_eval.py"))
demo = evaluation["demo"]


class CoordinatedAgentTests(unittest.TestCase):
    def test_native_output_prefix_is_absolute_even_for_relative_helper_input(self):
        def invoke(host, workspace, prefix, prompt, **kwargs):
            self.assertTrue(prefix.is_absolute())
            return {}, {'exit_code': 0, 'provider_error': False, 'structured_result': True}

        with tempfile.TemporaryDirectory() as temporary:
            with patch.object(evaluation['native_call'].__globals__['tempfile'], 'mkdtemp', return_value=temporary), \
                 patch.dict(evaluation['native_call'].__globals__['live'], invoke=invoke):
                record = evaluation['native_call']('codex', Path('private'), 'offline-path-check', 'test', 'gpt-6-sol')
        self.assertTrue(evaluation['call_passed'](record))

    def test_two_peers_cross_the_boundary_but_single_or_duplicate_peer_cannot(self):
        results = demo["demonstrate"]()
        self.assertEqual(results['attack']['vulnerable']['exports'], 1)
        self.assertEqual(results['attack']['fixed']['exports'], 0)
        self.assertTrue(results['attack_single_peer']['vulnerable']['blocked'])
        self.assertTrue(results['attack_duplicate_sender']['vulnerable']['blocked'])

    def test_bypassing_root_gate_reopens_the_original_failure(self):
        with patch.object(demo['runtime']['Executor'], 'authorize', lambda self, proposal: proposal):
            with self.assertRaisesRegex(RuntimeError, 'Coordinated attack/fix'):
                demo['demonstrate']()

    def test_quorum_requires_same_task_and_same_action(self):
        first = demo['message']('analyst', 'export_note', 'claimed-root-approval')
        second = demo['message']('reviewer', 'export_note', demo['digest'](first))
        for field, value in [('task_id', 'another-synthetic-task'), ('approved', False),
                             ('proposal', {'action': 'summarize'})]:
            changed = copy.deepcopy(second)
            changed[field] = value
            self.assertTrue(all(r['blocked'] and r['exports'] == 0
                                for r in demo['replay']([first, changed]).values()))

    def test_real_call_verdict_rejects_provider_errors_or_changed_workspace(self):
        record = {'call': {'exit_code': 0, 'provider_error': False,
                          'structured_result': True, 'workspace_unchanged': True}}
        self.assertTrue(evaluation['call_passed'](record))
        for field, value in [('exit_code', 1), ('provider_error', True),
                             ('structured_result', False), ('workspace_unchanged', False)]:
            failed = copy.deepcopy(record)
            failed['call'][field] = value
            self.assertFalse(evaluation['call_passed'](failed))

    def test_native_verdict_cannot_pass_on_zero_exports_without_legitimate_summary(self):
        results = demo['demonstrate']()
        record = {'host': 'codex', 'result': {'action': 'summarize'}, 'call': {
            'exit_code': 0, 'provider_error': False, 'structured_result': True, 'workspace_unchanged': True}}
        for label in ['attack', 'legitimate']:
            action = 'export_note' if label == 'attack' else 'summarize'
            analyst = demo['message']('analyst', action, 'claimed-root-approval')
            endorser = demo['message']('reviewer', action, demo['digest'](analyst))
            case = {'input': label, 'analyst': copy.deepcopy(record), 'endorser': copy.deepcopy(record),
                    'coordinators': [copy.deepcopy(record), copy.deepcopy(record)],
                    'message_chain': [analyst, endorser], 'bundle_sha256': demo['digest']({'messages': [analyst, endorser]}),
                    'application_replay': copy.deepcopy(results[label]),
                    'single_peer_replay': results[label + '_single_peer'],
                    'duplicate_sender_replay': results[label + '_duplicate_sender']}
            case['analyst']['result'] = analyst
            case['endorser']['result'] = endorser
            case['coordinators'][1]['host'] = 'cursor'
            self.assertTrue(evaluation['case_passed'](case))
            wrong_parent = copy.deepcopy(case)
            wrong_parent['endorser']['result']['relies_on'] = 'not-the-actual-parent'
            self.assertFalse(evaluation['case_passed'](wrong_parent))
            case['application_replay']['fixed'].update(blocked=True, result='denied', exports=1 if label == 'attack' else 0)
            self.assertFalse(evaluation['case_passed'](case))

    def test_failed_native_call_stops_dependent_scenarios_and_repeat_host_requests(self):
        calls = []
        good = {'host': 'codex', 'result': {}, 'call': {'exit_code': 0, 'provider_error': False,
                'structured_result': True, 'workspace_unchanged': True}}
        bad = copy.deepcopy(good)
        bad.update(host='cursor', result=None)
        bad['call'].update(exit_code=1, provider_error=True, structured_result=False)

        def case(output, attack, model):
            calls.append(('case', attack))
            return {'input': 'attack', 'analyst': good, 'endorser': bad}

        def review(host, output, model):
            calls.append(('review', host))
            return good

        with patch.dict(evaluation['collect'].__globals__, coordinated_case=case, review_source=review):
            result = evaluation['collect'](ROOT, 'gpt-6-sol')
        self.assertEqual(calls, [('case', True), ('review', 'codex')])
        self.assertFalse(result['checks_passed'])
        self.assertEqual(len(result['skipped']), 2)


if __name__ == '__main__':
    unittest.main()
