## Summary

Add two defensive Responses API walkthroughs:

- Investigate four fixed, sanitized honeypot sessions with two read-only functions and a typed report.
- Produce a structured incident assessment and a short streamed update, then record a simulated decision to defer containment.

Both use `gpt-6-astra`. Companion modules keep dataset-loading and offline-fixture code out of the main teaching flow. The model calls, prompts, report schemas, and case-specific checks remain visible. Each notebook includes saved live outputs and explanations of what those outputs do—and do not—establish.

## Motivation

These examples complement [Combining security scanners with the Agents SDK](https://developers.openai.com/cookbook/examples/agents_sdk/security_scanners_with_agents_sdk). That cookbook reviews static scanner candidates from source files. These examples instead teach evidence-cited telemetry investigation and the distinction between streaming an assessment and authorizing a response. They do not scan applications, execute captured commands, contact attacker infrastructure, or perform containment.

## Review notes

- `examples/security/` and the two slugs in `registry.entries.yaml` are proposed locations, not existing website registrations.
- Use the existing `hreh-oai` author entry. No duplicate author record is needed.
- Keep both helper modules and the example-specific `requirements.txt` beside the notebooks.
- The incident notebook defaults to an offline fixture; its saved live output is labeled separately.
- Keep internal model-comparison artifacts outside the upstream content PR. They are available in the originating repository for review.
- The source dataset is attributed in the honeypot notebook and helper; sanitized adaptations retain the CC BY 4.0 attribution.

## Validation

See `PUBLICATION_REVIEW.md` for the final execution and review results. The offline unit tests include failed-ID and overlong-update negative controls, deterministic redaction checks, and a no-API-call test of the incident notebook.

## Submission checklist

- [ ] Apply the two entries to the upstream `registry.yaml` after the destination paths are agreed.
- [ ] Confirm the final slugs, publication date, tags, and author with the maintainer.
- [ ] Run upstream notebook validation on the actual PR branch.
- [ ] Have the author read the saved outputs and final prose before submission.

The local content review covers relevance, distinctness from the existing scanner example, clarity, code execution, and attribution. These are self-review notes, not maintainer acceptance or a claim of production readiness.
