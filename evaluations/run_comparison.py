"""Run matched notebook trials; save sanitized results, never credentials or reasoning.

Usage: python evaluations/run_comparison.py --output evaluations/my-comparison
Requires the root requirements.txt packages plus nbclient and nbformat (Jupyter dependencies).
Executed notebook previews go to a new temporary directory, outside the repository.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import tempfile
from datetime import datetime, timezone

import nbformat
from nbclient import NotebookClient
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
NOTEBOOKS = {
    'honeypot': 'evidence_grounded_honeypot_investigation.ipynb',
    'incident': 'streaming_incident_response_triage_with_gpt_6.ipynb',
}

# Wrap only the public response objects. Never persist response.output, which can
# include reasoning items, or the request headers/credentials.
INSTRUMENT = '''
import time as _clock
from openai.resources.responses.responses import Responses as _Responses
_api_records = []
def _wrap_api(_original):
    def _wrapped(self, *args, **kwargs):
        _start = _clock.perf_counter()
        _record = {"method": _original.__name__, "requested_model": kwargs.get("model")}
        _api_records.append(_record)
        def _capture(_response):
            _record.update({
                "response_id": _response.id,
                "returned_model": _response.model,
                "status": _response.status,
                "elapsed_seconds": round(_clock.perf_counter() - _start, 3),
                "usage": _response.usage.model_dump() if _response.usage else None,
            })
        try:
            _result = _original(self, *args, **kwargs)
            if kwargs.get("stream"):
                def _events():
                    try:
                        for _event in _result:
                            if _event.type == "response.completed":
                                _capture(_event.response)
                            yield _event
                    finally:
                        _result.close()
                return _events()
            _capture(_result)
            return _result
        except Exception as _exc:
            _record["error_type"] = type(_exc).__name__
            raise
    return _wrapped
_Responses.create = _wrap_api(_Responses.create)
_Responses.parse = _wrap_api(_Responses.parse)
'''

EXPORT = '''
import hashlib as _hashlib
import json as _json
import openai as _openai
from IPython.display import display as _display
def _jsonable(_value):
    if hasattr(_value, "model_dump"):
        return _value.model_dump(mode="json")
    return _value
_names = [
    "report", "adversarial_report", "tool_trace", "adversarial_trace",
    "evaluation", "adversarial_evaluation", "fake_id_rejected",
    "EVIDENCE_STORE", "assessment", "commander_update", "stream_metrics",
    "assessment_usage", "gate_result", "timeline",
]
_payload = {name: _jsonable(globals()[name]) for name in _names if name in globals()}
_payload["api_records"] = _api_records
_payload["openai_version"] = _openai.__version__
_payload["input_hashes"] = {}
for _name in ["INVESTIGATION_PROMPT", "REPORT_TEXT_CONFIG", "TOOLS", "EVIDENCE_STORE",
              "TRUSTED_INSTRUCTIONS", "STREAMING_PROMPT", "triage_input"]:
    if _name in globals():
        _payload["input_hashes"][_name] = _hashlib.sha256(
            _json.dumps(globals()[_name], sort_keys=True).encode()).hexdigest()
if "IncidentAssessment" in globals():
    _payload["input_hashes"]["IncidentAssessment"] = _hashlib.sha256(
        _json.dumps(IncidentAssessment.model_json_schema(), sort_keys=True).encode()).hexdigest()
_display({"application/json": _payload}, raw=True)
'''


def run(name, model, trial, output, previews, live):
    path = ROOT / NOTEBOOKS[name]
    notebook = nbformat.read(path, as_version=4)
    source_hash = hashlib.sha256(path.read_bytes()).hexdigest()
    for cell in notebook.cells:
        if cell.cell_type == 'code':
            cell.source = cell.source.replace('MODEL = "gpt-6-astra"', f'MODEL = "{model}"')
            cell.outputs = []
            cell.execution_count = None
    notebook.cells.insert(0, nbformat.v4.new_code_cell(INSTRUMENT))
    notebook.cells.append(nbformat.v4.new_code_cell(EXPORT))
    started = datetime.now(timezone.utc).isoformat()
    print(f'Start {name} {model} trial {trial}', flush=True)
    # Retain failed checks and continue to export the actual output. Never rerun
    # a failing trial until it passes or exclude it from the comparison.
    client = NotebookClient(notebook, timeout=600, kernel_name='python3', allow_errors=True,
                            resources={'metadata': {'path': str(ROOT)}})
    client.execute()
    errors = [
        {'cell': i - 1, 'type': item['ename']}
        for i, cell in enumerate(notebook.cells) if cell.cell_type == 'code'
        for item in cell.outputs if item.output_type == 'error'
    ]
    exported = next((item.data['application/json'] for item in notebook.cells[-1].outputs
                     if item.output_type == 'display_data' and 'application/json' in item.data), {})
    result = {
        'notebook': path.name, 'source_sha256': source_hash, 'model': model,
        'helper_sha256': {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                          for p in ROOT.glob('*_helpers.py')},
        'trial': trial, 'started_at': started, 'live': live, 'errors': errors, **exported,
    }
    label = f'{name}-{model}-{trial}'
    (output / f'{label}.json').write_text(json.dumps(result, indent=2) + '\n')
    nbformat.write(notebook, previews / f'{label}.ipynb')
    print(f'Finished {label}: errors={errors}; checks={exported.get("evaluation")}', flush=True)
    return not errors and bool(exported.get('evaluation'))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--models', nargs='+', default=['gpt-5.6-sol', 'gpt-6-astra'])
    parser.add_argument('--notebooks', nargs='+', choices=NOTEBOOKS, default=list(NOTEBOOKS))
    parser.add_argument('--trials', type=int, default=2)
    parser.add_argument('--offline', action='store_true', help='Incident fixture only; no model comparison.')
    parser.add_argument('--output', type=Path, required=True, help='New directory; existing results are never overwritten.')
    args = parser.parse_args()
    if args.offline and args.notebooks != ['incident']:
        parser.error('--offline requires --notebooks incident')
    if args.trials < 1:
        parser.error('--trials must be positive')
    load_dotenv(ROOT / '.env.local')
    if not args.offline and not os.getenv('OPENAI_API_KEY'):
        parser.error('Set OPENAI_API_KEY or use the ignored .env.local file.')
    os.environ['OPENAI_COOKBOOK_RUN_LIVE'] = '0' if args.offline else '1'
    args.output.mkdir(parents=True, exist_ok=False)
    previews = Path(tempfile.mkdtemp(prefix='security-cookbook-previews-'))
    print(f'Executed notebooks: {previews}', flush=True)
    succeeded = True
    for trial in range(1, args.trials + 1):
        # Reverse the order on alternate trials to reduce simple order bias.
        models = args.models if trial % 2 else list(reversed(args.models))
        for name in args.notebooks:
            for model in models:
                succeeded = run(name, model, trial, args.output, previews, not args.offline) and succeeded
    raise SystemExit(0 if succeeded else 1)
