"""Offline teaching fixture and usage formatting for the incident cookbook.

This fixture is authored example data, not evidence of a live model response.
Importing this module performs no I/O or API calls.
"""
OFFLINE_ASSESSMENT = {
    "incident_id": "IR-2026-0816-042",
    "severity": "high",
    "confidence": 0.84,
    "executive_summary": "Correlated identity, process, DNS, and proxy evidence suggests a likely user-endpoint compromise requiring urgent validation and scoped containment.",
    "evidence_based_findings": [
        {
            "claim": "A suspicious process chain initiated network activity on FIN-LT-204.",
            "evidence_ids": [
                "E2",
                "E3",
                "E4"
            ]
        },
        {
            "claim": "The user's successful sign-in may be relevant but is not proof of account compromise.",
            "evidence_ids": [
                "E1"
            ]
        }
    ],
    "competing_hypotheses": [
        "A legitimate document automation or administrative script produced the process and network pattern.",
        "The identity anomaly is unrelated to the endpoint activity."
    ],
    "information_gaps": [
        "PowerShell command content and parent document provenance",
        "Domain reputation and historical prevalence",
        "EDR process tree, file writes, and persistence indicators",
        "User confirmation for the sign-in and MFA prompt"
    ],
    "proposed_actions": [
        {
            "action_id": "A1",
            "action_type": "preserve_evidence",
            "action": "Acquire the EDR process tree and volatile triage package from FIN-LT-204.",
            "rationale": "Validate scope while preserving evidence.",
            "evidence_ids": [
                "E2",
                "E3",
                "E4"
            ],
            "urgency": "now",
            "requires_human_approval": True
        },
        {
            "action_id": "A2",
            "action_type": "isolate_single_host",
            "action": "Ask the incident commander to approve scoped network isolation of FIN-LT-204.",
            "rationale": "Limit possible command-and-control while avoiding broad finance disruption.",
            "evidence_ids": [
                "E2",
                "E3",
                "E4"
            ],
            "urgency": "within_15m",
            "requires_human_approval": True
        },
        {
            "action_id": "A3",
            "action_type": "review_identity_session",
            "action": "Validate the sign-in with the user and review identity session telemetry.",
            "rationale": "Determine whether identity containment is warranted.",
            "evidence_ids": [
                "E1"
            ],
            "urgency": "within_15m",
            "requires_human_approval": True
        }
    ],
    "escalation_reason": "Potential endpoint compromise on a finance asset with possible identity involvement."
}

OFFLINE_UPDATE = (
    "Observed: On FIN-LT-204, an Office process started encoded PowerShell [E2]. "
    "Thirty-five seconds later, the host resolved a first-seen domain [E3] and sent 184 KB over TLS [E4]. "
    "A separate successful sign-in from a new ASN used push MFA [E1], but that event does not yet prove the identity and endpoint activity are connected. "
    "Assessment: Endpoint compromise is the leading explanation. "
    "Legitimate document automation remains a plausible alternative until we inspect the command, parent document, and process tree. "
    "Gaps: We still need domain reputation, file and persistence telemetry, and user confirmation of the sign-in. "
    "Next steps, pending human approval: preserve volatile evidence, review the identity session, and consider isolating only FIN-LT-204 if the incident commander accepts the business impact. "
    "No containment has been performed. "
    "Treat the high severity as provisional while those checks are completed. "
).strip()


def summarize_usage(usage) -> dict[str, int]:
    if usage is None:
        return {"input_tokens": 0, "cached_input_tokens": 0, "output_tokens": 0}
    input_details = getattr(usage, "input_tokens_details", None)
    return {
        "input_tokens": int(getattr(usage, "input_tokens", 0) or 0),
        "cached_input_tokens": int(
            getattr(input_details, "cached_tokens", 0) or 0
        ),
        "output_tokens": int(getattr(usage, "output_tokens", 0) or 0),
    }
