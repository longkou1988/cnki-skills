"""Offline contract tests: synthetic material and injected transport, never paid API calls."""
import copy
from concurrent.futures import ThreadPoolExecutor
import importlib.util
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import threading
import unittest
from unittest.mock import MagicMock, patch

ROOT = Path(__file__).resolve().parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


jev = load('jev', 'skills/cnki-jev/scripts/decide.py')
wf = load('workflow_jev', 'skills/cnki-resume/scripts/workflow.py')
installer = load('installer_jev', 'scripts/install.py')


class JevTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.task = Path(self.tmp.name) / 'task.sqlite'
        self.cfg = json.loads((ROOT / 'skills/cnki-jev/references/config.example.json').read_text())
        self.cfg.update(enabled=True, mode='assist', allow_abstract_upload=True,
                        input_usd_per_million=.042, budget_usd=1, max_calls=10)
        wf.init(self.task, {'topic': '合成研究', 'query': '合成', 'criteria': self.cfg['criteria']})
        self.db = wf.connect(self.task)
        self.addCleanup(self.db.close)
        self.ids = []
        for n in range(3):
            with self.db:
                result = wf.import_records(self.db, [{'title': '合成论文' + str(n),
                    'url': 'https://example.org/paper-' + str(n), 'retrieved_at': '2026-09-21',
                    'abstract': '本合成示例使用中国企业样本实证检验创新产出。',
                    'private_note': 'DO NOT UPLOAD', 'full_text': 'DO NOT UPLOAD'}])
            self.ids.append(result[0]['id'])
        self.env = patch.dict(os.environ, {'TYPESAFE_API_KEY': 'synthetic-secret-not-real'})
        self.env.start()
        self.addCleanup(self.env.stop)
        self.requests = []

    def response(self, choice='meets', probability=.98):
        probabilities = {k: (probability if k == choice else (1 - probability) / 2) for k in jev.OPTIONS}
        return {'model': 'jev-1.13.0', 'usage': {'input_tokens': 100}, 'answers': {
            k: {'type': 'choice', 'choice': choice, 'probabilities': probabilities, 'confidence': .9}
            for k in self.cfg['questions']}}

    def transport(self, payload, key):
        self.requests.append(copy.deepcopy(payload))
        return self.response()

    def run_decide(self, **kwargs):
        return jev.decide(self.task, self.ids[0], self.cfg, transport=self.transport, **kwargs)

    def test_disabled_and_no_consent_never_call_or_make_sidecar(self):
        self.cfg['enabled'] = False
        self.assertEqual(self.run_decide()['status'], 'disabled')
        self.cfg.update(enabled=True, mode='off')
        self.assertEqual(self.run_decide()['status'], 'disabled')
        self.cfg.update(mode='assist', allow_abstract_upload=False)
        self.assertEqual(self.run_decide()['reason'], 'abstract_upload_not_authorized')
        self.assertEqual(self.requests, [])
        self.assertFalse(Path(str(self.task) + '.jev.sqlite').exists())

    def test_allowlist_payload_atomic_questions_and_read_only_task(self):
        before = self.task.read_bytes()
        result = self.run_decide()
        self.assertEqual(result['candidate'], 'include')
        self.assertEqual(result['route'], 'verify_evidence')
        self.assertTrue(result['requires_review'])
        self.assertEqual(self.task.read_bytes(), before)
        self.assertEqual(set(self.requests[0]['state']), {'title', 'abstract'})
        self.assertNotIn('DO NOT UPLOAD', jev.dump(self.requests))
        self.assertNotIn('decision', result)
        self.assertNotIn('synthetic-secret', Path(str(self.task) + '.jev.sqlite').read_bytes().decode('utf-8', errors='ignore'))

    def test_cached_answer_and_shadow_route(self):
        first = self.run_decide()
        self.cfg['mode'] = 'shadow'
        second = self.run_decide()
        self.assertEqual(second['status'], 'cached')
        self.assertEqual(second['route'], 'baseline')
        self.assertEqual(second['request_key'], first['request_key'])
        self.assertEqual(second['budget']['calls'], 1)
        self.assertEqual(len(self.requests), 1)

    def test_low_probability_and_exclusions_always_review(self):
        raw = self.response('violates')
        self.assertEqual(jev.proposal(raw, self.cfg)['route'], 'review_exclusion')
        raw = self.response('insufficient')
        self.assertEqual(jev.proposal(raw, self.cfg)['candidate'], 'uncertain')
        raw = self.response('meets', .8)
        self.assertEqual(jev.proposal(raw, self.cfg)['candidate'], 'uncertain')
        # High confidence is not used in place of selected-option probability.
        for a in raw['answers'].values():
            a['confidence'] = 1
        self.assertEqual(jev.proposal(raw, self.cfg)['candidate'], 'uncertain')

    def test_budget_and_count_block_before_network(self):
        self.cfg['max_calls'] = 1
        self.run_decide()
        result = jev.decide(self.task, self.ids[1], self.cfg, transport=self.transport)
        self.assertEqual(result['reason'], 'budget_or_call_limit')
        self.assertEqual(len(self.requests), 1)

    def test_zero_budget_and_pause(self):
        self.cfg.update(budget_usd=0, on_failure='pause')
        result = self.run_decide()
        self.assertEqual(result['route'], 'pause')
        self.assertEqual(result['budget']['calls'], 0)
        self.assertEqual(self.requests, [])

    def test_missing_key_does_not_reserve(self):
        with patch.dict(os.environ, {'TYPESAFE_API_KEY': ''}):
            result = self.run_decide()
        self.assertEqual(result['reason'], 'missing_api_key')
        self.assertEqual(result['budget']['calls'], 0)

    def test_timeout_reserved_no_retry_and_explicit_retry(self):
        def fail(payload, key):
            raise TimeoutError('synthetic-secret-not-real')
        first = jev.decide(self.task, self.ids[0], self.cfg, transport=fail)
        self.assertGreater(float(first['budget']['accounted_usd']), 0)
        self.assertEqual(self.run_decide()['reason'], 'previous_request_failed')
        self.assertEqual(len(self.requests), 0)
        last = self.run_decide(retry_failed=True)
        self.assertEqual(last['budget']['calls'], 2)
        self.assertNotIn('synthetic-secret', jev.dump(first))

    def test_crash_preserves_pending_and_does_not_retry(self):
        def crash(payload, key):
            raise KeyboardInterrupt()
        with self.assertRaises(KeyboardInterrupt):
            jev.decide(self.task, self.ids[0], self.cfg, transport=crash)
        self.assertEqual(self.run_decide(retry_failed=True)['reason'], 'previous_request_pending')
        self.assertEqual(self.requests, [])

    def test_response_contract_rejection(self):
        mutations = [lambda r: r['answers'].pop('population'),
                     lambda r: r['answers']['population'].update(choice='invented'),
                     lambda r: r['answers']['population']['probabilities'].update(meets=float('nan')),
                     lambda r: r['answers']['population']['probabilities'].update(meets=.1),
                     lambda r: r['answers']['population'].update(confidence=True),
                     lambda r: r.update(usage={}),
                     lambda r: r.update(model='other')]
        for mutate in mutations:
            raw = self.response()
            mutate(raw)
            with self.assertRaises(ValueError):
                jev.validate_response(raw, self.cfg)
        bad = jev.decide(self.task, self.ids[0], self.cfg, transport=lambda p, k: {})
        self.assertEqual(bad['status'], 'fallback')
        self.assertEqual(bad['budget']['calls'], 1)

    def test_official_http_contract_without_network(self):
        response = MagicMock()
        response.__enter__.return_value.read.return_value = jev.dump(self.response()).encode('utf-8')
        opener = MagicMock()
        opener.open.return_value = response
        payload = jev.payload_for({'title': '合成', 'abstract': '合成摘要'}, self.cfg)
        with patch.object(jev.urllib.request, 'build_opener', return_value=opener) as build:
            raw = jev.request(payload, 'synthetic-secret-not-real')
        req = opener.open.call_args.args[0]
        self.assertEqual(req.full_url, 'https://api.typesafe.ai/v1/systemone')
        self.assertEqual(req.get_method(), 'POST')
        self.assertEqual(json.loads(req.data), payload)
        self.assertEqual(req.get_header('Authorization'), 'Bearer synthetic-secret-not-real')
        self.assertEqual(opener.open.call_args.kwargs['timeout'], 30)
        self.assertIsInstance(build.call_args.args[0], jev.NoRedirect)
        self.assertIsNone(jev.NoRedirect().redirect_request(req, None, 302, '', {}, 'https://example.org'))
        self.assertEqual(jev.validate_response(raw, self.cfg)['model'], 'jev-1.13.0')

    def test_pinned_model_mismatch_rejected(self):
        self.cfg['model'] = 'jev-1.12.0'
        with self.assertRaises(ValueError):
            jev.validate_response(self.response(), self.cfg)

    def test_reported_usage_above_reservation_blocks_further_calls(self):
        self.cfg['budget_usd'] = .01
        raw = self.response()
        raw['usage']['input_tokens'] = 1_000_000
        result = jev.decide(self.task, self.ids[0], self.cfg, transport=lambda p, k: raw)
        self.assertEqual(float(result['budget']['accounted_usd']), .042)
        other = jev.decide(self.task, self.ids[1], self.cfg, transport=self.transport)
        self.assertEqual(other['reason'], 'budget_or_call_limit')
        self.assertEqual(self.requests, [])

    def test_criteria_and_bound_policy_cannot_silently_change(self):
        self.cfg['criteria'] += '新增'
        with self.assertRaises(ValueError):
            self.run_decide()
        self.cfg['criteria'] = self.cfg['criteria'][:-2]
        self.run_decide()
        self.cfg['max_calls'] += 1
        with self.assertRaises(ValueError):
            self.run_decide()
        self.assertEqual(len(self.requests), 1)

    def test_changed_material_invalidates_cache(self):
        self.run_decide()
        row = self.db.execute('SELECT metadata FROM papers WHERE id=?', (self.ids[0],)).fetchone()
        material = json.loads(row[0])
        material['abstract'] += '补充资料'
        with self.db:
            self.db.execute('UPDATE papers SET metadata=? WHERE id=?', (jev.dump(material), self.ids[0]))
        self.assertEqual(self.run_decide()['status'], 'evaluated')
        self.assertEqual(len(self.requests), 2)

    def test_missing_abstract_no_call(self):
        row = self.db.execute('SELECT metadata FROM papers WHERE id=?', (self.ids[0],)).fetchone()
        material = json.loads(row[0])
        material.pop('abstract')
        with self.db:
            self.db.execute('UPDATE papers SET metadata=? WHERE id=?', (jev.dump(material), self.ids[0]))
        self.assertEqual(self.run_decide()['reason'], 'abstract_missing')
        self.assertEqual(self.requests, [])

    def test_concurrent_call_cap(self):
        self.cfg['max_calls'] = 1
        barrier = threading.Barrier(2)
        def run(pid):
            barrier.wait(timeout=5)
            return jev.decide(self.task, pid, self.cfg, transport=self.transport)
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(run, self.ids[:2]))
        self.assertEqual(len(self.requests), 1)
        self.assertEqual(sorted(r['status'] for r in results), ['evaluated', 'fallback'])

    def test_same_request_inflight_is_not_duplicated(self):
        started, finish = threading.Event(), threading.Event()
        def blocked(payload, key):
            started.set()
            if not finish.wait(5):
                raise TimeoutError()
            return self.transport(payload, key)
        with ThreadPoolExecutor(max_workers=1) as pool:
            future = pool.submit(jev.decide, self.task, self.ids[0], self.cfg, False, blocked)
            try:
                self.assertTrue(started.wait(5))
                second = self.run_decide()
                self.assertEqual(second['reason'], 'previous_request_pending')
            finally:
                finish.set()
            self.assertEqual(future.result()['status'], 'evaluated')
        self.assertEqual(len(self.requests), 1)

    def test_evidence_review_provenance_survives_base_export(self):
        result = self.run_decide()
        # A proposal is structurally not a screening record.
        with self.assertRaises(ValueError):
            wf.screen(self.db, self.ids[0], result)
        reviewed = {'decision': 'include', 'reason': '合成示例：逐条件核对摘要',
                    'basis': 'abstract', 'access_level': 'abstract_only',
                    'evidence': '本合成示例使用中国企业样本实证检验创新产出。',
                    'decision_provenance': {'engine': 'cnki-jev', 'request_key': result['request_key'],
                                            'reviewer': 'llm', 'reviewed': True}}
        with self.db:
            wf.screen(self.db, self.ids[0], reviewed)
        output = Path(self.tmp.name) / 'export'
        wf.export(self.db, output)
        snapshot = json.loads((output / 'task-snapshot.json').read_text())
        stored = json.loads(next(p for p in snapshot['papers'] if p['id'] == self.ids[0])['screening'])
        self.assertEqual(stored['decision_provenance'], reviewed['decision_provenance'])
        self.assertEqual(stored['evidence'], reviewed['evidence'])

    def test_invalid_configuration(self):
        for name, val in [('enabled', 'false'), ('budget_usd', -1), ('input_usd_per_million', float('nan')),
                          ('max_calls', True), ('min_probability', 2), ('mode', 'automatic'),
                          ('api_key', 'never-store-keys')]:
            cfg = dict(self.cfg, **{name: val})
            with self.assertRaises(ValueError):
                jev.validate_config(cfg)

    def test_cli_disabled_and_output_collision(self):
        cfg = Path(self.tmp.name) / 'cfg.json'
        self.cfg['enabled'] = False
        cfg.write_text(jev.dump(self.cfg))
        output = Path(self.tmp.name) / 'result.json'
        args = [sys.executable, str(ROOT / 'skills/cnki-jev/scripts/decide.py'), '--task', str(self.task),
                '--id', self.ids[0], '--config', str(cfg), '--output', str(output)]
        first = subprocess.run(args, capture_output=True, text=True)
        self.assertEqual(first.returncode, 0, first.stderr)
        content = output.read_bytes()
        self.assertEqual(json.loads(content)['status'], 'disabled')
        self.assertNotEqual(subprocess.run(args, capture_output=True).returncode, 0)
        self.assertEqual(output.read_bytes(), content)
        self.assertEqual(self.requests, [])


class OptionalInstallTests(unittest.TestCase):
    def test_base_opt_in_and_extension_only(self):
        for target, folder in [('codex', '.agents'), ('claude', '.claude'), ('workbuddy', '.workbuddy')]:
            with self.subTest(target=target), tempfile.TemporaryDirectory() as tmp:
                ext = Path(tmp) / folder / 'skills/cnki-jev'
                with self.assertRaises(ValueError):
                    installer.install(target, tmp, only_jev=True)
                installer.install(target, tmp)
                self.assertFalse(ext.exists())
                self.assertEqual(installer.install(target, tmp, only_jev=True), 1)
                self.assertTrue((ext / 'scripts/decide.py').is_file())
                marker = ext / 'custom-marker'
                marker.write_text('preserve on base upgrade')
                installer.install(target, tmp, upgrade=True)
                self.assertTrue(marker.exists())
                installer.install(target, tmp, upgrade=True, only_jev=True)
                self.assertFalse(marker.exists())
                self.assertTrue(list((Path(tmp) / folder / 'cnki-backups').glob('*/skills/cnki-jev/custom-marker')))

    def test_combined_install_and_dry_run(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(installer.install('codex', tmp, dry_run=True, with_jev=True), 13)
            self.assertFalse((Path(tmp) / '.agents').exists())
            installer.install('codex', tmp, with_jev=True)
            self.assertTrue((Path(tmp) / '.agents/skills/cnki-jev/SKILL.md').is_file())


if __name__ == '__main__':
    unittest.main()
