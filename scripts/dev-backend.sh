#!/usr/bin/env bash
# Start backend dev server dengan ANTHROPIC_API_KEY ter-export ke environment.
#
# Kenapa perlu: claude-agent-sdk men-spawn `claude` CLI sebagai subprocess.
# CLI butuh auth. Kalau OAuth Claude.ai sudah di-logout (`claude auth logout`),
# CLI HARUS dapat ANTHROPIC_API_KEY dari environment proses uvicorn. pydantic
# memuat .env untuk config app, TAPI tidak meng-export ANTHROPIC_API_KEY ke
# environment untuk subprocess — jadi kita export manual di sini.
#
# Pakai: bash scripts/dev-backend.sh   (Ctrl+C untuk stop)
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT/backend"

if [ ! -f .env ]; then
  echo "❌ backend/.env tidak ada (harus symlink ke ../.env). Lihat README gotcha #1."
  exit 1
fi

# Ambil ANTHROPIC_API_KEY dari .env dan export agar subprocess claude CLI mewarisinya.
KEY="$(grep -E '^ANTHROPIC_API_KEY=' .env | head -1 | cut -d= -f2- | tr -d '[:space:]')"
if [ -z "$KEY" ]; then
  echo "⚠️  ANTHROPIC_API_KEY tidak ditemukan di .env."
  echo "    Agen akan gagal auth kecuali Anda 'claude auth login' (OAuth)."
else
  export ANTHROPIC_API_KEY="$KEY"
  echo "✅ ANTHROPIC_API_KEY ter-export (${KEY:0:14}…). claude CLI akan pakai API key."
fi

# Aktifkan venv bila ada
if [ -f .venv/bin/activate ]; then
  # shellcheck disable=SC1091
  source .venv/bin/activate
fi

exec uvicorn app.main:app --reload --port 8000
