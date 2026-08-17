# Security cookbooks for the OpenAI API

Two defensive, hands-on notebooks for building security workflows with GPT-5.6 Sol. Both examples keep telemetry separate from instructions, require traceable evidence, and leave consequential actions to people.

## Cookbooks

### Investigating real honeypot sessions with traceable evidence

[`evidence_grounded_honeypot_investigation.ipynb`](evidence_grounded_honeypot_investigation.ipynb) uses four fixed sessions from the CyberLab Honeynet Dataset. It gives the model two read-only tools, produces a typed investigation report, and checks evidence grounding, redaction, activity coverage, and prompt-injection resistance.

### Streaming incident-response triage with GPT-5.6 Sol

[`streaming_incident_response_triage_with_gpt_5_6_sol.ipynb`](streaming_incident_response_triage_with_gpt_5_6_sol.ipynb) turns a small synthetic alert bundle into a structured assessment and a 120–150-word streamed commander update. Application code checks the evidence and pauses before a simulated containment action.

## Run locally

```bash
git clone https://github.com/hrehcodes/security-cookbooks.git
cd security-cookbooks
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
export OPENAI_API_KEY="your-key"
jupyter lab
```

The incident-response notebook runs with an offline fixture by default. Set `OPENAI_COOKBOOK_RUN_LIVE=1` before starting Jupyter to enable its live API path. The honeypot notebook uses live API calls and downloads a verified public dataset on its first run.

Keep API keys in your environment or an ignored local file such as `.env.local`. Never commit them.

## Scope and safety

These notebooks are defensive teaching examples, not production incident-response systems. The honeypot workflow sanitizes real decoy telemetry and never visits attacker infrastructure, retrieves payloads, or executes captured commands. The incident workflow uses synthetic data and simulated actions only.

The honeypot notebook attributes and links the source dataset and its CC BY 4.0 license inside the notebook.
