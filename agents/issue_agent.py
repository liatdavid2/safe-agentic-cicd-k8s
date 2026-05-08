import os
import re
from typing import Optional

import requests

from .io_utils import read_text, write_text
from .llm_client import MiniGPTClient
from .prompts import ISSUE_SYSTEM


def _extract_title(markdown: str) -> str:
    match = re.search(r"^#\s+(.+)$", markdown, flags=re.MULTILINE)
    if match:
        return match.group(1).strip()[:120]
    return "Agentic DevOps incident report"


def _create_github_issue(title: str, body: str) -> Optional[str]:
    token = os.getenv("GITHUB_TOKEN", "").strip()
    repo = os.getenv("GITHUB_REPOSITORY", "").strip()
    if not token or not repo:
        return None
    response = requests.post(
        f"https://api.github.com/repos/{repo}/issues",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
        },
        json={"title": title, "body": body, "labels": ["incident", "agentic-devops"]},
        timeout=60,
    )
    if response.status_code >= 400:
        raise RuntimeError(f"GitHub issue creation failed: HTTP {response.status_code}: {response.text[:1000]}")
    return response.json().get("html_url")


def run(evidence_file: str, out: str) -> None:
    evidence = read_text(evidence_file)
    if not evidence.strip():
        raise RuntimeError(f"Evidence file is empty or missing: {evidence_file}")
    client = MiniGPTClient()
    issue_md = client.chat(ISSUE_SYSTEM, f"Create a GitHub issue from this incident/RCA:\n\n{evidence[:60000]}")
    title = _extract_title(issue_md)
    url = _create_github_issue(title, issue_md)
    if url:
        issue_md += f"\n\nGitHub issue URL: {url}\n"
    write_text(out, issue_md.strip() + "\n")
