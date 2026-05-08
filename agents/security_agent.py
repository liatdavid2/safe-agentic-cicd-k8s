from pathlib import Path

from .io_utils import read_text, write_text
from .llm_client import MiniGPTClient
from .prompts import SECURITY_SYSTEM, SECURITY_USER_TEMPLATE

DEFAULT_FILES = [
    "services/orders-api/Dockerfile",
    "services/orders-api/requirements.txt",
    "services/orders-api/app/main.py",
    "k8s/orders-deployment.yaml",
    "k8s/orders-service.yaml",
    "policies/autonomy_policy.yaml",
]


def collect_files() -> str:
    parts = []
    for path in DEFAULT_FILES:
        p = Path(path)
        if p.exists():
            parts.append(f"\n--- FILE: {path} ---\n{read_text(path)}")
    if not parts:
        raise RuntimeError("No project files found for security review.")
    return "\n".join(parts)


def render_report(data: dict) -> str:
    lines = [
        "# Agentic Security Review",
        "",
        f"Risk level: {data.get('risk_level', 'unknown')}",
        "",
        "## Summary",
        "",
        data.get("summary", "No summary returned."),
        "",
        "## Findings",
    ]
    for finding in data.get("findings", []):
        lines += [
            f"### {finding.get('title', 'Finding')}",
            f"Severity: {finding.get('severity', 'unknown')}",
            f"Evidence: {finding.get('evidence', '')}",
            f"Recommendation: {finding.get('recommendation', '')}",
            "",
        ]
    lines += ["## Merge blockers"]
    blockers = data.get("merge_blockers", [])
    lines += [f"- {item}" for item in blockers] if blockers else ["- None"]
    return "\n".join(lines) + "\n"


def run(out: str) -> None:
    client = MiniGPTClient()
    files = collect_files()
    data = client.chat_json(SECURITY_SYSTEM, SECURITY_USER_TEMPLATE.format(files=files[:60000]))
    write_text(out, render_report(data))
