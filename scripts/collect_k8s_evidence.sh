#!/usr/bin/env bash
set -u

NAMESPACE="${1:-agentic-devops}"
DEPLOYMENT="${2:-orders-api}"

echo "# Kubernetes Evidence"
echo "namespace=$NAMESPACE"
echo "deployment=$DEPLOYMENT"
echo

echo "## kubectl get deployment"
kubectl get deployment "$DEPLOYMENT" -n "$NAMESPACE" -o wide || true
echo

echo "## kubectl describe deployment"
kubectl describe deployment "$DEPLOYMENT" -n "$NAMESPACE" || true
echo

echo "## kubectl get pods"
kubectl get pods -n "$NAMESPACE" -o wide || true
echo

echo "## kubectl get events"
kubectl get events -n "$NAMESPACE" --sort-by=.lastTimestamp | tail -50 || true
echo

echo "## kubectl logs deployment"
kubectl logs deployment/"$DEPLOYMENT" -n "$NAMESPACE" --tail=120 || true
echo

echo "## rollout history"
kubectl rollout history deployment/"$DEPLOYMENT" -n "$NAMESPACE" || true
