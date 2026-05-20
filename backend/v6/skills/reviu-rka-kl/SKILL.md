---
name: reviu-rka-kl
version: 3.0
jenis: Reviu Rencana Kerja dan Anggaran Kementerian/Lembaga
dasar-hukum: PMK 107/2024 (perubahan PMK 62/PMK.02/2023), Pasal 61
model: claude-sonnet-4-6
output: LHR RKA-K/L + Nota Dinas Pengantar
auto_execute: true
auto_execute_command: python3 audit-system-v4/scripts/reviu-rka-kl/run_batch.py --penugasan <PENUGASAN_DIR>
---

# Skill: Reviu Rencana Kerja dan Anggaran (RKA-K/L)
**Versi 3.0** (Mei 2026) — Sesuai PMK 107 Tahun 2024 (Perubahan PMK 62/PMK.02/2023)
> **Checklist gate-by-gate:** Lihat `audit-system-v4/checklists/reviu-rka-kl.md` untuk daftar pemeriksaan tahap demi tahap.

**Update v3.0:** pipeline 39 rules (21 + 18 alt), auto-execute via `run_batch.py`, render LHR multi-RO, parser pdftotext (10x speedup), end-to-end ≤ 13 detik untuk 12 RO.

---

## ⚡ AUTO-EXECUTE LANGKAH 0 — WAJIB SEBELUM ANALISIS APAPUN

**SEGERA setelah skill ini dipanggil dan auditor menyebut folder penugasan, Claude HARUS menjalankan pipeline orchestrator `run_batch.py` SEBELUM tindakan analisis apapun.** Tidak boleh skip, tidak boleh "uji coba dulu", tidak boleh manual.

```bash
python3 audit-system-v4/scripts/reviu-rka-kl/run_batch.py \
    --penugasan "<FOLDER_PENUGASAN>" \
    --workers 4 \
    --judul "Laporan Hasil Reviu RKA-K/L <Direktorat> TA <YYYY>" \
    --nomor "<nomor LHR>" \
    --tanggal "<DD Bulan YYYY>" \
    --penerima "<Direktur ...>"
```

Output otomatis (≤ 30 detik untuk N≤30 RO):
- `<PENUGASAN>/_KKP/tor-{N}.json` × N + `rab-{N}.json` × N (digest)
- `<PENUGASAN>/_KKP/anomalies-master.json` (39 rules deterministik + cross-RO check)
- `<PENUGASAN>/_KKP/_pipeline_meta.json` (timing, status per RO)
- `<PENUGASAN>/_LHP/LHR-DRAFT.docx` (multi-RO, dedup A.3, top-5 rekomendasi prioritas)

**Setelah pipeline selesai, BARU Claude masuk ke peran review/judgment** (filter false positive, validasi temuan substantif, polish narasi LHR). Jangan generate KKP/LHR/rule manual sebelum pipeline output ada — itu duplikasi pekerjaan.

**Jika `run_batch.py` error atau tidak ada:**
1. Cek script integrity: `python3 -c "import ast; ast.parse(open('audit-system-v4/scripts/reviu-rka-kl/run_batch.py').read())"`
2. Cek dependency: pdftotext (`apt install poppler-utils`), python3 ≥ 3.10, openpyxl, python-docx
3. Fallback ke 4 script terpisah (digest_tor → digest_rab → cross_check → render_lhr) — lihat Section "Pipeline Components" di bawah
4. Lapor ke auditor + tunggu instruksi

**Jika folder penugasan belum punya struktur (`input/objek/TOR/`, `input/objek/RAB/`)**: minta auditor mendefinisikan struktur, atau pakai mode flat dengan TOR & RAB di root folder. Jangan lanjut tanpa konfirmasi.

---

## ⚡ AUTO-EXECUTE LANGKAH 1 — ANALISIS SUBSTANTIF WAJIB POST-PIPELINE

**Setelah LANGKAH 0 (pipeline rule-based) selesai, Claude WAJIB lanjut analisis substantif berikut SECARA OTOMATIS.** Tidak boleh menawarkan opsi ke auditor ("Mau saya bantu...?") — auditor sudah meminta dengan memanggil skill ini, jadi semua analisis berikut WAJIB dieksekusi tanpa nunggu konfirmasi.

Rules deterministik di pipeline LANGKAH 0 hanya menangkap inkonsistensi struktural sederhana. Substantive judgment di bawah ini adalah value-add AI yang sesungguhnya — kalau Claude skip ini dan hanya tampilkan output rule-based, demo akan terlihat lemah.

| # | Tugas Substantif | Detail |
|---|------------------|--------|
| 1. | **Verifikasi false positive rules deterministik** | Pipeline jalankan 39 rules. Untuk setiap anomali HIGH/CRITICAL: buka TOR/RAB di halaman yang dirujuk, verifikasi anomali real atau parser glitch. Hapus false positive dari anomalies-master.json. |
| 2. | **Analisis kewajaran SBM/SBK** | Untuk setiap RO: bandingkan harga satuan di RAB vs SBM/SBK yang berlaku TA tersebut. Bila harga > batas SBM atau ada komponen yang tidak ada di SBM → temuan KRITIS. |
| 3. | **Cek kelengkapan substansi TOR (Kriteria IR2)** | Setiap TOR wajib punya 7 blok substansi: Latar Belakang, Penerima Manfaat + KPI, Strategi Pencapaian, Kurun Waktu, Biaya, CBA, Manajemen Risiko. Tampilkan TOR yang kurang. |
| 4. | **Validasi cascading anggaran** | Cek konsistensi cascading: program → kegiatan → KRO → RO. Bila ada output orphan (tidak ter-link ke kegiatan parent) → temuan PERINGATAN. |
| 5. | **Analisis penandaan anggaran** | Setiap RO wajib punya penandaan (Prioritas Nasional, Gender, Stunting, dll. sesuai kategori yang berlaku). Bila penandaan kosong atau tidak relevan dengan substansi RO → temuan PERINGATAN. |
| 6. | **Tambahkan temuan substantif ke anomalies-master.json** | Append sebagai entry baru dengan rule_id manual seperti SUB.1, SUB.2 (untuk membedakan dari rule deterministik). |

**Setiap temuan substantif WAJIB di-append** ke `_KKP/temuan.json` sebagai entry baru (T-XXX) dengan struktur lengkap KKSA + dokumen_sumber + status "DRAFT" + anggota_tim sesuai `_ROLE.md`.

**Setelah semua analisis substantif selesai, BARU lapor ke auditor** dengan ringkasan: total temuan rule-based + total temuan substantif + per-severity breakdown. Hindari kalimat "Mau saya lanjut ...?" — tampilkan langsung hasil.

---


## Identitas
- **Nama Skill:** reviu-rka-kl
- **Jenis Pengawasan:** Reviu Perencanaan Anggaran
- **Dasar Hukum:** PMK 107/PMK.02/2024 (mengubah PMK 62/PMK.02/2023), Pasal 61
- **Tingkat Keyakinan:** Terbatas (*limited assurance*) — memastikan kesesuaian kaidah penganggaran
- **Kode Nomor Surat:** PW.04.04
- **Model AI:** Claude Sonnet 4.6 (via Cowork)

---

## Posisi dalam Keluarga Skill Kinerja

> Semua skill kinerja menggunakan regulasi yang sama. Lihat `shared-kinerja-references/PANDUAN.md` untuk perbandingan lengkap.

| | Audit Kinerja | Evaluasi SAKIP | Reviu LKj | **Reviu RKA/KL** (skill ini) |
|---|---|---|---|---|
| Objek | Program yang berjalan | Sistem SAKIP (4 komponen) | Laporan Kinerja | **Draft anggaran T+1** |
| Waktu | Selama/setelah program | Jan–Mar (ex-post tahunan) | Sebelum LKj diserahkan | **Mar–Apr / Agt–Sep / Okt–Nov** |
| Keyakinan | Memadai | Terbatas (scored) | Terbatas | **Terbatas** |
| Output | LHA Kinerja | LHE AKIP + LKE | LHR LKj | **LHR RKA-K/L + Nota Dinas** |

**Pilih reviu RKA/KL ketika:**
- APIP diminta melakukan reviu pagu indikatif, pagu anggaran, atau pagu alokasi
- Pimpinan ingin memastikan kualitas perencanaan anggaran sebelum APBN ditetapkan
- Ada usulan tambahan anggaran dari sub BA BUN (LHR wajib dilampirkan)

**Jangan gunakan skill ini ketika:**
- Program sudah berjalan → gunakan **audit-kinerja**
- LKj sudah disusun dan perlu direviu → gunakan **reviu-kinerja**
- Sistem AKIP secara keseluruhan perlu dievaluasi → gunakan **evaluasi-sakip**

---

## Peran Claude

Kamu adalah reviewer APIP yang memeriksa kualitas dan kesesuaian dokumen perencanaan anggaran (RKA-K/L) berdasarkan **Pasal 61 PMK 107/2024**. Tugasmu adalah memberikan keyakinan terbatas (*limited assurance*) bahwa:

1. Rincian anggaran **sesuai SBM/SBK/SSB** yang ditetapkan
2. Penyusunan **patuh terhadap kaidah penganggaran** (Pasal 14 PMK 62/2023)
3. Keluaran memiliki **penandaan anggaran** yang tepat
4. **Dokumen pendukung** (KAK/TOR, RAB, RKA Satker) lengkap dan konsisten
5. Rincian anggaran untuk **Kegiatan/Keluaran baru** layak dan wajar
6. **Pengalokasian tematik** sesuai penugasan

Reviu ini **bukan audit penuh** — kamu tidak membuktikan pelanggaran atau menghitung kerugian. Kamu memberikan **saran perbaikan** sebelum dokumen difinalisasi.

---

## Tiga Tahap Reviu RKA-K/L

```
TAHAP 1 — REVIU PAGU INDIKATIF (Maret–April)
  Objek  : Renja K/L dan usulan Pagu Indikatif
  Fokus  : Keselarasan RPJMN/RKP, kualitas IK, relevansi program

TAHAP 2 — REVIU PAGU ANGGARAN (Agustus–September) ← PALING SUBSTANTIF
  Objek  : Rancangan RKA-K/L (sebelum Trilateral Meeting)
  Fokus  : Semua 6 aspek Pasal 61(2) — kelayakan SBM, kaidah,
           penandaan, kelengkapan dokumen, kewajaran rincian baru

TAHAP 3 — REVIU PAGU ALOKASI / DEFINITIF (Oktober–November)
  Objek  : RKA-K/L berdasarkan Pagu Alokasi (APBN yang ditetapkan)
  Fokus  : Penyesuaian pagu, verifikasi alokasi per Satker
```

---

## 6 Aspek Reviu (Pasal 61 Ayat 2)

### A. Kelayakan Anggaran vs Standar Biaya (SBM/SBK/SSB)

| Yang Diperiksa | Kriteria |
|----------------|----------|
| Satuan honor, perjalanan dinas, sewa | Sesuai PMK SBM tahun berjalan |
| Output yang ada SBK-nya | Total anggaran ≤ SBK × volume |
| Proporsi komponen biaya | Sesuai SSB yang ditetapkan |

> Jika PMK SBM belum tersedia sebagai referensi: **nyatakan keterbatasan** dalam LHR.

### B. Kepatuhan Kaidah Penganggaran (Pasal 14 PMK 62/2023)

- Tidak ada duplikasi anggaran antarkegiatan
- Klasifikasi belanja tepat (modal vs barang vs pegawai vs bansos)
- Nomenklatur Program/Kegiatan/Output valid (sesuai KRISNA/SAKTI)
- Kegiatan dalam tupoksi unit yang bersangkutan

### C. Penandaan Anggaran (*Budget Tagging*)

- Semua Keluaran (output) memiliki penandaan sesuai kategori yang ditetapkan
- Kategori penandaan relevan dengan substansi output (misal: Prioritas Nasional, gender, stunting)

### D. Kelengkapan Dokumen Pendukung

| Dokumen | Wajib Ada | Keterangan |
|---------|-----------|------------|
| KAK/TOR | Setiap kegiatan | Justifikasi, ruang lingkup, + 7 blok substansi (lihat Kriteria IR2) |
| RAB | Setiap komponen | Perincian biaya detail, selaras dengan Metode Pelaksanaan |
| RKA Satker | Semua Satker | Distribusi per unit kerja |
| Dokumen pendukung lain | Sesuai jenis kegiatan | SK, studi, dll. |

**Substansi TOR/KAK** wajib mengikuti **Kriteria IR2** (Inspektorat II) sebagaimana dirinci di `references/04-kriteria-substansi-tor.md`, meliputi: (1) Latar Belakang [Dasar Hukum + Gambaran Umum dengan urgensi, WBS/KPI, lokasi], (2) Penerima Manfaat + KPI, (3) Strategi Pencapaian Keluaran [Metode Pelaksanaan + Tahapan Waktu], (4) Kurun Waktu Pencapaian Keluaran, (5) Biaya yang Diperlukan, (6) CBA, (7) Manajemen Risiko.

### E. Kelayakan Rincian Anggaran Baru

Berlaku untuk **Kegiatan/Keluaran baru** dan **Angka Dasar yang berubah**:
- Volume dalam KAK = volume dalam RKA (konsisten)
- Komponen biaya relevan dengan output yang dihasilkan
- Tidak ada komponen berlebihan atau tidak terkait
- **Konsistensi internal TOR** (Kriteria IR2): WBS ↔ Metode Pelaksanaan ↔ Tahapan Waktu ↔ RAB harus saling selaras

### F. Pengalokasian Tematik

- Alokasi untuk tematik tertentu (sesuai penugasan/kebijakan Pemerintah) terpenuhi
- Proporsi sesuai target yang ditetapkan

---

## Format Catatan Reviu

```
CATATAN [N] — [JUDUL DESKRIPTIF KONDISI]

Kondisi    : [Fakta spesifik — sebutkan Program/Kegiatan/Output/Satker/
              baris RAB yang dimaksud, nilai rupiah jika relevan]

Kriteria   : [Pasal/PMK acuan — contoh: Pasal 61(2)(a) PMK 107/2024 jo.
              PMK SBM Tahun [YYYY] Nomor [...] Lampiran [...]]

Akibat     : [Konsekuensi: anggaran tidak efisien / risiko blokir DIPA /
              tidak dapat dicairkan / ketidaksesuaian dengan target kinerja]

Rekomendasi: [Tindakan konkret: sesuaikan dengan SBM, lengkapi KAK,
              hapus komponen yang tidak relevan — oleh siapa, sebelum kapan]
```

**Penting:**
- Hindari kata "temuan" — gunakan "catatan"
- Sebutkan angka/kode spesifik, bukan generalisasi
- JANGAN menganalisis Sebab — reviu tidak investigasi penyebab
- JANGAN menilai kebijakan (apakah program ini perlu ada)

---

## Pipeline Components (audit-system-v4 — v3.0)

**Lokasi:** `audit-system-v4/scripts/reviu-rka-kl/` (BUKAN audit-system-v2 — itu legacy)

**Entry utama:** `run_batch.py` (orchestrator end-to-end). 4 component script di-orchestrate olehnya:

| Script | Fungsi | Input | Output | v3.0 Notes |
|---|---|---|---|---|
| `run_batch.py` | **Orchestrator end-to-end** (auto-pair TOR-RAB + parallel + render) | folder penugasan | semua output | **WAJIB pakai ini sebagai entry** |
| `digest_tor.py` | Parse TOR PDF → JSON terstruktur (7 blok substansi Kriteria IR2 + raw_text_pages) | TOR.pdf | `tor-{N}.json` | pdftotext -layout (10x faster, robust >5MB) |
| `digest_rab.py` | Parse RAB PDF → JSON komponen→akun→rincian | RAB.pdf | `rab-{N}.json` | pdftotext -layout |
| `cross_check.py` | **39 rules** (21 original + 18 alt-rules) deterministik | tor+rab JSON | `anomalies-{N}.json` atau `anomalies-master.json` (mode `--batch`) | +18 alt-rules codified dari pola manual supplement |
| `render_lhr.py` | Render LHR DOCX dari anomalies-master | anomalies-master + KP context | `LHR-DRAFT.docx` | multi-RO mode dengan A.3 dedup |

**Self-check AST preflight** terpasang di setiap script (proteksi dari corrupt sync OneDrive).

### Distribusi Rules (39 total)

| Aspek | Original (21) | Alt (18) | Total |
|-------|---------------|----------|-------|
| A — SBM/SBK | A.1, A.2, A.3 | — | 3 |
| B — Kaidah | B.1, B.2, B.3 | B.alt-1..5 | 8 |
| C — Penandaan | C.1 | C.alt-1..3 | 4 |
| D — Kelengkapan | D.1..D.6 | — | 6 |
| E — Rincian Baru | E.1..E.6 | E.alt-1..6 | 12 |
| F — Tematik | F.1, F.2 | F.alt-1..4 | 6 |

Detail lengkap rules (judul, severity, kondisi trigger): `audit-system-v4/scripts/reviu-rka-kl/cross_check.py` (cari komentar `# Rule X.Y` atau function `rule_x_y_*`).

### Performa Benchmark (smoke test 12 RO DIT PED, Mei 2026)

| Metrik | Hasil |
|--------|-------|
| Wall clock end-to-end (run_batch.py + render LHR) | ~13 detik |
| Anomali ter-deteksi pipeline-only | 66 (vs 24 pre-v3 = 2,75x) |
| RO terbesar (RAB 7,3 MB) | 3,6 detik (vs >25s timeout pre-v3) |
| Speedup vs sequential pre-v3 | 8x |
| Manual supplement waktu | 0 menit (vs 10 menit pre-v3) |

### Hemat Token (Setelah Pipeline)

**ATURAN PENTING:** Setelah pipeline jalan dan output JSON ada di `_KKP/`, Claude **TIDAK BOLEH** membuka ulang TOR/RAB PDF untuk mendapat fakta yang sudah di-parse (komponen biaya, akun, volume, harga satuan, total per output, klasifikasi belanja, indikator KPI, raw text). Pakai langsung field di `tor-{N}.json` dan `rab-{N}.json` (terutama `raw_text_pages` untuk teks lengkap).

**Boleh re-read PDF** hanya untuk: verifikasi halaman yang dikutip ke catatan reviu, cross-check false positive rule, atau mengambil kalimat tepat untuk substansi LHR.

### Peran Claude Setelah Pipeline

Pipeline v3.0 meng-handle ~95% catatan deterministik (39 rules). Claude tetap perlu menangani ~5% catatan substantif yang butuh judgment:

- **Kualitas formula/metodologi KPI** — apakah formula IKP/IKK operasional dan matematis benar
- **Relevansi kebijakan program** — apakah RO layak pada level policy (di luar mandat APIP, hanya catatan)
- **False positive filtering** — tidak semua anomali script valid (mis. C.alt-2 kadang over-trigger di RAB tanpa penandaan eksplisit)
- **Verifikasi bukti material** — anomali dengan nominal besar atau implikasi serius, buka halaman PDF spesifik
- **Narasi dan bahasa LHR** — polish rekomendasi agar preventif & membangun
- **Konteks domain** — kalau ada nuansa direktorat (mis. RO digital tidak bisa dibandingkan dengan RO konstruksi)

### Cara Menambah Rules

Tulis fungsi `def rule_x_y_nama(tor: dict, rab: dict) -> dict | None` di `cross_check.py`, pakai helper `_rule(rule_id, severity, aspek, judul, deskripsi, bukti, draft)`, tambah ke list `ALL_RULES`. Untuk rule cross-RO (lintas penugasan), tambah ke list `CROSS_RO_RULES` dengan signature `def cross_rule_x(all_tor: list, all_rab: list) -> list[dict]`.

---

## Alur Kerja Reviu (Gate-Based v3.0)

```
GATE 0 — VALIDASI INPUT
  Auditor sediakan folder penugasan dengan:
  • 00-surat-tugas/  (ST + ND permintaan jika ada)
  • input/objek/TOR/  (PDF KAK/TOR per RO)
  • input/objek/RAB/  (PDF RAB per RO)
  • input/objek/RKA-Satker/  (RKA per Satker)
  Plus: PMK SBM tahun berjalan (jika tersedia)

GATE 1 — KP-Reviu (Kerangka Penugasan)
  • Latar belakang, tujuan reviu, ruang lingkup, metodologi
  • Pakai template: audit-system-v4/templates/PKP-Reviu-RKA-KL-template.xlsx
  • STOP & konfirmasi auditor

GATE 2 — PKP-Reviu (Program Kerja Pengujian)
  • Matriks 6 aspek × N RO
  • Pakai template
  • STOP & konfirmasi auditor

GATE 3 — PELAKSANAAN
  ┌─────────────────────────────────────────────────────────────────┐
  │ LANGKAH 0 (AUTO-EXECUTE WAJIB) — run_batch.py                   │
  │   python3 audit-system-v4/scripts/reviu-rka-kl/run_batch.py \   │
  │       --penugasan "<FOLDER>" --workers 4 \                      │
  │       --judul "..." --nomor "..." --tanggal "..." --penerima ...│
  │                                                                 │
  │   Output otomatis:                                              │
  │   • _KKP/tor-{N}.json + rab-{N}.json + anomalies-{N}.json       │
  │   • _KKP/anomalies-master.json (39 rules + cross-RO check)      │
  │   • _LHP/LHR-DRAFT.docx (siap review)                           │
  │   • _KKP/_pipeline_meta.json (metadata)                         │
  └─────────────────────────────────────────────────────────────────┘

  LANGKAH 1 — Review anomali (Claude judgment ~5%)
  • Baca anomalies-master.json
  • Filter false positive (terutama C.alt-2, E.alt-2)
  • Validasi PERINGATAN material → buka halaman PDF spesifik untuk konfirmasi
  • STOP & TANYA AUDITOR untuk anomali material atau PERINGATAN >5

  LANGKAH 2 — KKR-Reviu.xlsx
  • Pakai template KKR-Reviu-RKA-KL-template.xlsx
  • Sheet "Catatan Reviu" diisi dari anomalies-master.json
  • Klasifikasi status: TERPENUHI / TERPENUHI DENGAN CATATAN / TIDAK TERPENUHI

GATE 4 — LAPORAN HASIL REVIU (LHR)
  • LHR-DRAFT.docx sudah di-render run_batch.py
  • Polish narasi Bab E (Hasil Reviu) sesuai konteks domain
  • Polish Bab F (Rekomendasi) prioritas
  • Konfirmasi simpulan keyakinan terbatas (Bab G)
  • Generate Nota Dinas pengantar dari template
  • STOP & konfirmasi final auditor sebelum penomoran resmi
```

**Catatan gate-based wajib:** Tidak boleh skip Gate 1 atau 2 walau dalam mode "uji coba" (lihat memory `feedback_gate_based_workflow`). Gate 3 Langkah 0 (`run_batch.py`) WAJIB jalan dulu sebelum Claude masuk ke judgment.

---

## Format Output: LHR RKA-K/L

```
A. PENDAHULUAN
   1. Latar Belakang dan Dasar Hukum (Pasal 61 PMK 107/2024)
   2. Tujuan Reviu (keyakinan terbatas, kepatuhan kaidah penganggaran)
   3. Ruang Lingkup (tahap reviu, unit kerja, tahun anggaran, total pagu)
   4. Metodologi (desk review — penelaahan dokumen RKA-K/L)
   5. Jangka Waktu dan Komposisi Tim

B. GAMBARAN UMUM RKA-K/L
   [Total pagu, jumlah Program/Kegiatan/Output, sumber dana,
    perbandingan dengan pagu tahun sebelumnya jika relevan]

C. HASIL REVIU
   C.1 Aspek Kelayakan Anggaran vs SBM/SBK/SSB
       [Tabel dan catatan: komponen yang melebihi/sesuai standar]
   C.2 Aspek Kepatuhan Kaidah Penganggaran
       [Catatan terkait klasifikasi, duplikasi, nomenklatur]
   C.3 Aspek Penandaan Anggaran
       [Status penandaan per keluaran]
   C.4 Aspek Kelengkapan Dokumen
       [Matriks: Kegiatan | KAK | RAB | RKA Satker | Status]
   C.5 Aspek Kelayakan Rincian Anggaran Baru
       [Catatan per kegiatan/output baru yang direviu]
   C.6 Aspek Pengalokasian Tematik
       [Verifikasi pemenuhan alokasi tematik]

   [Catatan reviu lengkap: Kondisi → Kriteria → Akibat → Rekomendasi]

D. SIMPULAN
   [Keyakinan terbatas — lihat panduan bahasa di bawah]

E. REKOMENDASI
   [Kompilasi rekomendasi, dikelompokkan per aspek dan prioritas]

F. APRESIASI
   [Hal-hal yang sudah baik — reviu ini preventif dan membangun]
```

---

## Panduan Bahasa LHR

**Simpulan — tidak ditemukan catatan signifikan:**
> *"Berdasarkan hasil reviu secara terbatas atas RKA-K/L [Nama K/L] Tahun Anggaran [YYYY] pada tahap [pagu indikatif/pagu anggaran/pagu alokasi], tidak terdapat hal-hal yang membuat kami yakin bahwa perencanaan anggaran tidak disusun sesuai dengan kaidah penganggaran yang berlaku."*

**Simpulan — ditemukan catatan:**
> *"Berdasarkan hasil reviu secara terbatas atas RKA-K/L [Nama K/L] Tahun Anggaran [YYYY] pada tahap [pagu indikatif/pagu anggaran/pagu alokasi], ditemukan [N] catatan yang perlu ditindaklanjuti sebelum RKA-K/L difinalisasi, sebagaimana diuraikan dalam laporan ini."*

**Bahasa umum:**
- Gunakan "catatan" bukan "temuan"
- Gunakan bahasa membangun — reviu ini preventif
- Hindari generalisasi — sebutkan Program/Kegiatan/baris anggaran yang spesifik

---

## Batasan

- JANGAN menganalisis Sebab — reviu tidak menginvestigasi penyebab
- JANGAN menghitung kerugian negara — RKA-K/L belum dilaksanakan
- JANGAN menilai kebijakan (apakah program ini perlu ada) — hanya kualitas perencanaan
- Jika SBM/SBK tidak tersedia sebagai referensi: **nyatakan keterbatasan** dalam LHR
- Catatan harus spesifik: sebutkan Program/Kegiatan/kode/baris anggaran yang dimaksud

---

## Referensi yang Digunakan

| Dokumen | Lokasi | Isi |
|---------|--------|-----|
| Pedoman Reviu PMK 107/2024 | `references/01-pmk-107-2024-pedoman-reviu.md` | Pasal 61, 6 aspek reviu, checklist, red flag |
| PMK SBM (SBM tahun berjalan) | `references/02-sbm-[tahun].md` | Satuan biaya input (belum tersedia — perlu disiapkan) |
| Klasifikasi Anggaran & Akun | `references/03-klasifikasi-anggaran.md` | PMK 102/2018 jo. 187/2019: klasifikasi jenis belanja, bagan akun standar, red flags salah klasifikasi, decision tree |
| **Kriteria Substansi TOR (IR2)** | `references/04-kriteria-substansi-tor.md` | Ringkasan kriteria 7 blok substansi TOR/KAK Inspektorat II + 27 butir aspek reviu Renja per tahap pagu |
| Matriks lengkap kriteria TOR | `references/04-kriteria-kerangka-tor.xlsx` | File sumber Excel — pembanding PMK 107, PMK 62, Bappenas, DJED, IR2 |
| Shared Kinerja References | `shared-kinerja-references/PANDUAN.md` | Perbandingan 4 skill kinerja 