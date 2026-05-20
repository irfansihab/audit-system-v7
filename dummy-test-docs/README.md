# Dummy Test Documents — Audit AI v7

Folder ini berisi dokumen dummy realistic untuk testing UI workflow di audit-system-v7.
Generated otomatis — semua konten fiktif, tidak terkait dengan transaksi nyata.

## Inventaris

### Reviu Pengadaan (skill: `reviu-pengadaan`)

**5 KAK** — Kerangka Acuan Kerja
- `KAK-Layanan-Cloud-PSrE-2026.pdf` — Cloud PSrE, Rp 5,5 M, SLA 99,9%
- `KAK-Data-Center-DRC-2026.pdf` — DC Tier-3, Rp 8,2 M
- `KAK-Pelatihan-Cyber-Security-2026.pdf` — Pelatihan, Rp 450 jt
- `KAK-App-SatuData-2026.pdf` — App Mobile, Rp 1,85 M
- `KAK-Lisensi-M365-2026.pdf` — Lisensi MS 365, Rp 3,4 M

**4 HPS** — Harga Perkiraan Sendiri (rincian item + tabel vendor RFI)
- `HPS-Cloud-PSrE-2026.pdf` ⚠️ **berisi anomali**: RFI Telkom Sigma menolak (1 valid + 3 invalid)
- `HPS-Data-Center-2026.pdf`
- `HPS-Pelatihan-Cyber-2026.pdf`
- `HPS-Lisensi-M365-2026.pdf`

**5 RFI** — Request for Information dari vendor
- `RFI-CNI-Cloud-PSrE-2026.pdf` — penawaran valid
- `RFI-Telkom-Sigma-Cloud-2025.pdf` ⚠️ **surat penolakan + TA salah (2025 vs 2026)**
- `RFI-Biznet-Cloud-PSrE-2026.pdf`
- `RFI-DCI-DataCenter-2026.pdf`
- `RFI-MII-Lisensi-M365-2026.pdf`

**2 KONTRAK**
- `KONTRAK-Cloud-PSrE-CNI-2026.pdf`
- `KONTRAK-DataCenter-DCI-2026.pdf`

### Reviu RKA-K/L (skill: `reviu-rka-kl`)

**4 TOR** — Term of Reference (struktur lengkap 7-8 blok)
- `TOR-App-PDP-2026.pdf` — Rp 2,45 M
- `TOR-Survei-Literasi-Digital-2026.pdf` — Rp 3,2 M
- `TOR-Sosialisasi-PDP-2026.pdf` — Rp 1,8 M
- `TOR-PDN-Tahap-2-2026.pdf` — Rp 15 M

**3 RAB** — Rencana Anggaran Biaya (Excel, tabel akun)
- `RAB-App-PDP-2026.xlsx`
- `RAB-Survei-Literasi-2026.xlsx`
- `RAB-Sosialisasi-PDP-2026.xlsx`

### Dokumen Umum

**2 ST** — Surat Tugas
- `ST-51-Reviu-Cloud-PSrE-2026.pdf` — penugasan reviu pengadaan
- `ST-78-Reviu-RKA-DIT-PENGENDALIAN-2026.pdf` — penugasan reviu RKA-K/L

**2 KP** — Kartu Penugasan
- `KP-156-Reviu-Cloud-PSrE-2026.pdf`
- `KP-203-Reviu-RKA-2026.pdf`

**2 PKP** — Program Kerja Pengawasan (sasaran + langkah kerja)
- `PKP-Reviu-Cloud-PSrE-2026.pdf` — 4 sasaran (S-PBJ-01 s.d. S-PBJ-04)
- `PKP-Reviu-RKA-DIT-PENGENDALIAN-2026.pdf` — 3 sasaran (S-RKA-01 s.d. S-RKA-03)

## Cara Pakai

### Skenario 1: Test Reviu Pengadaan

1. Buat penugasan baru dengan skill **Reviu Pengadaan**, obyek "Pengadaan Layanan Cloud PSrE Induk"
2. Upload ke tab Dokumen:
   - `ST-51-...pdf` (ST)
   - `KP-156-...pdf` (KP)
   - `PKP-Reviu-Cloud-PSrE-2026.pdf` (PKP)
   - `KAK-Layanan-Cloud-PSrE-2026.pdf` (KAK)
   - `HPS-Cloud-PSrE-2026.pdf` (HPS)
   - 4 file RFI (`RFI-CNI-...`, `RFI-Telkom-Sigma-...`, `RFI-Biznet-...`)
   - `KONTRAK-Cloud-PSrE-CNI-2026.pdf` (KONTRAK)
3. Ingestion auto-trigger, tunggu status semua `READY`
4. Edit `context.md` dan `_PKP/sasaran-assignment.json` (set sasaran S-PBJ-01..04 assigned ke "Sarah Aulia")
5. Tab **Chat AT** → jalankan agen
6. Expected temuan: anomali RFI Telkom Sigma (penolakan + TA salah), HPS hanya 1 sumber harga valid

### Skenario 2: Test Reviu RKA-K/L

Pakai `ST-78`, `KP-203`, `PKP-Reviu-RKA-...`, plus 1-2 TOR + RAB yang sesuai.

## Catatan

Generator script: `dummy-test-docs/_generator.py` (jika perlu regenerate).
Folder ini di-gitignore — tidak ter-commit ke repo.
