"""Dataset loading and sanitization for the honeypot cookbook.

No network or file writes occur on import. The notebook explicitly calls the loader.
Source: CyberLab Honeynet Dataset, https://doi.org/10.5281/zenodo.3687527
Urban Sedlar, Matej Kren, Leon Štefanič Južnič, Mojca Volk; CC BY 4.0.
Behavioral summaries are adaptations of the source events, not execution proof.
"""
import gzip
import hashlib
import shutil
import tempfile
import urllib.request
from pathlib import Path
from typing import Any

import ijson

DATASET_URL = (
    "https://zenodo.org/records/3687527/files/"
    "cyberlab_2019-12-26.json.gz?download=1"
)
DATASET_FILENAME = "cyberlab_2019-12-26.json.gz"
EXPECTED_SIZE = 8_031_966
EXPECTED_MD5 = "4dcb5309af7cabc4a6881db0dcf39764"
TARGET_SESSION_IDS = (
    "d40eb242995b",
    "039a4321a1f6",
    "921afe11245e",
    "274f23140383",
)
CACHE_DIR = Path.home() / ".cache" / "openai-cookbook"
SOURCE_PATH = CACHE_DIR / DATASET_FILENAME


def file_md5(path: Path) -> str:
    digest = hashlib.md5()  # Dataset identity check; not a security primitive.
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def source_is_valid(path: Path) -> bool:
    return (
        path.is_file()
        and path.stat().st_size == EXPECTED_SIZE
        and file_md5(path) == EXPECTED_MD5
    )


def download_verified_source() -> Path:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    if source_is_valid(SOURCE_PATH):
        return SOURCE_PATH

    request = urllib.request.Request(
        DATASET_URL,
        headers={"User-Agent": "openai-cookbook-honeypot-example/1.0"},
    )
    temporary_path = None
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            with tempfile.NamedTemporaryFile(
                dir=CACHE_DIR, suffix=".download", delete=False
            ) as temporary:
                temporary_path = Path(temporary.name)
                shutil.copyfileobj(response, temporary)
        if not source_is_valid(temporary_path):
            raise ValueError("Downloaded dataset failed its size or MD5 check.")
        temporary_path.replace(SOURCE_PATH)
    finally:
        if temporary_path is not None and temporary_path.exists():
            temporary_path.unlink()
    return SOURCE_PATH


def select_sessions(path: Path) -> dict[str, list[dict[str, Any]]]:
    selected: dict[str, list[dict[str, Any]]] = {}
    with gzip.open(path, "rb") as compressed:
        for item in ijson.items(compressed, "item"):
            for session_id, events in item.items():
                if session_id in TARGET_SESSION_IDS:
                    selected[session_id] = events
            if len(selected) == len(TARGET_SESSION_IDS):
                break
    if set(selected) != set(TARGET_SESSION_IDS):
        missing = sorted(set(TARGET_SESSION_IDS) - set(selected))
        raise ValueError(f"Expected sessions were not found: {missing}")
    return selected


def behavioral_summary(event: dict[str, Any]) -> str:
    event_type = str(event.get("eventid", "unknown"))
    message = str(event.get("message", "")).lower()
    command = str(event.get("input", "")).lower()
    combined = f"{message} {command}"

    if event_type == "cowrie.session.connect":
        return "An SSH connection opened from a pseudonymized source."
    if event_type in {"cowrie.client.version", "cowrie.client.kex"}:
        return "SSH client metadata was observed; identifying values are omitted."
    if event_type == "cowrie.client.fingerprint":
        return "An SSH client fingerprint was observed; its value is omitted."
    if event_type == "cowrie.login.failed":
        return "Authentication failed; username and password are redacted."
    if event_type == "cowrie.login.success":
        return "Authentication succeeded; username and password are redacted."
    if event_type == "cowrie.command.input":
        if "wget" in combined or "curl" in combined:
            return (
                "Attempted to download scripts, mark them executable, and run them; "
                "all network locations and command arguments are redacted."
            )
        if "passwd" in combined:
            return (
                "Attempted to change an account password; credential material is redacted."
            )
        if "/tmp/up.txt" in combined:
            return (
                "Submitted a command to write credential-like material to a temporary file; contents are redacted."
            )
        if "rm " in combined or "unlink" in combined:
            return "Submitted a command to remove temporary or staged artifacts; paths are generalized."
        discovery_markers = (
            "uname",
            "cpuinfo",
            "lscpu",
            "free ",
            "top",
            " w",
            "whoami",
            "crontab",
        )
        if any(marker in combined for marker in discovery_markers):
            return "Submitted a command to query host hardware, operating-system, or scheduled-task details."
        return "Issued a command; its arguments are omitted."
    if event_type == "cowrie.direct-tcpip.request":
        return (
            "Requested SSH direct-TCP forwarding to a redacted destination; "
            "the destination identifier is omitted."
        )
    if event_type in {"cowrie.log.closed", "cowrie.session.closed"}:
        return "The captured session or command-output stream closed."
    return "A honeypot event was recorded; potentially identifying details are omitted."


def build_evidence_store(
    raw_sessions: dict[str, list[dict[str, Any]]],
) -> dict[str, list[dict[str, Any]]]:
    safe_store: dict[str, list[dict[str, Any]]] = {}
    for session_id in TARGET_SESSION_IDS:
        ordered = sorted(
            raw_sessions[session_id], key=lambda event: str(event.get("timestamp", ""))
        )
        safe_store[session_id] = [
            {
                "evidence_id": f"EVT-{session_id}-{index:02d}",
                "session_id": session_id,
                "timestamp": str(event.get("timestamp", "unknown")),
                "event_type": str(event.get("eventid", "unknown")),
                "details": behavioral_summary(event),
                "synthetic": False,
            }
            for index, event in enumerate(ordered, start=1)
        ]
    return safe_store
