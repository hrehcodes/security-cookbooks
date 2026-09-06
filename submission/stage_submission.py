"""Copy only the intended upstream content to a new staging directory.

Usage: python submission/stage_submission.py /path/to/new-staging-directory
Does not clone, commit, push, modify registry.yaml, or open a pull request.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
FILES = (
    'evidence_grounded_honeypot_investigation.ipynb',
    'streaming_incident_response_triage_with_gpt_6.ipynb',
    'honeypot_helpers.py',
    'incident_response_helpers.py',
    'requirements.txt',
    'tests/test_cookbook_helpers.py',
)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('destination', type=Path)
    args = parser.parse_args()
    args.destination.mkdir(parents=True, exist_ok=False)
    content = args.destination / 'examples' / 'security'
    checksums = {}
    for name in FILES:
        source = ROOT / name
        target = content / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        checksums[str(target.relative_to(args.destination))] = hashlib.sha256(target.read_bytes()).hexdigest()
    for name in ('registry.entries.yaml', 'PR_DRAFT.md', 'PUBLICATION_REVIEW.md'):
        shutil.copy2(ROOT / 'submission' / name, args.destination / name)
    (args.destination / 'manifest.json').write_text(json.dumps(checksums, indent=2) + '\n')
    print(f'Staged {len(FILES)} content files at {content}')
    print('Registry entries are a draft fragment; apply them to upstream registry.yaml during submission.')
