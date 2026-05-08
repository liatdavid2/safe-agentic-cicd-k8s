#!/usr/bin/env bash
set -euo pipefail

NAMESPACE="${NAMESPACE:-agentic-devops}"
DEPLOYMENT="${DEPLOYMENT:-orders-api}"

kubectl rollout undo deployment/${DEPLOYMENT} -n ${NAMESPACE}
kubectl rollout status deployment/${DEPLOYMENT} -n ${NAMESPACE} --timeout=180s
