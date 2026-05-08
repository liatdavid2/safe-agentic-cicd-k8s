from .io_utils import read_text, write_text
from .llm_client import MiniGPTClient
from .prompts import PR_REVIEW_SYSTEM, PR_REVIEW_USER_TEMPLATE


def render_report(data: dict) -> str:
    lines = [
        "# Agentic PR Review",
        "",
        f"Risk level: {data.get('risk_level', 'unknown')}",
        f"Human approval required: {data.get('human_approval_required', True)}",
        "",
        "## Changed areas",
    ]
    lines += [f"- {item}" for item in data.get("changed_areas", [])]
    lines += ["", "## Possible regressions"]
    lines += [f"- {item}" for item in data.get("possible_regressions", [])]
    lines += ["", "## Suggested tests"]
    lines += [f"- {item}" for item in data.get("suggested_tests", [])]
    lines += ["", "## Security concerns"]
    lines += [f"- {item}" for item in data.get("security_concerns", [])]
    lines += ["", "## Recommendation", "", data.get("recommendation", "No recommendation returned.")]
    return "\n".join(lines) + "\n"


def run(diff_file: str, out: str) -> None:
    diff = read_text(diff_file)
    if not diff.strip():
        raise RuntimeError(f"Diff file is empty or missing: {diff_file}")
    client = MiniGPTClient()
    data = client.chat_json(PR_REVIEW_SYSTEM, PR_REVIEW_USER_TEMPLATE.format(diff=diff[:60000]))
    write_text(out, render_report(data))
