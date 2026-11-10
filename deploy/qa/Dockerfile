# Preparation only. Context: approved Git archive locally, or trusted Render
# tracked Git checkout at the exact approved deploy commit. Never ambient files.
FROM python:3.11.14-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
ARG SOURCE_SHA
LABEL org.opencontainers.image.revision=$SOURCE_SHA
WORKDIR /opt/auren
RUN python -c "import os,re; value=os.environ['SOURCE_SHA']; assert re.fullmatch('[0-9a-f]{40}', value); open('.qa-source-sha','w').write(value)"
COPY requirements-lock.txt ./
RUN pip install --no-cache-dir -r requirements-lock.txt \
    && pip install --no-cache-dir --no-deps httpx==0.28.1 httpcore==1.0.9 certifi==2026.2.25
COPY app ./app
COPY data ./data
COPY scripts ./scripts
COPY tools ./tools
COPY docs ./docs
COPY CLAUDE.md ./CLAUDE.md
COPY clients/mobile/src/api/firstPlan.contract.json clients/mobile/src/api/firstPlan.ts ./clients/mobile/src/api/
COPY openspec/changes/science-initial-plan-policy/design.md openspec/changes/science-initial-plan-policy/proposal.md ./openspec/changes/science-initial-plan-policy/
RUN python -m tools.plan_calibration_runtime_bundle /opt/science \
    && python -c "from pathlib import Path; from app.services.plan_v3.packaging import execute_science; execute_science('authorities',{},root=Path('/opt/science'))" \
    && chmod -R a-w /opt/science \
    && useradd --uid 10001 --create-home qa
USER 10001
RUN mkdir -m 0700 /home/qa/.ssh
EXPOSE 8080
STOPSIGNAL SIGTERM
ENTRYPOINT ["python", "-m", "tools.qa_delivery.bootstrap"]
CMD ["--config", "/etc/secrets/qa-config.json", "--activation", "/var/lib/qa/activation.json"]
