# Security cookbooks for the OpenAI API

Two defensive, hands-on notebooks for building security workflows with GPT-6 Astra (`gpt-6-astra`). Both examples keep telemetry separate from instructions, require traceable evidence, and leave consequential actions to people.

## Cookbooks

### Investigating real honeypot sessions with traceable evidence

[`evidence_grounded_honeypot_investigation.ipynb`](evidence_grounded_honeypot_investigation.ipynb) uses four fixed sessions from the CyberLab Honeynet Dataset. It gives the model two read-only tools, produces a typed investigation report, and checks evidence grounding, redaction, activity coverage, and prompt-injection resistance.

### Streaming incident-response triage with GPT-6 Astra

[`streaming_incident_response_triage_with_gpt_6.ipynb`](streaming_incident_response_triage_with_gpt_6.ipynb) turns a small synthetic alert bundle into a structured assessment and a 120–150-word streamed commander update. Application code checks citation IDs and pauses before a simulated containment action. These checks do not replace reading the claims against their evidence.

## Run locally

```bash
git clone https://github.com/hrehcodes/security-cookbooks.git
cd security-cookbooks
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pip install jupyterlab
export OPENAI_API_KEY="your-key"
jupyter lab
```

Use Python 3.12. Keep the companion `honeypot_helpers.py` and `incident_response_helpers.py` files beside their notebooks. The incident-response notebook runs with an offline fixture by default. Set `OPENAI_COOKBOOK_RUN_LIVE=1` before starting Jupyter to enable its live API path. The honeypot notebook uses live API calls and downloads a verified public dataset on its first run. Saved notebook outputs are labeled live examples; rerunning the incident notebook in default mode replaces them with the offline fixture.

Keep API keys in your environment or an ignored local file such as `.env.local`. Never commit them.

## GPT-6 comparison

We ran both notebooks twice with GPT-5.6 Sol and GPT-6 Astra on matching inputs. GPT-6 was more precise about uncertain outcomes in these cases, but was not faster on every workflow. See the [comparison, saved outputs, and reproducible checks](evaluations/GPT6_COMPARISON.md) for the measured results and limitations.

## Scope and safety

These notebooks are defensive teaching examples, not production incident-response systems. The honeypot workflow sanitizes real decoy telemetry and never visits attacker infrastructure, retrieves payloads, or executes captured commands. The incident workflow uses synthetic data and simulated actions only.

The honeypot notebook attributes and links the source dataset and its CC BY 4.0 license inside the notebook.

## Publication draft

The notebooks follow the teaching structure of [Combining security scanners with the Agents SDK](https://developers.openai.com/cookbook/examples/agents_sdk/security_scanners_with_agents_sdk). The [publication review](submission/PUBLICATION_REVIEW.md), [proposed registry entries](submission/registry.entries.yaml), and [PR draft](submission/PR_DRAFT.md) prepare them for OpenAI Cookbook review. They have not been submitted or accepted upstream.

Run the offline regression checks with:

```bash
python -m unittest discover -s tests -v
```
