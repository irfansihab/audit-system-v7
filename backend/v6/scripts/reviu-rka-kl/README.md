# Pre-digest, Cross-Check & Render Pipeline — Reviu RKA-K/L (v0.2)

Pipeline deterministik yang menggeser pekerjaan ekstraksi dan deteksi inkonsistensi dari reasoning LLM ke Python scripts. Mempercepat + meningkatkan akurasi skill `reviu-rka-kl`.

## Arsitektur v0.2

```
TOR.pdf ─┐                                          ┌─► LHR-DRAFT.docx
         ├─► digest_tor.py ─► tor.json ─┐           │       (siap review auditor)
         │                              │           │
RAB.pdf ─┴─► digest_rab.py ─► rab.json ─┴─► cross_check.py ─► anomalies.json ─► render_lhr.py
                                                    │
                                                    ├─► context.md (dari Task 01)
                                                    └─► tor.json/rab.json (metadata cover)
```

Claude masuk di dua titik: (1) **setelah anomalies.json dihasilkan** — verify, filter false positive, tambah catatan substantif yang rule tidak capture; (2) **setelah LHR-DRAFT.docx** — narasi polishing dan validasi gate auditor.

## Komponen

| Script | Fungsi | Input | Output |
|---|---|---|---|
| `digest_tor.py` | Parse TOR PDF → JSON terstruktur | PDF TOR | `<file>.tor.json` |
| `digest_rab.py` | Parse RAB PDF → JSON komponen-akun-rincian | PDF RAB | `<file>.rab.json` |
| `cross_check.py` | 21 rules deterministik atas TOR+RAB JSON | 2 JSON | `anomalies.json` |
| `render_lhr.py` | Render anomalies → draft LHR docx | 3 JSON + context.md | `.docx` |
| `demo-anomalies.json` | Contoh output cross-check (v0.1) | — | — |

## Cara Pakai

```bash
cd audit-system-v4

PENUGASAN=penugasan/RKAKL
TOR="$PENUGASAN/03-perencanaan/TOR 2027-Fasilitasi Sektor Pertanian-Rev2.docx.pdf"
RAB="$PENUGASAN/03-perencanaan/RAB 2027-Pertanian-Review 2.pdf"

mkdir -p "$PENUGASAN/_KKP" "$PENUGASAN/_LHP"

# 1. Pre-digest dokumen
python3 scripts/reviu-rka-kl/digest_tor.py "$TOR" --no-raw -o "$PENUGASAN/_KKP/tor.json"
python3 scripts/reviu-rka-kl/digest_rab.py "$RAB" -o "$PENUGASAN/_KKP/rab.json"

# 2. Cross-check → anomali terdeteksi
python3 scripts/reviu-rka-kl/cross_check.py \
  "$PENUGASAN/_KKP/tor.json" \
  "$PENUGASAN/_KKP/rab.json" \
  -o "$PENUGASAN/_KKP/anomalies.json"

# 3. Render draft LHR
python3 scripts/reviu-rka-kl/render_lhr.py \
  "$PENUGASAN/_KKP/anomalies.json" \
  "$PENUGASAN/context.md" \
  --tor "$PENUGASAN/_KKP/tor.json" \
  --rab "$PENUGASAN/_KKP/rab.json" \
  -o "$PENUGASAN/_LHP/LHR-DRAFT.docx"
```

Empat file dihasilkan, siap direview auditor.

## Daftar 21 Rules (v0.2)

| ID | Aspek | Severity | Rule |
|---|---|---|---|
| A.1 | A | PERINGATAN | Honor Tim Pengelola Output berdurasi panjang di Persiapan |
| A.2 | A | PERINGATAN | Sewa kendaraan pejabat Eselon I/II |
| A.3 | A | INFO | Keterbatasan referensi SBM tahun reviu |
| B.1 | B | PERINGATAN | Akun 526xxx digunakan untuk line-item sewa |
| B.2 | B | PERINGATAN | Akun 522191 untuk konstruksi/properti panggung |
| B.3 | B | PERINGATAN | Duplikasi pola biaya antar komponen |
| C.1 | C | PERINGATAN | Penandaan ganda Cluster 1 dan Cluster 2 |
| D.1 | D | PERINGATAN | Dasar hukum tanpa pasal/ayat spesifik |
| D.2 | D | PERINGATAN | Dasar hukum merujuk sektor yang tidak relevan |
| D.3 | D | PERINGATAN | Inkonsistensi IRO antar bagian TOR dan RAB |
| D.4 | D | PERINGATAN | Formula KPI belum operasional (bobot/formula tidak konvensional) |
| D.5 | D | PERINGATAN | Matriks Manajemen Risiko belum lengkap (Kriteria IR2 butir 7) |
| D.6 | D | PERINGATAN | CBA tidak inline dengan jumlah penerima manfaat |
| E.1 | E | PERINGATAN | TOR menyebut lokasi bukan lokasi target |
| E.2 | E | PERINGATAN | Narasi sektor lain dalam TOR sektor tertentu |
| E.3 | E | PERINGATAN | Inkonsistensi baseline narasi vs tabel |
| E.4 | E | PERINGATAN | Asumsi biaya CBA tidak konsisten dengan pagu RO |
| E.5 | E | PERINGATAN | Tenaga Ahli TOR tidak memiliki line-item RAB |
| E.6 | E | PERINGATAN | Rasio target per perangkat tidak dijustifikasi |
| F.1 | F | INFO | Narasi merujuk ≥3 Asta Cita tanpa pemetaan |
| F.2 | F | INFO | Penandaan RPJMN PN tanpa referensi bab/kegiatan prioritas spesifik |

## Hasil Demo Terbaru di TOR+RAB 2027 Pertanian

- 21 rules diuji
- **19 anomali** terdeteksi (16 PERINGATAN + 3 INFO)
- Coverage vs 21 catatan manual Claude: **90% (19/21)**
  - Tambahan v0.2: A.1 (honor), D.2 (regulasi tidak relevan), F.2 (RPJMN PN)
  - Gap tersisa: D.4 parser KPI dari tabular PDF layout (parser tidak bisa extract field, rule exist tetapi tidak ter-trigger); C.1 ditemukan manual Claude ternyata false positive (TOR tidak mark Cluster 1)
  - Net valid coverage: 19/20 = **95%**

## Peran Claude Setelah Pipeline

Pipeline meng-handle 95% catatan deterministik. Claude menangani 5% sisa yang substantif:

- **Kualitas formula KPI** (parser belum extract IKP/IKK detail dari layout tabular; Claude bisa baca raw_text_pages untuk verifikasi)
- **False positive filtering** — rules kadang over-flag (mis. E.2 pendidikan/kesehatan dari konteks "6 sektor strategis")
- **Judgment kebijakan** — apakah RO relevan pada level policy
- **Narasi LHR** — sentuhan akhir bahasa agar preventif dan persuasif
- **Catatan substantif baru** — hal yang rules tidak model

## Batasan (v0.2)

**Parser TOR**:
- Field `ro` ✅ FIXED di v0.2 (regex lookbehind)
- Field `kpi.ikp_program/ikk_kegiatan` — parsial, masih gagal extract detail dari layout tabular (rule D.4 masih bisa trigger dari keyword detection)
- Field `penandaan_cluster` — detection checkbox unicode (◻ vs ☑) tetap probabilistik; untuk dokumen tanpa Cluster 1 ditandai eksplisit, parser menyatakan empty (behavior correct)
- Field `dasar_hukum.jenis_regulasi` ✅ FIXED di v0.2

**Parser RAB**:
- Total per komponen ✅ FIXED di v0.2 (pattern digit group ≥3)
- Line-item dengan harga diawali "-" dash masih miss. Fix nyata: minta unit penyusun kirim file Excel (.xlsx) asli.

**Rules**:
- Rules hanya flag structural/pattern issues. Substantive judgment (kebijakan, kualitas pasar, nuansa regional) tetap tugas Claude/auditor.
- False positives pada E.2 (sector leakage) saat RO disebut dalam konteks "6 sektor strategis" — parser sudah filter, tapi masih bisa terlewat.

## Integrasi dengan Task Workflow

Pipeline ini sudah terintegrasi ke:
- `tasks/03-generate-kkp.md` — Langkah 0 menginstruksikan Claude menjalankan 3 skrip sebelum analisis
- `skills/reviu-rka-kl/SKILL.md` — section "Pipeline Pre-digest & Cross-check (WAJIB untuk Task 03)" dengan tabel 21 rules

Claude akan otomatis memanggil pipeline saat user memasuki Task 03 di gate-based workflow.

## Cara Menambah Rule

1. Tulis fungsi `rule_<id>_<nama>(tor, rab) -> dict | None` di `cross_check.py`.
2. Pakai helper `_rule(rule_id, severity, aspek, judul, deskripsi, bukti, draft)`.
3. Return `None` bila tidak match, atau dict dari `_rule(...)` bila match.
4. Tambahkan nama fungsi ke list `ALL_RULES`.
5. Test: jalankan `cross_check.py` di JSON dokumen uji coba.

## Sketch Pipeline untuk Skill Lain

Pola sama bisa dipakai untuk skill lain dengan penyesuaian parser input dan rules. Estimasi effort per skill ~2–4 jam untuk parser + 2–3 jam untuk rules awal (10–15 rules).

| Skill | Dokumen input | Rules kandidat awal |
|---|---|---|
| `audit-pengadaan` | Kontrak/SPK + HPS + RFI + BAST + BA Pembayaran | Perbedaan nilai Kontrak vs HPS, pembayaran non-LS, dokumen BAST fisik incomplete, SLA kurang, penyimpangan jadwal |
| `reviu-pengadaan` | KAK + HPS + Dok Pemilihan | Konsistensi KAK–HPS, metode pemilihan sesuai PMK, spektek terukur, kewajaran harga vs market research |
| `pemantauan-pengadaan` | Kontrak + BAST progres + Laporan bulanan | Progres fisik ≠ progres keuangan, keterlambatan timeline, amandemen kontrak |
| `evaluasi-sakip` | LKE Excel + LKj + IKU | Cascading IKU PK → RKT → LKj, formula IK operasional, cakupan penilaian 100% |
| `evaluasi-spip` | LKE SPIP Excel + bukti dukung | Kecukupan bukti per pernyataan, konsistensi nilai, AoI terakumulasi |

Untuk skill-skill ini, prioritas bangun parser LKE Excel (openpyxl) lebih dulu karena SAKIP/SPIP lebih bergantung pada data tabular daripada narasi PDF.

## Perbaikan Roadmap

**v0.3** (next quick win):
- Fix parse_kpi untuk handle layout tabular dengan pendekatan tokenization (bukan regex)
- Support input XLSX untuk RAB (bypass semua masalah PDF extraction)
- 5 rules tambahan: pembulatan biaya tidak wajar, jumlah rincian vs target output, duplikasi akun antar komponen per deskripsi

**v1.0** (production):
- Unit tests dengan dataset TOR/RAB berbagai sektor
- CLI wrapper yang menggabung 4 skrip dalam satu perintah `reviu-rka-kl run <penugasan-folder>`
- Schema JSON yang di-version untuk backward compatibility
