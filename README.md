# Safe Agentic CI/CD for Kubernetes

AI-powered DevOps agents for pull request review, security analysis, Kubernetes deployment checks, root-cause analysis, rollback control, issue generation, and audit logging.

This first version intentionally avoids Argo CD and Argo Rollouts. It uses GitHub Actions, Docker, kubectl, Kubernetes, and EKS.

Important: this project is LLM-only for agent reasoning. There is no rule-based fallback. If the MiniGPT / meinGPT API key, model, or endpoint is missing or invalid, agent commands fail fast instead of silently switching to rules.

## Architecture

```text
+----------------------+        +--------------------------+
| Developer Pull Req   | -----> | GitHub Actions PR CI     |
+----------------------+        +------------+-------------+
                                         |
                                         v
                              +--------------------------+
                              | devops-agent-runner     |
                              | PR Review Agent         |
                              | Security Agent          |
                              +------------+-------------+
                                           |
                                           v
                                  PR report / artifact

+----------------------+        +--------------------------+
| Merge to main        | -----> | GitHub Actions Deploy   |
+----------------------+        +------------+-------------+
                                           |
                                           v
                              +--------------------------+
                              | Build Docker image       |
                              | Push to ECR              |
                              | kubectl set image        |
                              +------------+-------------+
                                           |
                                           v
                              +--------------------------+
                              | EKS / Kubernetes         |
                              | orders-api Deployment    |
                              +------------+-------------+
                                           |
                                           v
                              +--------------------------+
                              | Smoke Test               |
                              | RCA Agent                |
                              | Rollback Agent           |
                              | Issue Agent              |
                              +--------------------------+
```

## Repository structure

```text
safe-agentic-cicd-k8s/
├─ services/orders-api/          FastAPI demo service
├─ agents/                       LLM-only DevOps agents
├─ k8s/                          Kubernetes manifests
├─ policies/                     Autonomy and rollback policies
├─ scripts/                      Smoke test, deploy, rollback, evidence collection
├─ examples/                     Example PR diff for local testing
├─ artifacts/                    Generated reports and audit files
└─ .github/workflows/            GitHub Actions templates
```

## MiniGPT / meinGPT configuration

The code uses an OpenAI-compatible chat-completions API.

The default URLs match the public meinGPT API documentation:

```text
POST https://app.meingpt.com/api/openai/v1/chat/completions
GET  https://app.meingpt.com/api/models/v1
```

Create `.env`:

```bash
cp .env.example .env
```

Edit `.env`:

```env
MINIGPT_API_KEY=sk_meingpt_your_token_here
MINIGPT_MODEL=replace_with_model_id_from_your_account
MINIGPT_CHAT_URL=https://app.meingpt.com/api/openai/v1/chat/completions
MINIGPT_MODELS_URL=https://app.meingpt.com/api/models/v1
MINIGPT_TEMPERATURE=0.1
```

To list available models for your token:

```bash
python -m agents.list_models
```

Then copy one model `id` into `MINIGPT_MODEL`.

## Local Python setup

```bash
python -m venv .venv
. .venv/Scripts/activate  # Windows Git Bash
# or: source .venv/bin/activate

pip install -r services/orders-api/requirements.txt
pip install -r agents/requirements.txt
```

## Run the API locally

```bash
uvicorn services.orders-api.app.main:app --host 0.0.0.0 --port 8000
```

Because the folder name contains a hyphen, the easier local command is:

```bash
cd services/orders-api
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Test:

```bash
curl http://localhost:8000/health
curl http://localhost:8000/orders
python scripts/smoke_test.py --base-url http://localhost:8000
```

## Run tests

```bash
pytest services/orders-api/tests
```

## Build Docker images

```bash
docker build -t orders-api:local -f services/orders-api/Dockerfile .
docker build -t devops-agent-runner:local -f agents/Dockerfile .
```

Run the API container:

```bash
docker run --rm -p 8000:8000 orders-api:local
```

## Run LLM agents locally

All commands require `.env` with `MINIGPT_API_KEY` and `MINIGPT_MODEL`.

PR review:

```bash
python -m agents.agent_runner \
  --mode pr_review \
  --diff-file examples/pr_diff_example.diff \
  --out artifacts/pr_review_report.md
```

Security review:

```bash
python -m agents.agent_runner \
  --mode security_scan \
  --out artifacts/security_report.md
```

Deployment decision from an existing evidence file:

```bash
python -m agents.agent_runner \
  --mode deploy_check \
  --evidence-file examples/deployment_evidence_example.txt \
  --out artifacts/deployment_decision.md
```

RCA from collected evidence:

```bash
python -m agents.agent_runner \
  --mode rca \
  --evidence-file examples/deployment_evidence_example.txt \
  --out artifacts/rca_reports/rca_local.md
```

Generate issue text:

```bash
python -m agents.agent_runner \
  --mode issue \
  --evidence-file artifacts/rca_reports/rca_local.md \
  --out artifacts/issues/incident_issue.md
```

## Run on Minikube

Start Minikube:

```bash
minikube start
```

Build image directly inside Minikube:

```bash
minikube image build -t orders-api:local -f services/orders-api/Dockerfile .
```

Deploy:

```bash
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/orders-deployment.yaml
kubectl apply -f k8s/orders-service.yaml
kubectl rollout status deployment/orders-api -n agentic-devops
```

Port forward:

```bash
kubectl port-forward svc/orders-api 8000:80 -n agentic-devops
```

Smoke test:

```bash
python scripts/smoke_test.py --base-url http://localhost:8000
```

## Simulate a bad deployment

Patch the deployment to enable a simulated bug:

```bash
kubectl set env deployment/orders-api BUG_MODE=error -n agentic-devops
kubectl rollout status deployment/orders-api -n agentic-devops
```

Run smoke test:

```bash
python scripts/smoke_test.py --base-url http://localhost:8000
```

Collect evidence:

```bash
bash scripts/collect_k8s_evidence.sh agentic-devops orders-api > artifacts/deployment_evidence.txt
```

Run RCA:

```bash
python -m agents.agent_runner \
  --mode rca \
  --evidence-file artifacts/deployment_evidence.txt \
  --out artifacts/rca_reports/rca_after_failure.md
```

Rollback in dev/staging according to policy:

```bash
python -m agents.agent_runner \
  --mode rollback \
  --namespace agentic-devops \
  --deployment orders-api \
  --environment dev \
  --evidence-file artifacts/rca_reports/rca_after_failure.md \
  --out artifacts/audit/rollback_audit.json
```

## EKS flow

Create ECR repositories:

```bash
aws ecr create-repository --repository-name orders-api --region us-east-1
aws ecr create-repository --repository-name devops-agent-runner --region us-east-1
```

Create EKS cluster:

```bash
eksctl create cluster \
  --name agentic-devops-demo \
  --region us-east-1 \
  --nodes 2 \
  --node-type t3.medium
```

Update kubeconfig:

```bash
aws eks update-kubeconfig --region us-east-1 --name agentic-devops-demo
kubectl get nodes
```

Build and push API image:

```bash
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
REGION=us-east-1
ECR_URI=$ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/orders-api

aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com

docker build -t orders-api:latest -f services/orders-api/Dockerfile .
docker tag orders-api:latest $ECR_URI:latest
docker push $ECR_URI:latest
```

Deploy to EKS:

```bash
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/orders-service.yaml
kubectl apply -f k8s/orders-deployment.yaml
kubectl set image deployment/orders-api orders-api=$ECR_URI:latest -n agentic-devops
kubectl rollout status deployment/orders-api -n agentic-devops
```

For public demo access, you can temporarily change the service to `LoadBalancer` in `k8s/orders-service.yaml`, then:

```bash
kubectl get svc orders-api -n agentic-devops
```

## GitHub Actions setup

Add repository secrets:

```text
MINIGPT_API_KEY
MINIGPT_MODEL
AWS_ROLE_TO_ASSUME
AWS_REGION
EKS_CLUSTER_NAME
ECR_REPOSITORY
```

The workflows in `.github/workflows/` are templates:

```text
pr-agent.yml       Runs tests, security agent, and PR review agent.
deploy-eks.yml     Builds image, pushes to ECR, deploys to EKS, runs smoke test, RCA, rollback, issue generation.
```

## Safety model

The rollback agent uses two layers:

1. LLM reasoning to summarize the failure and recommend action.
2. Deterministic policy enforcement from `policies/autonomy_policy.yaml` before any kubectl action is executed.

This is intentional. LLMs can reason, but production actions must be bounded by explicit policy.

## Future work

```text
Add Prometheus and Grafana
Add OPA Gatekeeper policies
Add GitHub PR comments through API
Add Slack notification
Add Argo CD as Phase 2
Add Argo Rollouts canary as Phase 3
Add multi-service demo: users-api, orders-api, payments-api
```
