"""Recheck saved results against the current notebook without making API calls.

Usage: python evaluations/verify_saved_results.py evaluations/gpt6-2026-09-05
Preserves the original results, including any original notebook assertion failures.
"""
import contextlib
import hashlib
import io
import json
import os
from pathlib import Path
import sys

import nbformat

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
results_dir = Path(sys.argv[1])
results = [json.loads(path.read_text()) for path in sorted(results_dir.glob('*.json'))]
assert len(results) == 8, 'Expected two models x two notebooks x two trials.'
assert len({(r['notebook'], r['model'], r['trial']) for r in results}) == 8

# Execute the incident lesson's offline path, then reuse its real schema and
# evaluator. The saved live outputs are not regenerated or edited.
os.environ['OPENAI_COOKBOOK_RUN_LIVE'] = '0'
incident_path = ROOT / 'streaming_incident_response_triage_with_gpt_6.ipynb'
namespace = {}
with contextlib.redirect_stdout(io.StringIO()):
    for cell in nbformat.read(incident_path, as_version=4).cells:
        if cell.cell_type == 'code':
            exec(compile(cell.source, str(incident_path), 'exec'), namespace)

for notebook_name in {r['notebook'] for r in results}:
    group = [r for r in results if r['notebook'] == notebook_name]
    assert all(r['input_hashes'] == group[0]['input_hashes'] for r in group), 'Inputs differ.'
    assert len({r['source_sha256'] for r in group}) == 1, 'Trial notebook source changed.'
    if notebook_name == incident_path.name:
        for name, expected in group[0]['input_hashes'].items():
            value = (namespace[name].model_json_schema() if name == 'IncidentAssessment'
                     else namespace[name])
            actual = hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()
            assert actual == expected, f'Final notebook input changed: {name}'

rows = []
for result in results:
    assert result['live']
    records = result['api_records']
    assert records and all(r.get('status') == 'completed' for r in records)
    assert all(r['requested_model'] == r['returned_model'] == result['model'] for r in records)
    assert all(r['usage']['input_tokens'] > 0 for r in records)
    row = {'notebook': result['notebook'], 'model': result['model'], 'trial': result['trial'],
           'original_errors': result['errors'], 'original_evaluation': result['evaluation'],
           'api_calls': len(records),
           'api_seconds': round(sum(r['elapsed_seconds'] for r in records), 3),
           'input_tokens': sum(r['usage']['input_tokens'] for r in records),
           'output_tokens': sum(r['usage']['output_tokens'] for r in records),
           'cached_input_tokens': sum(r['usage']['input_tokens_details']['cached_tokens'] for r in records)}
    if 'stream_metrics' in result:
        assessment = namespace['IncidentAssessment'].model_validate(result['assessment'])
        namespace['selected_action'] = next(a for a in assessment.proposed_actions
                                             if a.action_type.value == 'isolate_single_host')
        namespace['RUN_LIVE'] = True
        namespace['assessment_usage'] = result['assessment_usage']
        row['current_evaluation'] = namespace['evaluate_current_case'](
            assessment, result['commander_update'], result['stream_metrics'], result['gate_result'])
        assert row['current_evaluation']['failures'] == (
            ['stream_completion_and_length'] if result['model'] == 'gpt-5.6-sol' and result['trial'] == 1 else []
        )
        row['stream_words'] = result['stream_metrics']['word_count']
        assert namespace['count_words'](result['commander_update']) == row['stream_words']
        row['first_text_seconds'] = result['stream_metrics']['time_to_first_text_seconds']
        row['stream_seconds'] = result['stream_metrics']['total_latency_seconds']
        row['severity'] = assessment.severity.value
        row['confidence'] = assessment.confidence
        row['actions'] = len(assessment.proposed_actions)
    else:
        assert all(result['evaluation'].values())
        assert all(result['adversarial_evaluation'].values()) and result['fake_id_rejected']
        evidence = result['EVIDENCE_STORE']
        assert len(evidence) == 4
        for report_key in ['report', 'adversarial_report']:
            report = result[report_key]
            assert report['priority_order'] == ['921afe11245e', '039a4321a1f6', '274f23140383', 'd40eb242995b']
            for assessment in report['assessments']:
                valid_ids = {e['evidence_id'] for e in evidence[assessment['session_id']]}
                for observation in assessment['observations']:
                    assert observation['evidence_ids'] and set(observation['evidence_ids']) <= valid_ids
        row['current_evaluation'] = result['evaluation']
    rows.append(row)

print(json.dumps({'matched_input_hashes': True, 'returned_models_verified': True,
                  'final_notebook_sha256': {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                                            for p in ROOT.glob('*.ipynb')},
                  'trials': rows}, indent=2))
