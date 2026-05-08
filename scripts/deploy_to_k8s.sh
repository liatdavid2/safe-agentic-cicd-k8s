#!/usr/bin/env bash
set -euo pipefail

NAMESPACE="${NAMESPACE:-agentic-devops}"
DEPLOYMENT="${DEPLOYMENT:-orders-api}"
CONTAINER="${CONTAINER:-orders-api}"
IMAGE="${IMAGE:?IMAGE env var is required}"

kubectl set image deployment/${DEPLOYMENT} ${CONTAINER}=${IMAGE} -n ${NAMESPACE}
kubectl rollout status deployment/${DEPLOYMENT} -n ${NAMESPACE} --timeout=180s
