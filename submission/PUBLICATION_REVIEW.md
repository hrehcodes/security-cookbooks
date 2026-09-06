# OpenAI Cookbook publication review

Prepared September 6, 2026. **Ready for author and maintainer review; not submitted or accepted upstream.** Code and content checks pass. A final visual read in Jupyter/GitHub and the author's sign-off remain open.

## The standard used

The reference is Hunter Reh's [Combining security scanners with the Agents SDK](https://developers.openai.com/cookbook/examples/agents_sdk/security_scanners_with_agents_sdk). Upstream [registry.yaml](https://github.com/openai/openai-cookbook/blob/main/registry.yaml) attributes it to `hreh-oai`; that author already exists in [authors.yaml](https://github.com/openai/openai-cookbook/blob/main/authors.yaml).

We followed its short introduction, linked contents, companion-helper approach, pinned direct dependencies, visible API workflow, saved results, and result-specific explanations. We did not copy its scanner or agent architecture into these different lessons.

## What changed

- Honeypot data-loading and sanitization moved into `honeypot_helpers.py`. Notebook code fell from 590 to 432 lines; the helper remains part of the example, not removed complexity or an undisclosed dependency.
- The incident offline fixture and usage formatting moved into `incident_response_helpers.py`. Notebook code fell from 539 to 452 lines. The model prompts, schemas, calls, and case-specific evaluator remain visible.
- Both notebooks now have linked contents, clearer prerequisites, a direct-dependency version file tested with Python 3.12, and explanations before the main code steps.
- The incident diagram now shows the two independent requests. The approval section explicitly explains the hardcoded `defer`, in-memory record, and lack of real actions.
- Repeated safety and schema explanations were shortened. Conclusions point to concrete observations and practical exercises rather than a second checklist of objectives.
- Fresh live outputs are saved inside both notebooks, with run-mode labels. The incident's default offline fixture is clearly distinguished from those saved model results.

## Validation evidence

A new temporary virtual environment installed `requirements.txt` successfully. Its own Python 3.12 kernel ran both notebooks top to bottom with the already authorized key. Nothing was sent to attacker infrastructure or connected to a production system.

| Check | Result |
| --- | --- |
| Offline regression suite | 7 tests passed, including fake-citation and excessive-length negative controls |
| Honeypot live run | 12/12 case checks; 4/4 displayed synthetic-test checks |
| Incident live run | 10/10 case checks; completed update of 139 words |
| Simulation | Containment deferred; no external action executed |
| Historical comparison | Original eight-trial JSON preserved; saved-result verifier still passes |
| Format and syntax | Both notebooks validate; Python cells and helpers parse |
| Metadata | Two draft registry entries match the current required field shape; author entry exists |
| Local links and credentials | Companion-file/contents links checked; no key-like values found in the intended publication artifacts |
| Render | HTML exports generated; browser visual inspection blocked by local-file URL policy |

The fresh [honeypot result](../evaluations/publication-2026-09-06/honeypot-gpt-6-astra-1.json) and [incident result](../evaluations/publication-2026-09-06/incident-gpt-6-astra-1.json) contain response IDs, returned model names, usage, timings, input hashes, helper hashes, and checks. They are separate from the earlier model comparison. Notebook source hashes in those records precede embedding the outputs; the save step checked that every cell's source exactly matched the executed version.

Manual output review found the claims used in the explanations present in this run: submitted honeypot commands are not described as proven effects; the synthetic timestamp is distinguished from the real session closure; account-to-host linkage and exfiltration remain unproven; containment remains conditional and subject to approval. This is a focused review of the saved outputs, not a general accuracy or safety certification.

## Submission package

Run `python submission/stage_submission.py /path/to/a/new/directory` to stage six content files under the proposed `examples/security/` directory: two notebooks, two helpers, requirements, and offline tests. The script also copies the registry fragment and review notes, and records content checksums. It does not copy `.env.local`, internal evaluation data, or temporary previews.

The [registry fragment](registry.entries.yaml) and [PR draft](PR_DRAFT.md) are ready to adapt on an upstream branch. Paths, slugs, tags, date, and final author approval remain maintainer/author decisions. Apply the fragment to the real upstream registry; it is not a replacement registry file. Do not include this local review note or model-comparison archive as published notebook content by default.

The current [PR template](https://github.com/openai/openai-cookbook/blob/main/.github/pull_request_template.md) asks for registry metadata and self-review of relevance, uniqueness, spelling, clarity, correctness, and completeness. The public [contribution page](https://github.com/openai/openai-cookbook/blob/main/CONTRIBUTING.md) says review is best-effort and does not guarantee acceptance. Its rubric anchor referenced by the template is currently absent; no additional requirements or maintainer score are claimed here.

## Remaining sign-offs

1. Open both notebooks in Jupyter or GitHub and check the final rendered layout. HTML generation and structural checks passed, but automated browser inspection was blocked; no visual sign-off is claimed.
2. Have Hunter read the prose and saved results before attaching his byline. These drafts were AI-assisted; conversational style is not evidence of human authorship.
3. Agree on the upstream paths and slugs, apply metadata, and run upstream validation on the actual PR branch.

These are bounded teaching examples, not production response systems. Fixed-case checks and one new publication run per notebook do not establish general prompt-injection resistance, calibrated confidence, or operational reliability.

## Recheck locally

```bash
python -m unittest discover -s tests -v
python submission/validate_publication.py
python evaluations/verify_saved_results.py evaluations/gpt6-2026-09-05
```

For a new billable run, use `python evaluations/run_comparison.py --models gpt-6-astra --trials 1 --output evaluations/new-publication-run`. That runner preserves failed results and returns nonzero on any notebook error; it does not automatically replace the saved publication outputs.
