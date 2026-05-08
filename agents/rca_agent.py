from .io_utils import read_text, write_text
from .llm_client import MiniGPTClient
from .prompts import RCA_SYSTEM


def run(evidence_file: str, out: str) -> None:
    evidence = read_text(evidence_file)
    if not evidence.strip():
        raise RuntimeError(f"Evidence file is empty or missing: {evidence_file}")
    client = MiniGPTClient()
    report = client.chat(RCA_SYSTEM, f"Analyze this Kubernetes deployment evidence:\n\n{evidence[:60000]}")
    write_text(out, report.strip() + "\n")
