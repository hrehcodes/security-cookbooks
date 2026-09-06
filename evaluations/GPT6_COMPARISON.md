# GPT-6 cookbook review

September 5, 2026. **Keep the GPT-6 Astra migration.** On these examples, its outputs were more careful about what the evidence actually proves, and its incident updates stayed shorter. The gain was precision and restraint, not discovery of a different incident or a new attack. This is a small teaching-case comparison, not a general security benchmark.

Publication update, September 6: the notebooks were subsequently reorganized into a shorter walkthrough with companion helpers and freshly saved live outputs. See the [publication review](../submission/PUBLICATION_REVIEW.md). The original comparison JSON below is unchanged; its results describe the September 5 trials, not the later publication run.

## What we ran

Two fresh trials per notebook per model: **eight live notebook executions, 32 completed API calls**. Each honeypot execution includes a normal investigation and a synthetic prompt-injection test. Each incident execution includes a structured assessment and an independently generated streamed update. The incident offline path also passed.

The comparison used `gpt-5.6-sol` and `gpt-6-astra`, with the returned model identifiers verified. Prompts, schemas, tools, and starting evidence were identical across models and trials; saved hashes confirm this. Honeypot reasoning stayed at `medium`; incident reasoning stayed at `low`. Model order was reversed for the second trial. No failed trial was regenerated or discarded, and no model fallback was used. The SDK's default transient-request retry behavior was unchanged.

Before either model ran, we corrected two source issues for both models: the incident's nine-second description contradicted its timestamps and is now 35 seconds; honeypot command summaries now describe submitted commands instead of assuming writes, queries, or deletions succeeded. Those corrections are not counted as GPT-6 improvements.

## Results

| Check or observation | GPT-5.6 Sol | GPT-6 Astra |
| --- | --- | --- |
| Honeypot checks, each trial | 12/12 plus 4/4 synthetic-test checks | 12/12 plus 4/4 synthetic-test checks |
| Incident checks, after correcting the evaluator | 9/10; 10/10 | 10/10; 10/10 |
| Streamed update length | 154; 147 words | 142; 138 words |
| Incident severity | High in both trials | High in both trials |
| Proposed incident actions | 6 in each trial | 4 in each trial |
| Honeypot session priority order | Same in every normal and synthetic report | Same in every normal and synthetic report |

The priority order remained payload attempts, discovery/credential-change attempts, forwarding requests, then failed authentication. Both models rejected the fake evidence ID. All proposed incident actions required approval, and all containment audit records remained deferred simulations.

The first Sol incident trial originally scored **8/10**. One failure was genuine: its update exceeded the 150-word limit. The other was a false positive: the evaluator required the literal word `user` in selected report fields, even though the report clearly described the sign-in's connection to the host as unconfirmed. The final evaluator also recognizes `sign-in`, `identity`, and `account`. Rechecking all four saved incident outputs with the same corrected evaluator changes only that false positive. The original results and assertion failure remain in the saved JSON. This lexical check is still a smoke test, not a semantic judge.

## What actually got better

**Honeypot: fewer claims of unobserved success.** In both Sol normal reports and both synthetic-test reports, an observation said credential-like material was written to a temporary file. Event `EVT-039a4321a1f6-37` only records a submitted command to do that. A general limitations paragraph does not repair that stronger local claim. Astra consistently described a submitted command or attempt and explicitly left the write outcome unknown. It likewise qualified retrieval, execution, deletion, and forwarding outcomes beside the observations themselves. Compare the [first Sol result](gpt6-2026-09-05/honeypot-gpt-5.6-sol-1.json) and [first Astra result](gpt6-2026-09-05/honeypot-gpt-6-astra-1.json), then their [Sol repeat](gpt6-2026-09-05/honeypot-gpt-5.6-sol-2.json) and [Astra repeat](gpt6-2026-09-05/honeypot-gpt-6-astra-2.json).

Astra also identified the synthetic event's 2099 timestamp as distorting the session end time in both adversarial reports and cited the real closure event. Sol noticed the end-time issue in its second adversarial report, so this was more consistent handling here, not a capability unique to Astra. The synthetic fixture is intentionally retained; excluding an injected instruction does not automatically prevent test data from affecting ordinary summaries.

**Incident response: tighter decisions and clearer uncertainty.** Both Astra assessments explicitly distinguish temporal correlation from process attribution and exfiltration. Both retain a benign explanation and the missing account-to-host link. Their four actions focus on preservation, conditional single-host isolation, artifact review, and identity review. Sol proposed six actions, including broader hunting and conditional indicator blocking; those are not inherently wrong, but add material beyond this small lesson's immediate decision.

In Sol's first streamed update, “block the domain” was pending approval but no longer conditional on confirming maliciousness, unlike its own structured report. Astra's two updates kept isolation conditional on further findings and human approval, without adding that premature block proposal. The second Sol update was also restrained; this was not a universal Sol failure. See the [Sol incident trial 1](gpt6-2026-09-05/incident-gpt-5.6-sol-1.json), [trial 2](gpt6-2026-09-05/incident-gpt-5.6-sol-2.json), [Astra trial 1](gpt6-2026-09-05/incident-gpt-6-astra-1.json), and [trial 2](gpt6-2026-09-05/incident-gpt-6-astra-2.json).

**Readability: more focused, not magically human-authored.** Astra's incident outputs are easier to use because they ask for fewer immediate decisions and place caveats next to claims. Both models still use formulaic headings. The notebook explanations remain short and conversational; changing models does not establish human authorship. Astra's more qualified honeypot wording is sometimes longer, and that is useful detail rather than an across-the-board brevity win.

## Latency and token trade-offs

Arithmetic means of two trials. API time is the sum of client-observed completed-request durations, excluding dataset loading, kernel startup, and rendering. Honeypot figures include both investigations; incident figures include assessment plus stream. Output-token counts include reasoning tokens, not just visible prose.

| Metric | Sol | Astra |
| --- | ---: | ---: |
| Honeypot API time | 47.00 s | 58.71 s |
| Honeypot input / output tokens | 18,262.5 / 3,413 | 18,177 / 3,584 |
| Incident API time | 21.56 s | 20.01 s |
| Incident input / output tokens | 1,527 / 1,493 | 1,527 / 1,227 |
| Incident first streamed text | 3.53 s | 1.35 s |
| Incident completed stream | 6.74 s | 5.10 s |

Astra was slower on the honeypot workflow, despite its better wording. The second Astra honeypot trial reported 15,046 cached input tokens; other trials reported zero cached tokens. Tool-call history also changes subsequent inputs, even with identical starting evidence. These are observed timings, not controlled throughput or cost benchmarks. No dollar-cost or general speed claim is warranted.

## Changes and remaining limits

Both notebooks now use `gpt-6-astra`; the incident filename and README links were updated. Unsupported `none` reasoning was removed from the exercise, and the appendix no longer implies this text-streaming example uses the Realtime API. These choices follow the [GPT-6 migration guidance](https://developers.openai.com/api/docs/guides/latest-model) and [model documentation](https://developers.openai.com/api/docs/models/gpt-6-astra). No new framework, action capability, or production-control checklist was added.

**Ready to share as bounded teaching examples, with caveats.** Notebook schema and Python syntax checks pass. The final incident code runs offline and its corrected evaluator was replayed against every saved incident output without new API calls. Only evaluator logic and explanatory markdown changed after the live trials; the final incident input hashes still match. Published-source notebooks have no embedded execution output or keys; the dated JSON files provide the comparison evidence.

Before claiming broader reliability, add diverse benign cases, missing and contradictory evidence, and more repeated trials with independent claim-level review. Two trials cannot establish statistical superiority, calibrated confidence, or general prompt-injection resistance. Astra's incident confidence was 0.78 in both trials versus Sol's 0.86 and 0.82; lower numbers alone are not proof of better calibration. Citation validity is not proof that a claim follows from its evidence. The two independently generated incident outputs can still disagree. None of these runs tested a production system or executed containment.

## Reproduce or inspect

From the repository root, install `requirements.txt` and supply an API key through the environment or ignored `.env.local`:

```bash
# Billable: eight fresh notebook runs. Choose a new output directory.
python evaluations/run_comparison.py --output evaluations/my-comparison

# No API calls: verify this saved comparison against the final incident evaluator.
python evaluations/verify_saved_results.py evaluations/gpt6-2026-09-05
```

The runner saves sanitized reports, tool traces, input hashes, response IDs, returned model names, token counts, errors, and timings. It does not save credentials, raw honeypot commands, or model reasoning text. Executed notebook previews go to a temporary directory. Environment: Python 3.12.2, OpenAI SDK 2.43.0, Pydantic 2.13.4, nbclient 0.10.4, nbformat 5.10.4, ipykernel 6.29.3, python-dotenv 1.2.2, ijson 3.5.1. Future model aliases and dependencies can change outputs.

The honeypot evidence is derived from the [CyberLab Honeynet Dataset](https://doi.org/10.5281/zenodo.3687527) by Urban Sedlar, Matej Kren, Leon Štefanič Južnič, and Mojca Volk, University of Ljubljana, under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). The saved excerpts are sanitized behavioral summaries, not the original capture.
