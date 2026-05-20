# Backend Audit AI v7 — FastAPI + Claude Agent SDK
FROM python:3.12-slim

# System deps untuk pdfplumber, python-docx, pdftotext (poppler),
# plus Node.js 20 untuk Claude Code CLI (transport claude-agent-sdk).
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    poppler-utils \
    libpoppler-cpp-dev \
    curl \
    ca-certificates \
    gnupg \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && rm -rf /var/lib/apt/lists/*

# Install Claude Code CLI globally — required oleh claude-agent-sdk
# (SubprocessCLITransport menjalankan binary `claude` sebagai subprocess).
# CLI akan auto-auth lewat env var ANTHROPIC_API_KEY di runtime.
RUN npm install -g @anthropic-ai/claude-code \
    && claude --version

WORKDIR /app

# Install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY app/ ./app/

# Copy V6 ke /v6 (di-bake ke image agar mandiri).
# V6 ter-embed di backend/v6/ (struktur: scripts/, skills/, templates/, checklists/).
# Layout ini dipakai oleh v6_bridge.py: settings.v6_path / "scripts/{skill}/run_batch.py".
COPY v6/ /v6/

# Data directory untuk penugasan (di-mount sebagai Fly volume di production)
RUN mkdir -p /data
ENV APP_DATA_DIR=/data
ENV APP_V6_PATH=/v6
ENV PYTHONPATH=/app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
