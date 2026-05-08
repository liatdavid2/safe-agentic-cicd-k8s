from .io_utils import read_text, write_text
from .llm_client import MiniGPTClient
from .prompts import DEPLOYMENT_SYSTEM, DEPLOYMENT_USER_TEMPLATE


def render_report(data: dict) -> str:
    lines = [
        "# Deployment Agent Decision",
        "",
        f"Rollout status: {data.get('rollout_status', 'unknown')}",
        f"Recommended next action: {data.get('recommended_next_action', 'manual_review')}",
        f"Human approval required: {data.get('human_approval_required', True)}",
        "",
        "## Likely problem",
        "",
        data.get("likely_problem", "No problem summary returned."),
        "",
        "## Evidence summary",
    ]
    lines += [f"- {item}" for item in data.get("evidence_summary", [])]
    return "\n".join(lines) + "\n"


def run(evidence_file: str, out: str) -> None:
    evidence = read_text(evidence_file)
    if not evidence.strip():
        raise RuntimeError(f"Evidence file is empty or missing: {evidence_file}")
    client = MiniGPTClient()
    data = client.chat_json(DEPLOYMENT_SYSTEM, DEPLOYMENT_USER_TEMPLATE.format(evidence=evidence[:60000]))
    write_text(out, render_report(data))
