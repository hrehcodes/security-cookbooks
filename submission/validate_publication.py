"""Check the prepared publication artifacts without network access or API calls."""
import ast
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re

import nbformat

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / 'evaluations/publication-2026-09-06'
NOTEBOOKS = {
    'honeypot': 'evidence_grounded_honeypot_investigation.ipynb',
    'incident': 'streaming_incident_response_triage_with_gpt_6.ipynb',
}


class Anchors(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()

    def handle_starttag(self, tag, attrs):
        self.ids.update(value for name, value in attrs if name == 'id')


for label, filename in NOTEBOOKS.items():
    path = ROOT / filename
    notebook = nbformat.read(path, 4)
    nbformat.validate(notebook)
    result = json.loads((RESULTS / f'{label}-gpt-6-astra-1.json').read_text())
    assert result['live'] and not result['errors']
    assert all(r['status'] == 'completed' and r['returned_model'] == 'gpt-6-astra'
               for r in result['api_records'])
    for name, expected in result['helper_sha256'].items():
        assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == expected
    markdown = '\n'.join(c.source for c in notebook.cells if c.cell_type == 'markdown')
    anchors = Anchors()
    anchors.feed(markdown)
    for link in re.findall(r'\]\(([^)]+)\)', markdown):
        if link.startswith('#'):
            assert link[1:] in anchors.ids, (filename, link)
        elif not link.startswith(('https://', 'http://')):
            assert (path.parent / link).is_file(), (filename, link)
    visible = []
    for cell in notebook.cells:
        if cell.cell_type == 'code':
            ast.parse(cell.source)
            assert cell.execution_count is not None
            for output in cell.outputs:
                assert output.output_type != 'error'
                if output.output_type == 'stream':
                    visible.append(output.text)
                else:
                    visible.extend(str(value) for value in output.get('data', {}).values())
    text = ''.join(visible)
    if label == 'honeypot':
        assert all(result['evaluation'].values())
        assert all(result['adversarial_evaluation'].values()) and result['fake_id_rejected']
        assert result['report']['executive_summary'] in text
    else:
        assert result['evaluation']['failures'] == []
        assert result['commander_update'] in text
        assert 120 <= result['stream_metrics']['word_count'] <= 150
        assert result['gate_result']['result'] == 'not executed: defer'
    print(f'{filename}: structure, code, saved live output, checks, links PASS')

for path in [*ROOT.glob('*_helpers.py'), *ROOT.glob('tests/*.py'), *ROOT.glob('submission/*.py')]:
    ast.parse(path.read_text())

# Scan only intended public artifacts, never read or print the credential file.
patterns = [r'sk-(?:proj-)?[A-Za-z0-9_-]{20,}', r'gh[pousr]_[A-Za-z0-9]{20,}',
            r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----']
public_files = [*ROOT.glob('*.ipynb'), *ROOT.glob('*_helpers.py'), *ROOT.glob('submission/*.md'),
                *RESULTS.glob('*.json')]
assert not [p.name for p in public_files if any(re.search(s, p.read_text()) for s in patterns)]
print('Public artifact secret-pattern scan: PASS (not a comprehensive secret audit)')
