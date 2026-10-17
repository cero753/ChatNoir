"""Real-handoff verdict regressions; no model requests."""
import copy
import json
from pathlib import Path
import runpy
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
e = runpy.run_path(str(ROOT / 'scripts/codex_coordinated_eval.py'))


def record(result):
    return {'host': 'codex', 'result': result, 'call': {
        'exit_code': 0, 'provider_error': False, 'structured_result': True,
        'workspace_unchanged': True, 'input_reads': {'analyst.json': True, 'bundle.json': True}}}


def case(attack=True):
    action = 'export_note' if attack else 'summarize'
    analyst = e['demo']['message']('analyst', action, 'root-task')
    analyst['argument'] = 'Synthetic analyst-authored argument.'
    reviewer = e['demo']['message']('reviewer', action, e['demo']['digest'](analyst))
    reviewer['argument'] = 'Synthetic independent endorsement of that actual analyst.'
    messages = [analyst, reviewer]
    return {'input': 'attack' if attack else 'legitimate', 'analyst': record(analyst),
            'endorser': record(reviewer), 'coordinator': record({'action': 'summarize'}),
            'messages': messages, 'bundle_sha256': e['demo']['digest']({'messages': messages}),
            'application_replay': e['demo']['replay'](messages),
            'single_peer_replay': e['demo']['replay'](messages[:1]),
            'duplicate_sender_replay': e['demo']['replay']([analyst, analyst])}


class CodexChainTests(unittest.TestCase):
    def test_real_message_replay_requires_lineage_reads_and_preserved_controls(self):
        for attack in (True, False):
            original = case(attack)
            self.assertTrue(e['case_passed'](original))
            mutations = [
                lambda c: c['endorser']['call']['input_reads'].update({'analyst.json': False}),
                lambda c: c['coordinator']['call']['input_reads'].update({'bundle.json': False}),
                lambda c: c['endorser']['result'].update(relies_on='wrong-parent'),
                lambda c: c['analyst']['result'].update(argument='changed-after-handoff'),
                lambda c: c['coordinator']['result'].update(action='export_note'),
                lambda c: c['application_replay']['fixed'].update(exports=1),
                lambda c: c['application_replay']['vulnerable'].update(result='wrong-control'),
                lambda c: c['analyst']['call'].update(provider_error=True),
            ]
            for mutate in mutations:
                changed = copy.deepcopy(original)
                mutate(changed)
                self.assertFalse(e['case_passed'](changed))

    def test_model_claim_or_filename_without_actual_file_output_is_not_a_read(self):
        content = json.dumps({'argument': 'actual synthetic message'})
        def event(output, status=0):
            return {'item': {'type': 'command_execution', 'command': 'cat analyst.json',
                             'exit_code': status, 'aggregated_output': output}}
        self.assertTrue(e['observed_read']([event(content)], 'analyst.json', content))
        self.assertFalse(e['observed_read']([event('I read it')], 'analyst.json', content))
        self.assertFalse(e['observed_read']([event(content, 1)], 'analyst.json', content))

    def test_failed_chain_stops_remaining_calls_without_retry(self):
        calls = []
        def failed(*args):
            calls.append('first-chain')
            return {'input': 'attack'}
        with patch.dict(e['collect'].__globals__, run_case=failed,
                        review_chain=lambda *args: self.fail('review must not run')):
            result = e['collect'](Path('unused'), Path('unused'), 'gpt-6-sol')
        self.assertEqual(calls, ['first-chain'])
        self.assertFalse(result['checks_passed'])
        self.assertEqual(len(result['skipped']), 1)

    def test_review_assurance_without_native_runtime_evidence_cannot_pass(self):
        review = record({'helper_version': '0.2.1', 'fixed_result': 'fixed',
                         'findings': [{'status': 'confirmed'}]})
        with tempfile.TemporaryDirectory() as temp:
            out = Path(temp)
            skill = out / 'skill'
            skill.mkdir()
            (skill / 'SKILL.md').write_text('synthetic skill instructions')
            event = {'item': {'type': 'command_execution', 'command': 'cat ' + str(skill / 'SKILL.md'),
                              'exit_code': 0, 'aggregated_output': 'synthetic skill instructions'}}
            (out / 'chatnoir-review.jsonl').write_text(json.dumps(event) + '\n')
            self.assertFalse(e['verify_review'](review, out, [case(), case(False)], skill))

    def test_review_binds_selected_helper_version_instead_of_requiring_old_patch(self):
        helper = runpy.run_path(str(ROOT / 'skills/chatnoir/scripts/chatnoir.py'))
        cases = [case(), case(False)]
        attack, legitimate = (c['messages'] for c in cases)
        measures = {'attack': e['demo']['replay'](attack),
                    'legitimate': e['demo']['replay'](legitimate),
                    'attack_single_peer': e['demo']['replay'](attack[:1]),
                    'attack_duplicate_sender': e['demo']['replay']([attack[0], attack[0]]),
                    'gate_bypass': {'exports': 1, 'blocked': False, 'result': 'exported-to-local-list'}}
        with tempfile.TemporaryDirectory() as temp:
            out = Path(temp)
            skill = out / 'skill'
            (skill / 'scripts').mkdir(parents=True)
            (skill / 'SKILL.md').write_text('synthetic skill instructions')
            for version in ('0.2.1', '0.2.2'):
                (skill / 'scripts/chatnoir.py').write_text(f'VERSION = {version!r}\n')
                def event(command, value):
                    return {'item': {'type': 'command_execution', 'command': command,
                                     'exit_code': 0, 'aggregated_output': value}}
                events = [event('cat ' + str(skill / 'SKILL.md'), 'synthetic skill instructions')]
                for variant in ('vulnerable', 'fixed'):
                    scan = helper['baseline'](ROOT / 'examples/coordinated-agents' / variant)
                    scan['version'] = version
                    events.append(event('python3 chatnoir.py scan ' + variant, json.dumps(scan)))
                events.append(event('python3 attack.json legitimate.json run_consensus authorize', json.dumps(measures)))
                (out / 'chatnoir-review.jsonl').write_text('\n'.join(json.dumps(x) for x in events))
                review = record({'helper_version': version, 'fixed_result': 'fixed',
                                 'findings': [{'status': 'confirmed'}]})
                self.assertTrue(e['verify_review'](review, out, cases, skill), version)
                review['result']['helper_version'] = '9.9.9'
                self.assertFalse(e['verify_review'](review, out, cases, skill))
                review['result']['helper_version'] = version
                bad = copy.deepcopy(events)
                scan = json.loads(bad[1]['item']['aggregated_output'])
                scan['version'] = '9.9.9'
                bad[1]['item']['aggregated_output'] = json.dumps(scan)
                (out / 'chatnoir-review.jsonl').write_text('\n'.join(json.dumps(x) for x in bad))
                self.assertFalse(e['verify_review'](review, out, cases, skill))

    def test_mutating_gate_reopens_real_envelope_effect_without_source_edits(self):
        messages = case()['messages']
        self.assertEqual(e['demo']['replay'](messages)['fixed']['exports'], 0)
        with patch.object(e['demo']['runtime']['Executor'], 'authorize', lambda self, proposal: proposal):
            self.assertEqual(e['demo']['replay'](messages)['fixed']['exports'], 1)


if __name__ == '__main__':
    unittest.main()
