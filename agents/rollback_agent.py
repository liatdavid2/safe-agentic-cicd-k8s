import os
from typing import Any, Dict

import yaml

from .io_utils import read_text, run_cmd, utc_now, write_json, write_text
from .llm_client import MiniGPTClient
from .prompts import ROLLBACK_REASONING_SYSTEM, ROLLBACK_REASONING_USER_TEMPLATE


def load_policy(path: str = "policies/autonomy_policy.yaml") -> Dict[str, Any]:
    content = read_text(path)
    if not content.strip():
        raise RuntimeError(f"Policy file is empty or missing: {path}")
    return yaml.safe_load(content)


def policy_mode(policy: Dict[str, Any], environment: str) -> str:
    return policy.get("rollback", {}).get(environment, {}).get("mode", "approval_required")


def run(namespace: str, deployment: str, environment: str, evidence_file: str, out: str) -> None:
    evidence = read_text(evidence_file)
    if not evidence.strip():
        raise RuntimeError(f"Evidence file is empty or missing: {evidence_file}")

    policy = load_policy()
    client = MiniGPTClient()
    reasoning = client.chat_json(
        ROLLBACK_REASONING_SYSTEM,
        ROLLBACK_REASONING_USER_TEMPLATE.format(policy=yaml.safe_dump(policy), evidence=evidence[:60000]),
    )

    mode = policy_mode(policy, environment)
    approved = os.getenv("APPROVE_PRODUCTION_ROLLBACK", "false").lower() == "true"
    should_execute = bool(reasoning.get("rollback_recommended")) and (
        mode == "auto_allowed" or (mode == "approval_required" and approved)
    )

    kubectl_result = None
    if should_execute:
        undo = run_cmd(["kubectl", "rollout", "undo", f"deployment/{deployment}", "-n", namespace])
        status = run_cmd(["kubectl", "rollout", "status", f"deployment/{deployment}", "-n", namespace, "--timeout=180s"])
        kubectl_result = {"undo": undo, "status": status}

    audit = {
        "timestamp": utc_now(),
        "agent": "rollback_agent",
        "namespace": namespace,
        "deployment": deployment,
        "environment": environment,
        "policy_mode": mode,
        "production_approval_env": approved,
        "llm_reasoning": reasoning,
        "executed": should_execute,
        "kubectl_result": kubectl_result,
    }
    write_json(out, audit)

    md_out = out.rsplit(".", 1)[0] + ".md"
    write_text(
        md_out,
        "# Rollback Audit\n\n"
        f"Executed: {should_execute}\n\n"
        f"Policy mode: {mode}\n\n"
        f"Reason: {reasoning.get('reason', '')}\n",
    )
