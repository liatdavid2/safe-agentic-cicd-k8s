import argparse
import os

from . import deployment_agent, issue_agent, pr_review_agent, rca_agent, rollback_agent, security_agent


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="LLM-only DevOps agent runner")
    parser.add_argument("--mode", required=True, choices=[
        "pr_review",
        "security_scan",
        "deploy_check",
        "rca",
        "rollback",
        "issue",
    ])
    parser.add_argument("--diff-file", default="artifacts/pr_diff.diff")
    parser.add_argument("--evidence-file", default="artifacts/deployment_evidence.txt")
    parser.add_argument("--out", default="artifacts/agent_report.md")
    parser.add_argument("--namespace", default=os.getenv("K8S_NAMESPACE", "agentic-devops"))
    parser.add_argument("--deployment", default=os.getenv("K8S_DEPLOYMENT", "orders-api"))
    parser.add_argument("--environment", default=os.getenv("ENVIRONMENT", "dev"))
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.mode == "pr_review":
        pr_review_agent.run(args.diff_file, args.out)
    elif args.mode == "security_scan":
        security_agent.run(args.out)
    elif args.mode == "deploy_check":
        deployment_agent.run(args.evidence_file, args.out)
    elif args.mode == "rca":
        rca_agent.run(args.evidence_file, args.out)
    elif args.mode == "rollback":
        rollback_agent.run(args.namespace, args.deployment, args.environment, args.evidence_file, args.out)
    elif args.mode == "issue":
        issue_agent.run(args.evidence_file, args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
