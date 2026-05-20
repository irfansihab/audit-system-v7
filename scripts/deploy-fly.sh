#!/usr/bin/env bash
# Deployment script untuk Fly.io
# Jalankan dari folder audit-system-v7/

set -euo pipefail

if ! command -v fly &> /dev/null; then
    echo "❌ flyctl belum terinstall. Install dulu: https://fly.io/docs/hands-on/install-flyctl/"
    exit 1
fi

cd "$(dirname "$0")/../backend"

echo "🔍 Memverifikasi V6 sudah ter-embed di backend/v6/..."

# V6 sudah ter-embed di backend/v6/ (tidak lagi di sibling folder audit-system-v4).
# Dockerfile akan COPY v6/ /v6/ langsung saat build.
MISSING=()
for sub in scripts skills templates checklists; do
    if [ ! -d "v6/$sub" ]; then
        MISSING+=("v6/$sub")
    fi
done

if [ "${#MISSING[@]}" -gt 0 ]; then
    echo "❌ Folder berikut tidak ditemukan di backend/:"
    printf '   - %s\n' "${MISSING[@]}"
    echo ""
    echo "V6 harus ter-embed di backend/v6/{scripts,skills,templates,checklists}."
    echo "Lihat panduan setup di README atau memory setup_dev_audit_v7."
    exit 1
fi

# Sanity: pastikan binary entrypoint V6 ada
for script in v6/scripts/reviu-rka-kl/run_batch.py v6/scripts/reviu-pengadaan/run_batch.py; do
    if [ ! -f "$script" ]; then
        echo "⚠️  Peringatan: $script tidak ditemukan. Skill terkait mungkin tidak jalan."
    fi
done

echo "✅ V6 ter-embed: $(ls v6/scripts/ | wc -l | tr -d ' ') item di scripts/, $(ls v6/skills/ | wc -l | tr -d ' ') item di skills/."

# Cek apakah app sudah ada di Fly
if fly status --app audit-ai-v7 &> /dev/null; then
    echo "📤 Deploying ke app audit-ai-v7 yang sudah ada..."
    fly deploy --app audit-ai-v7
else
    echo "🆕 App audit-ai-v7 belum ada. Setup pertama kali:"
    echo ""
    echo "1) fly launch --copy-config --no-deploy --name audit-ai-v7 --region sin"
    echo "2) fly postgres create --name audit-ai-v7-db --region sin --vm-size shared-cpu-1x"
    echo "3) fly postgres attach audit-ai-v7-db --app audit-ai-v7"
    echo "4) fly volumes create audit_data --app audit-ai-v7 --size 3 --region sin"
    echo "5) fly secrets set ANTHROPIC_API_KEY=sk-ant-... --app audit-ai-v7"
    echo "6) fly secrets set APP_SECRET_KEY=\$(openssl rand -hex 32) --app audit-ai-v7"
    echo "7) fly secrets set APP_CORS_ORIGINS=https://audit-ai-v7.vercel.app --app audit-ai-v7"
    echo "8) fly deploy --app audit-ai-v7"
    echo ""
    echo "Setelah deploy pertama berhasil, jalankan script ini lagi untuk redeploy."
fi
