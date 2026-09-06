"""Offline regression checks. No API calls, captured commands, or downloads run."""
import contextlib
import hashlib
import importlib
import io
import os
from pathlib import Path
import re
import sys
import tempfile
import unittest
from unittest.mock import patch

import nbformat

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import honeypot_helpers as honeypot
import incident_response_helpers as incident


class CookbookTests(unittest.TestCase):
    def test_helper_imports_do_not_download(self):
        with patch('urllib.request.urlopen', side_effect=AssertionError('Unexpected download')):
            importlib.reload(honeypot)
            importlib.reload(incident)

    def test_command_summary_does_not_claim_deletion(self):
        event = {'eventid': 'cowrie.command.input', 'input': 'rm temporary-example'}
        self.assertEqual(honeypot.behavioral_summary(event),
                         'Submitted a command to remove temporary or staged artifacts; paths are generalized.')

    def test_command_summary_does_not_claim_write_success(self):
        event = {'eventid': 'cowrie.command.input', 'input': 'example /tmp/up.txt'}
        self.assertTrue(honeypot.behavioral_summary(event).startswith('Submitted a command to write'))

    def test_sanitization_and_ids(self):
        raw = {sid: [{'timestamp': '2026-01-01T00:00:00Z',
                      'eventid': 'cowrie.login.failed', 'username': 'private-user',
                      'password': 'private-password', 'src_ip': '192.0.2.8'}]
               for sid in honeypot.TARGET_SESSION_IDS}
        store = honeypot.build_evidence_store(raw)
        self.assertEqual(store, honeypot.build_evidence_store(raw))
        for sid, events in store.items():
            self.assertEqual(events[0]['evidence_id'], f'EVT-{sid}-01')
            self.assertNotIn('private-user', str(events))
            self.assertNotIn('private-password', str(events))
            self.assertNotIn('192.0.2.8', str(events))
            self.assertFalse(events[0]['synthetic'])

    def test_dataset_identity_rejects_changes(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'test-capture'
            self.assertFalse(honeypot.source_is_valid(path))
            path.write_bytes(b'fixture')
            with patch.object(honeypot, 'EXPECTED_SIZE', 7), patch.object(
                honeypot, 'EXPECTED_MD5', hashlib.md5(b'fixture').hexdigest()
            ):
                self.assertTrue(honeypot.source_is_valid(path))
                path.write_bytes(b'changed')
                self.assertFalse(honeypot.source_is_valid(path))

    def test_offline_fixture_is_short_and_qualified(self):
        words = len(re.findall(r"\b[\w'-]+\b", incident.OFFLINE_UPDATE))
        self.assertTrue(120 <= words <= 150)
        self.assertIn('Thirty-five seconds', incident.OFFLINE_UPDATE)
        self.assertIn('pending human approval', incident.OFFLINE_UPDATE)

    def test_incident_notebook_offline_end_to_end(self):
        namespace = {}
        with patch.dict(os.environ, {'OPENAI_COOKBOOK_RUN_LIVE': '0'}), \
             patch('openai.resources.responses.responses.Responses.create', side_effect=AssertionError('Unexpected API call')), \
             patch('openai.resources.responses.responses.Responses.parse', side_effect=AssertionError('Unexpected API call')), \
             contextlib.redirect_stdout(io.StringIO()):
            notebook = nbformat.read(ROOT / 'streaming_incident_response_triage_with_gpt_6.ipynb', 4)
            for cell in notebook.cells:
                if cell.cell_type == 'code':
                    exec(compile(cell.source, 'incident_notebook', 'exec'), namespace)
        self.assertEqual(namespace['evaluation']['failures'], [])
        self.assertEqual(namespace['gate_result']['result'], 'not executed: defer')
        self.assertEqual(namespace['api_response_id'], 'offline-fixture')
        # Negative controls show that the checks can fail; an all-green fixture
        # alone would not demonstrate their usefulness.
        changed = dict(namespace['stream_metrics'], word_count=151)
        result = namespace['evaluate_current_case'](
            namespace['assessment'], namespace['commander_update'], changed, namespace['gate_result'])
        self.assertIn('stream_completion_and_length', result['failures'])
        report = namespace['assessment'].model_copy(deep=True)
        report.evidence_based_findings[0].evidence_ids = ['E-FAKE-999']
        result = namespace['evaluate_current_case'](
            report, namespace['commander_update'], namespace['stream_metrics'], namespace['gate_result'])
        self.assertIn('evidence_grounding', result['failures'])


if __name__ == '__main__':
    unittest.main()
