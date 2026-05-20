# Pipeline Audit Pengadaan — v0.1

Pipeline deterministik untuk skill `audit-pengadaan` (Keyakinan Memadai). Pola mengikuti pipeline `reviu-rka-kl` tapi disesuaikan dengan dokumen multi-jenis khas pengadaan (KAK, HPS, Kontrak, BAST, Pembayaran).

## Arsitektur

```
folder penugasan ─► digest_pengadaan.py ─► pengadaan-digest.json
                    (scan + klasifikasi + parse)     │
                                                      ▼
                                           cross_check.py (11 rules)
                                                      │
                                                      ▼
                                           anomalies.json
                                                      │
                                         context.md ──┤
                                                      ▼
                                           render_lha.py ─► LHA-DRAFT.docx
```

## Komponen

| Script | Fungsi |
|---|---|
| `digest_pengadaan.py` | Scan folder, klasifikasi 14 jenis dokumen via filename pattern, parse ke JSON |
| `cross_check.py` | 11 rules deterministik (Perencanaan, Kontrak, Pelaksanaan, Pembayaran, Dokumentasi) |
| `render_lha.py` | Render anomalies → draft LHA dengan kolom KKP audit (No, Judul, Kondisi, Kriteria, Sebab, Akibat) |

## Cara Pakai

```bash
cd audit-system-v4

PENUGASAN=penugasan/2026-005-audit-pengadaan-dcdrc

# 1. Digest (scan + parse semua dokumen)
python3 scripts/audit-pengadaan/digest_pengadaan.py \
  "$PENUGASAN" \
  -o "$PENUGASAN/_KKP/pengadaan-digest.json"

# 2. Cross-check
python3 scripts/audit-pengadaan/cross_check.py \
  "$PENUGASAN/_KKP/pengadaan-digest.json" \
  -o "$PENUGASAN/_KKP/anomalies.json"

# 3. Render LHA
python3 scripts/audit-pengadaan/render_lha.py \
  "$PENUGASAN/_KKP/anomalies.json" \
  "$PENUGASAN/context.md" \
  -o "$PENUGASAN/_LHP/LHA-DRAFT.docx"
```

## 14 Jenis Dokumen yang Diklasifikasi

| Doc Type | Pola Filename | Parser |
|---|---|---|
| `kak` | `KAK`, `Kerangka Acuan`, `TOR` | ✅ `parse_kak` |
| `hps` | `HPS`, `Harga Perkiraan` | ✅ `parse_hps` |
| `hps_detail` | `Tabel Penyusun HPS`, `Rekap Komponen HPS` | (no parser) |
| `identifikasi_pengadaan` | `Identifikasi Pengadaan` | (no parser) |
| `rfi` | `RFI`, `Request For Information` | (no parser) |
| `kontrak` | `SSUKSSKK`, `Salinan Jasa Lainnya`, `Kontrak`, `SPK` | ✅ `parse_kontrak` |
| `sppbj` | `SPPBJ` | (no parser) |
| `perjanjian_kerahasiaan` | `Perjanjian Kerahasiaan`, `NDA` | (no parser) |
| `permohonan_jaminan` | `Permohonan Jaminan` | (no parser) |
| `pembayaran_ls` | `LS` + bulan, `SPM LS` | ✅ `parse_pembayaran` |
| `sptb` | `SPTB` | ✅ `parse_pembayaran` |
| `ba_rekonsiliasi` | `BA Rekonsiliasi`, `Berita Acara SLA` | ✅ `parse_bast` |
| `laporan_bulanan` | `Laporan Bulanan` | (no parser) |

## 11 Rules (v0.1)

| ID | Aspek | Severity | Rule |
|---|---|---|---|
| D.1 | Dokumentasi | KRITIS/PERINGATAN | Dokumen kunci (KAK/HPS/Kontrak) tidak ditemukan |
| D.2 | Dokumentasi | INFO | Banyak file unclassified di folder |
| P.1 | Perencanaan | PERINGATAN | HPS tanpa dokumen pembentuk harga |
| P.2 | Perencanaan | PERINGATAN | Periode KAK ≠ HPS |
| P.3 | Perencanaan | PERINGATAN | SLA KAK ≠ HPS |
| P.4 | Perencanaan | PERINGATAN | KAK menyebut migrasi tapi HPS tidak |
| K.1 | Kontrak | PERINGATAN | Nilai kontrak ≥ HPS (tidak wajar) |
| K.2 | Kontrak | PERINGATAN | Kontrak tanpa klausul SLA padahal KAK mensyaratkan |
| K.3 | Kontrak | PERINGATAN | Kontrak tanpa Jaminan Pelaksanaan |
| PL.1 | Pelaksanaan | PERINGATAN | Pembayaran dilakukan namun BAST tidak ditemukan |
| B.1 | Pembayaran | PERINGATAN | Pembayaran tanpa rujukan BAST/Invoice/Kwitansi |

## Hasil Demo di Sample DCDRC PSrE

Dijalankan pada `uji coba/1.Pusat Data dan Pusat Pemulihan Bencana PSrE Induk`:
- 14 dokumen dikenali (3 HPS, 1 KAK, 1 kontrak, 3 RFI, 1 BAST, 1 SPPBJ, 1 SPTB, dll.)
- 5 file tidak terklasifikasi
- **4 anomali terdeteksi** (P.2 periode, P.4 migrasi, B.1 bukti pembayaran, D.2 unclassified)

## Batasan v0.1

- Parser `kak` dan `hps` punya beberapa false positive pada periode (ambil angka pertama yang match, bukan necessarily periode pengadaan)
- SLA detection simpel — `\bSLA\b\d+%` — bisa miss variasi "Service Level 99.5%"
- Kontrak parser pakai `search` — nilai kontrak yang spread across paragraphs bisa miss
- Rules belum cover: Jaminan Pemeliharaan, Addendum Kontrak, PPN, Retensi, Denda Keterlambatan, SPTJM

## Roadmap v0.2

- Perbaiki false positive periode parser (regex lebih ketat, context-aware)
- Tambah 5 rules: nilai kontrak vs pagu, addendum compliance, denda keterlambatan, retensi, PPN
- Support XLSX untuk RAB & HPS detail
- Integrasi tools Claude untuk verifikasi manual pada temuan KRITIS
