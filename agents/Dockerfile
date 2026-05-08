FROM python:3.10-slim

WORKDIR /workspace

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl git bash ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY agents/requirements.txt /workspace/agents/requirements.txt
RUN pip install --no-cache-dir -r /workspace/agents/requirements.txt

COPY agents /workspace/agents
COPY policies /workspace/policies
COPY scripts /workspace/scripts
COPY examples /workspace/examples
COPY services /workspace/services
COPY k8s /workspace/k8s

ENV PYTHONPATH=/workspace

CMD ["python", "-m", "agents.agent_runner", "--mode", "security_scan", "--out", "artifacts/security_report.md"]
