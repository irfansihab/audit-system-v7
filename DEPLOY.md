# Panduan Deployment — Audit AI v7

Backend ke **Fly.io** (Singapore), frontend ke **Vercel**.

## Arsitektur Deployment

```
┌───────────────────────┐         ┌───────────────────────┐
│   Vercel (frontend)   │  HTTPS  │  Fly.io (Singapore)   │
│   Next.js 14          │ ──────► │  FastAPI + Agent SDK  │
│   audit-ai-v7         │  + SSE  │  + claude-code CLI    │
│   .vercel.app         │ ◄────── │  + Fly Postgres        │
└───────────────────────┘         │  + Fly Volume (3 GB)  │
                                  └───────────┬───────────┘
                                              │
                                              ▼
                                  ┌───────────────────────┐
                                  │  Anthropic API         │
                                  │  (Sonnet 4.6 + Haiku)  │
                                  └───────────────────────┘
```

---

## Status Deployment Saat Ini

Per terakhir update README, **backend dan frontend sudah ter-deploy** tetapi **AI belum jalan di production** sampai redeploy dengan Dockerfile baru. Lihat [TODO Production](#todo-production) untuk daftar pekerjaan tersisa.

### Yang sudah benar di production:
- ✅ Backend container `python:3.12-slim` jalan di Fly app `audit-ai-v7`
- ✅ Fly Postgres ter-attach (`DATABASE_URL` auto-injected)
- ✅ Fly Volume `audit_data` ter-mount di `/data`
- ✅ Frontend Vercel `audit-ai-v7.vercel.app` connect ke backend Fly
- ✅ Secrets ter-set: `ANTHROPIC_API_KEY`, `APP_SECRET_KEY`, `APP_CORS_ORIGINS`, `DATABASE_URL`

### Yang perlu redeploy:
- ❌ Dockerfile lama tidak install Node.js + Claude Code CLI → agen crash dengan `Claude Code not found`
- ❌ `requirements.txt` lama pin `claude-agent-sdk==0.1.0` (incompatible dengan CLI modern, `rate_limit_event` MessageParseError)
- ❌ Layout `v6_scripts/` lama vs `v6/` baru — Dockerfile COPY path beda
- ❌ Pipeline V6 hardening (5 fix lokal) belum sampai ke production image

---

## Prasyarat

| Tool | Install |
|------|---------|
| Akun Fly.io | https://fly.io/app/sign-up |
| Akun Vercel | https://vercel.com/signup |
| Anthropic API key | https://console.anthropic.com |
| `flyctl` CLI | `brew install flyctl` |
| `vercel` CLI | `npm install -g vercel` |

---

## Setup Pertama (sekali — kalau app belum pernah ada)

### 1. Login ke kedua platform

```bash
fly auth login        # buka browser, OAuth ke fly.io
vercel login          # pilih GitHub/Email, OAuth ke Vercel
```

### 2. Launch app Fly.io

```bash
cd "/Users/itjen/Downloads/sistem audit v7/backend"

# Launch tanpa deploy (--copy-config pakai fly.toml yang sudah ada)
fly launch --copy-config --no-deploy --name audit-ai-v7 --region sin

# Buat Postgres
fly postgres create --name audit-ai-v7-db --region sin --vm-size shared-cpu-1x
fly postgres attach audit-ai-v7-db --app audit-ai-v7
# Otomatis set DATABASE_URL sebagai secret

# Buat volume untuk data audit
fly volumes create audit_data --app audit-ai-v7 --size 3 --region sin

# Set secrets aplikasi
fly secrets set ANTHROPIC_API_KEY=sk-ant-... --app audit-ai-v7
fly secrets set APP_SECRET_KEY=$(openssl rand -hex 32) --app audit-ai-v7
fly secrets set APP_CORS_ORIGINS=https://audit-ai-v7.vercel.app --app audit-ai-v7
```

Verifikasi secrets ter-set:

```bash
fly secrets list --app audit-ai-v7
# Harus muncul: ANTHROPIC_API_KEY, APP_CORS_ORIGINS, APP_SECRET_KEY, DATABASE_URL
```

### 3. Deploy backend pertama kali

```bash
cd "/Users/itjen/Downloads/sistem audit v7"
bash scripts/deploy-fly.sh
```

`deploy-fly.sh` akan:
1. Verifikasi `backend/v6/{scripts,skills,templates,checklists}` ada (V6 embedded)
2. Cek sanity binary entrypoint V6: `v6/scripts/reviu-rka-kl/run_batch.py` + `v6/scripts/reviu-pengadaan/run_batch.py`
3. Jalankan `fly deploy --app audit-ai-v7`

> ⚠️ Script tidak lagi tergantung pada `audit-system-v4` di parent folder (V6 sudah embedded di `backend/v6/`).

Build duration: **3-7 menit** (pull Python image + apt deps + Node.js 20 + npm install -g @anthropic-ai/claude-code + pip install).

Setelah deploy:

```bash
fly status --app audit-ai-v7
# Tunggu sampai status "running" + health check passing

curl https://audit-ai-v7.fly.dev/health
# Harus return: {"status":"ok"}
```

### 4. Setup frontend di Vercel

```bash
cd "/Users/itjen/Downloads/sistem audit v7/frontend"

# Link project
vercel
# Pilih: Create new, framework Next.js, root directory ./

# Set environment variable
vercel env add NEXT_PUBLIC_API_BASE production
# Masukkan: https://audit-ai-v7.fly.dev

# Deploy production
vercel --prod
```

URL akan otomatis: `https://audit-ai-v7.vercel.app` (atau alias custom).

### 5. Verifikasi end-to-end

| Test | URL | Expected |
|------|-----|----------|
| Backend health | https://audit-ai-v7.fly.dev/health | `{"status":"ok"}` |
| Backend Swagger | https://audit-ai-v7.fly.dev/docs | UI muncul |
| Frontend landing | https://audit-ai-v7.vercel.app | Halaman login |
| Login | (UI) | Email `auditor.at@komdigi.go.id` + NIP 18 digit |
| Run AI di Chat AT | (UI) | Agen merespon tanpa error "Claude Code not found" |

---

## Redeploy (workflow rutin)

### Redeploy Backend

```bash
cd "/Users/itjen/Downloads/sistem audit v7"
bash scripts/deploy-fly.sh
```

Yang dilakukan:
- Verifikasi V6 layout
- `fly deploy` → rebuild image dengan Dockerfile current → rolling restart container
- Secrets, Postgres, volume **tidak terpengaruh** (persisten)
- Down time: ~30 detik (rolling deploy)

### Redeploy Frontend

```bash
cd "/Users/itjen/Downloads/sistem audit v7"
bash scripts/deploy-vercel.sh   # atau cd frontend && vercel --prod
```

---

## Dockerfile (Backend)

Dockerfile saat ini di `backend/Dockerfile`:

```dockerfile
FROM python:3.12-slim

# System deps + Node.js 20 (untuk Claude Code CLI)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential poppler-utils libpoppler-cpp-dev \
    curl ca-certificates gnupg \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && rm -rf /var/lib/apt/lists/*

# Claude Code CLI global — REQUIRED oleh claude-agent-sdk
RUN npm install -g @anthropic-ai/claude-code \
    && claude --version

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app/ ./app/

# V6 embedded di backend/v6/
COPY v6/ /v6/

RUN mkdir -p /data
ENV APP_DATA_DIR=/data APP_V6_PATH=/v6 PYTHONPATH=/app
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Perubahan dari versi awal:
- **+ install Node.js 20** (NodeSource repo)
- **+ install @anthropic-ai/claude-code** global + verifikasi
- **COPY v6/ /v6/** (1 baris) menggantikan 4 baris `COPY v6_scripts/`, dll
- (env `APP_CORS_ORIGINS` di-set lewat fly secrets, tidak di-bake ke image)

---

## Auth Claude Code CLI di Container

Di lokal kita pakai `claude /login` (OAuth interaktif). Di container Fly **tidak ada browser**, jadi auth lewat env var:

- Fly secret `ANTHROPIC_API_KEY=sk-ant-...` di-inject ke container saat boot
- Claude Code CLI otomatis baca `ANTHROPIC_API_KEY` dari env saat pertama dijalankan via SubprocessCLITransport
- Tidak perlu setup `~/.claude/credentials.json` manual

> 💡 Kalau ada error auth di production, cek `fly logs --app audit-ai-v7 | grep -i claude` untuk pesan dari CLI.

---

## Monitoring Biaya

Set budget alert di:

| Service | Lokasi | Rekomendasi prototype |
|---------|--------|-----------------------|
| Anthropic | Console → Settings → Limits → Daily spend | USD 5/hari (≈ Rp 80rb) |
| Fly.io | Dashboard → Billing → Spending alerts | USD 10/bulan (≈ Rp 160rb) |
| Vercel | Hobby plan free | (tidak perlu alert) |

Per call agen Sonnet ~1-2K token in + 500-1000 token out × harga Sonnet ≈ USD 0.02-0.05 per run. 1 run KKP dengan 39 tool calls = est. USD 0.50-1.50.

---

## Troubleshooting

### `fly deploy` gagal saat build

Cek 30 baris terakhir output `fly deploy`:

| Error | Penyebab | Fix |
|-------|----------|-----|
| `COPY failed: file not found in build context: v6/` | Folder `backend/v6/` tidak ada di mesin Anda | Pastikan V6 embedded di `backend/v6/{scripts,skills,templates,checklists}`. Lihat README §Layout V6 |
| `pip ERROR: ResolutionImpossible ... pydantic` | Konflik versi pydantic dengan mcp (>=2.11) | `requirements.txt` sudah pin `pydantic==2.11.10`. Pastikan local match (atau bump) |
| `npm ERR! 404 @anthropic-ai/claude-code` | Network issue saat build | Retry `fly deploy` |
| `claude-agent-sdk MessageParseError: Unknown message type rate_limit_event` | SDK < 0.1.81 dengan CLI modern | Pastikan requirements.txt: `claude-agent-sdk==0.1.81` |

### Frontend tidak bisa connect ke backend

| Symptom | Fix |
|---------|-----|
| `Load failed` di UI | Cek `NEXT_PUBLIC_API_BASE` di Vercel env var: `vercel env ls`. Harus `https://audit-ai-v7.fly.dev` |
| CORS error di Console | Set `fly secrets set APP_CORS_ORIGINS=https://your-vercel-url.vercel.app --app audit-ai-v7` lalu `fly deploy` |
| 401 Unauthorized | JWT lama (sebelum APP_SECRET_KEY ter-set). Logout & login ulang |

### Agen Claude error di production

| Symptom | Fix |
|---------|-----|
| `Claude Code not found` | Dockerfile belum install claude-code CLI. Redeploy dengan Dockerfile terbaru |
| `'SdkMcpTool' object has no attribute '__name__'` | Patch `agents/base.py` line 44 `t.__name__` → `t.name` belum di image. Redeploy |
| `Read-only file system: '/data'` | `APP_DATA_DIR` belum mengarah ke Fly volume. Cek fly.toml `[[mounts]] destination = '/data'` + env `APP_DATA_DIR=/data` |
| `Read-only file system: '/v6'` | V6 di-bake ke image (bukan volume). Cek Dockerfile `COPY v6/ /v6/` |

### SSE stream terputus

- Vercel Hobby tidak mendukung response > 10s untuk Edge runtime
- Tapi frontend pakai EventSource langsung ke Fly.io (bypass Vercel), seharusnya tidak ada masalah
- Cek `fly logs --app audit-ai-v7 -i` untuk timeout / connection drop

### Cek log real-time

```bash
# Tail log live
fly logs --app audit-ai-v7

# Filter pesan tertentu
fly logs --app audit-ai-v7 | grep -i "error\|claude\|qc_saipi"

# Cek SSH masuk ke container
fly ssh console --app audit-ai-v7
# Di dalam container:
which claude && claude --version
ls /v6/scripts/
ls /data/penugasan/
```

---

## TODO Production

Daftar pekerjaan untuk membuat AI jalan penuh di production. Urutan rekomendasi:

- [ ] **Apply 5 fix pipeline hardening lokal ke production** (lihat [README §Pipeline V6 Hardening](README.md#pipeline-v6-hardening)). File yang berubah:
  - `backend/Dockerfile` (Node + claude-code CLI) — sudah ✅
  - `backend/requirements.txt` (claude-agent-sdk 0.1.81, pydantic 2.11.10) — sudah ✅
  - `backend/app/agents/base.py` (tools=[], t.name, disallowed_tools) — sudah ✅
  - `backend/app/routes/penugasan.py` (scaffolding) — sudah ✅
  - `backend/app/tools/kkp_tools.py` (transform + sync QC) — sudah ✅
  - `backend/app/prompts/anggota_tim.md` (tighten) — sudah ✅
  - `backend/app/tools/pipeline_tools.py` (drop --no-render) — sudah ✅
  - `scripts/deploy-fly.sh` (V6 layout baru) — sudah ✅
  - **→ tinggal: `bash scripts/deploy-fly.sh`**

- [ ] **Verifikasi `claude` CLI auth headless di container.** Setelah deploy, SSH masuk dan test: `fly ssh console --app audit-ai-v7` → `echo "hi" | claude --print` harus jalan tanpa OAuth prompt.

- [ ] **Test agen end-to-end di production.** Upload 1 set dokumen reviu-pengadaan, jalankan agen, pastikan output PASS QC seperti di lokal.

- [ ] **Setup `APP_CORS_ORIGINS` multi-origin** kalau ada preview deploy Vercel: `https://audit-ai-v7.vercel.app,https://audit-ai-v7-*.vercel.app`

- [ ] **Setup logs persistence.** Fly free tier log retention pendek. Kalau perlu retensi audit, integrasikan ke external (e.g., Logtail, Better Stack).

- [ ] **Setup budget alert** (Anthropic + Fly).

- [ ] **Health check endpoint `/health` periodic** dari frontend untuk warm machine — saat ini `auto_stop_machines = 'stop'` di fly.toml, container shutdown setelah idle, cold start ~5-10s.

- [ ] **Backup strategy** untuk Postgres + Fly Volume (snapshot mingguan).

---

## Migrasi ke PDN (Tahap-2)

Bila ke depannya wajib pindah ke Pusat Data Nasional:

1. Setup VM di PDN (mis. server Pusdatin Komdigi) dengan Docker + Postgres
2. Build image backend dari Dockerfile yang sama
3. Restore database dari `pg_dump audit-ai-v7-db`
4. Pindahkan data file dari Fly Volume (snapshot) ke storage PDN
5. Update DNS — pointing ke server PDN
6. Sesuaikan `APP_CORS_ORIGINS` dengan URL frontend baru

Karena seluruh kode portable (FastAPI + Postgres + filesystem), migrasi terbatas pada infrastruktur, bukan rewrite.

---

## Lihat Juga

- [README.md](README.md) — Setup dev lokal + arsitektur + workflow auditor
- `backend/fly.toml` — Fly app config (mounts, env, http_service)
- `scripts/deploy-fly.sh` — Validasi V6 layout + fly deploy
- `scripts/deploy-vercel.sh` — Vercel deploy wrapper
