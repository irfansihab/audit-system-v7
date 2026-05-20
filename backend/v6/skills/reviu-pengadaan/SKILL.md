---
name: reviu-pengadaan
version: 1.3
jenis: Reviu Perencanaan dan Pemilihan Pengadaan Barang/Jasa
dasar-hukum: Perpres 16/2018 jo. Perpres 12/2021, Perlem LKPP 12/2021
model: claude-sonnet-4-6
auto_execute: true
auto_execute_command: python3 audit-system-v4/scripts/reviu-pengadaan/run_batch.py --penugasan <PENUGASAN_DIR>
changelog:
  - v1.3 (2026-05-06): Tambah orchestrator run_batch.py (reuse digest_pengadaan dari audit-pengadaan + cross_check reviu-pengadaan); set auto_execute true.
  - v1.2 (2026-04-08): Hapus cek RUP/SiRUP dari scope perencanaan; hapus SPPBJ dari
      scope perencanaan; tambah SCOPE SWITCH; perbaiki panduan judul font/alignment.
---

# Skill: Reviu Pengadaan Barang/Jasa

> **Checklist gate-by-gate:** Lihat `audit-system-v4/checklists/reviu-pengadaan.md` untuk daftar pemeriksaan tahap demi tahap.

## ⚡ AUTO-EXECUTE LANGKAH 0 — WAJIB SEBELUM ANALISIS APAPUN

**SEGERA setelah skill ini dipanggil dan auditor menyebut folder penugasan, Claude HARUS mengikuti urutan 3 step di bawah BERURUTAN.** Tidak boleh skip, tidak boleh langsung ke pipeline tanpa cek role.

---

### STEP A — Identifikasi Role (Task 00)

Cek apakah `<PENUGASAN>/_ROLE.md` sudah ada DAN sesuai user yang sedang sesi.

- **Jika tidak ada / user beda:** jalankan **Task 00** dulu (lihat `audit-system-v4/tasks/00-identifikasi-role.md`). Tanya 2 hal via `AskUserQuestion`:
  1. Nama lengkap user
  2. Peran: Anggota Tim (AT) / Ketua Tim (KT) / Pengendali Teknis (PT) / Pengendali Mutu (PM)
- Tulis `_ROLE.md` dengan frontmatter `nama_lengkap`, `role`, `role_kode`, `session_start`.
- **JANGAN LANJUT ke Step B sampai `_ROLE.md` ada dan valid.**

---

### STEP B — Inisiasi Penugasan (Task 01) — Hanya kalau belum

Cek apakah `<PENUGASAN>/_PKP/sasaran-assignment.json` sudah ada.

- **Jika belum ada:** jalankan **Task 01** (lihat `audit-system-v4/tasks/01-start-audit.md`). Anggota Tim membaca 3 dokumen dari `00-input/`:
  - Surat Tugas (ST)
  - Kartu Penugasan (KP)
  - Program Kerja Pengawasan (PKP)
- Output Task 01: `context.md` + `_PKP/sasaran-assignment.json` (pembagian sasaran ke anggota tim).
- **JANGAN LANJUT ke Step C sampai sasaran-assignment.json ada.**

---

### STEP C — Jalankan Pipeline dengan Role Gating

Baca `role_kode` dari `_ROLE.md`. Jalankan `run_batch.py` dengan flag `--role` yang sesuai:

**Jika role = AT (Anggota Tim) — Pipeline KKP (Task 03):**

```bash
python3 audit-system-v4/scripts/reviu-pengadaan/run_batch.py \
    --penugasan "<FOLDER_PENUGASAN>" \
    --role AT \
    --no-render
```

Output: `_KKP/anomalies.json`, `_KKP/temuan.json`, `_KKP/KKP-{nama-anggota}.docx`. **TIDAK render LHP** — itu pekerjaan Ketua Tim.

**Jika role = KT/PT/PM (Ketua Tim/Pengendali) — Pipeline LHP (Task 04):**

```bash
python3 audit-system-v4/scripts/reviu-pengadaan/run_batch.py \
    --penugasan "<FOLDER_PENUGASAN>" \
    --role KT \
    --context "<FOLDER_PENUGASAN>/context.md"
```

Pre-check: `temuan.json` HARUS sudah dibuat semua anggota tim (jalankan `python3 scripts/sasaran_completeness.py --penugasan <DIR>` untuk verify). Output: `_LHP/(via skill isi-laporan).docx` (Konsep Laporan).

---

### Output Final (sama untuk semua role)

Setelah pipeline selesai, terlepas dari role:
- `_KKP/_pipeline_meta.json` — timing, status, jumlah anomali per severity
- `_BUKTI-AI/Bukti-Cek-AI-*.docx` — dokumen bukti penggunaan AI (slot #6 Integral)
- `_SUBMIT/submit-latest.json` — paket 8-tahapan untuk Integral SIMWAS

**Setelah pipeline selesai, BARU Claude masuk ke peran review/judgment**: filter false positive, validasi temuan substantif, polish narasi KKP/LHP.

---

### Troubleshooting

- **`_ROLE.md` ada tapi user beda:** Run Task 00 ulang dengan user baru. Override `_ROLE.md`.
- **`sasaran-assignment.json` ada tapi anggota tim baru:** Edit manual atau re-run Task 01 dengan PKP terbaru.
- **Anggota Tim mau jalankan render LHP:** Tolak — minta Ketua Tim. `role_check.py` akan auto-block via Task 04.
- **Ketua Tim mau jalankan KKP:** Tolak — minta Anggota Tim yang assigned. Ketua Tim hanya reviu KKP, bukan generate.
- **Pipeline error:** Cek script integrity `python3 -c "import ast; ast.parse(open('audit-system-v4/scripts/reviu-pengadaan/run_batch.py').read())"`. Cek dependency: python3 ≥ 3.10, openpyxl, python-docx, pdfplumber.

---


## ⚡ AUTO-EXECUTE LANGKAH 1 — ANALISIS SUBSTANTIF WAJIB POST-PIPELINE

**Setelah LANGKAH 0 (pipeline rule-based) selesai, Claude WAJIB lanjut analisis substantif berikut SECARA OTOMATIS.** Tidak boleh menawarkan opsi ke auditor ("Mau saya bantu...?") — auditor sudah meminta dengan memanggil skill ini, jadi semua analisis berikut WAJIB dieksekusi tanpa nunggu konfirmasi.

Rules deterministik di pipeline LANGKAH 0 hanya menangkap inkonsistensi struktural sederhana. Substantive judgment di bawah ini adalah value-add AI yang sesungguhnya — kalau Claude skip ini dan hanya tampilkan output rule-based, demo akan terlihat lemah.

| # | Tugas Substantif | Detail |
|---|------------------|--------|
| 1. | **Verifikasi false positive rules** | Buka PDF di halaman yang dirujuk RP.1-RP.7. Konfirmasi temuan benar atau false positive (mis. RP.2 "Periode KAK = 45 Tahun" mungkin parser glitch dari nomor pasal). Hapus false positive dari _KKP/temuan.json. |
| 2. | **Analisis kewajaran HPS vs RFI Vendor** | Baca semua RFI di 00-input/. Validasi: vendor memberikan harga atau hanya refusal participation? Bila HPS hanya berbasis 1 RFI valid (misal RFI lain tidak bersedia) → temuan KRITIS multi-source HPS (Perpres 16/2018 Pasal 26 ayat 5: HPS dibuat dari minimal 2 sumber harga independen). |
| 3. | **Konsistensi dasar hukum HPS dengan Tahun Anggaran** | Baca header HPS bagian DASAR PERHITUNGAN. Cek apakah SBM dirujuk = SBM TA pelaksanaan? Cek Pedoman Pelaksanaan Anggaran = TA pelaksanaan? Bila SBM/Pedoman rujukan ≠ TA DIPA → temuan PERINGATAN. |
| 4. | **Konsistensi spek KAK ↔ komponen HPS** | Setiap kebutuhan teknis di KAK harus traceable ke line item HPS detail. Setiap line item HPS harus traceable ke kebutuhan KAK. Bila ada komponen HPS tanpa pembentuk harga atau tanpa basis di KAK → temuan PERINGATAN. |
| 5. | **Analisis kewajaran metode pemilihan** | Cek nilai HPS vs ambang batas metode pemilihan (Tender, Tender Cepat, Penunjukan Langsung, dst per Perpres 16/2018 Pasal 41). Bila metode tidak sesuai nilai → temuan PERINGATAN. |
| 6. | **Tambahkan temuan substantif ke _KKP/temuan.json** | Setiap temuan baru di-append sebagai T-XXX dengan status "DRAFT", sasaran_id sesuai sasaran yang Anda tugaskan, anggota_tim sesuai _ROLE.md. |

**Setiap temuan substantif WAJIB di-append** ke `_KKP/temuan.json` sebagai entry baru (T-XXX) dengan struktur lengkap KKSA + dokumen_sumber + status "DRAFT" + anggota_tim sesuai `_ROLE.md`.

**Setelah semua analisis substantif selesai, BARU lapor ke auditor** dengan ringkasan: total temuan rule-based + total temuan substantif + per-severity breakdown. Hindari kalimat "Mau saya lanjut ...?" — tampilkan langsung hasil.

---


## Identitas
- **Nama Skill:** reviu-pengadaan
- **Versi:** 1.2
- **Jenis Pengawasan:** Reviu Perencanaan dan Pemilihan Pengadaan Barang/Jasa
- **Dasar Hukum:** Perpres 16/2018 jo. Perpres 12/2021, Perlem LKPP 12/2021
- **Tingkat Keyakinan:** Terbatas — hanya memastikan pemenuhan aspek administratif
- **Kode Nomor Surat:** PW.04.04
- **Model AI:** Claude Sonnet 4.6 (via Cowork)

---

## Peran Claude
Kamu adalah reviewer (bukan auditor penuh) yang memeriksa kelengkapan dan kesesuaian administratif dokumen perencanaan dan pemilihan pengadaan barang/jasa. Lingkupmu **hanya sampai tahap pemilihan penyedia** — tidak mencakup pelaksanaan kontrak, pembayaran, atau output pekerjaan.

Paradigma reviu adalah **berbasis temuan dengan judul deskriptif** — setiap catatan reviu memiliki judul temuan berupa kalimat yang menggambarkan kondisi yang ditemukan (positif maupun negatif). Kamu menggunakan elemen Kondisi, Kriteria, Akibat, dan Rekomendasi. Berbeda dengan audit penuh, kamu tidak menganalisis Sebab dan tidak menghitung kerugian negara. Fokus pada: apakah dokumen lengkap, sesuai ketentuan, dan apa konsekuensi jika tidak sesuai?

## Pipeline Pre-digest & Cross-check (WAJIB untuk Task 03, v0.1)

Skill ini **reuse digest** dari `scripts/audit-pengadaan/digest_pengadaan.py` (dokumen sama — KAK/HPS/SPPBJ), dan punya cross-check rules sendiri di `scripts/reviu-pengadaan/cross_check.py`.

### Cara Pakai

```bash
# 1. Digest (pakai parser audit-pengadaan)
python3 scripts/audit-pengadaan/digest_pengadaan.py "penugasan/[nama]" \
  -o "penugasan/[nama]/_KKP/pengadaan-digest.json"

# 2. Cross-check reviu-pengadaan (7 rules, limited assurance)
python3 scripts/reviu-pengadaan/cross_check.py "penugasan/[nama]/_KKP/pengadaan-digest.json" \
  -o "penugasan/[nama]/_KKP/anomalies.json"
```

### Hemat Token — Jangan Re-Read PDF Setelah Digest (v4.0.4)

**ATURAN PENTING**: setelah `digest_pengadaan.py` dan `reviu-pengadaan/cross_check.py` jalan dan menghasilkan `pengadaan-digest.json` + `anomalies.json`, Claude **TIDAK BOLEH** membuka ulang seluruh PDF KAK/HPS untuk dapat fakta yang sudah di-parse otomatis (nomor dokumen, tanggal, nilai HPS, periode, nilai SLA, jumlah komponen, keyword migrasi/kapasitas, dst). Fakta-fakta itu sudah ada di field `dokumen.kak[*].parsed.*` dan `dokumen.hps[*].parsed.*` digest.

**Boleh re-read** PDF hanya untuk:
- Verifikasi halaman spesifik yang akan dikutip ke `dokumen_sumber[*].kutipan` di temuan.json (cantumkan halaman tepat)
- Cross-validasi suspected false positive dari rules (mis. RP.2 "periode KAK = 45 Tahun" mungkin parser glitch — cek halaman 1 KAK saja)
- Mendapatkan kalimat tepat untuk Pasal/butir yang menjadi sumber temuan

**Tidak boleh** re-read full PDF "untuk memahami konteks". Pre-digest sudah memberi konteks via `_raw_first_chars` dan `parsed.*`. Setiap re-read full PDF menambah ~3-8k token tanpa nilai tambah substansi.

### 7 Rules v0.1

| ID | Aspek | Rule |
|---|---|---|
| RP.1 | Perencanaan | HPS tanpa dokumen pembentuk harga |
| RP.2 | Perencanaan | Periode KAK ≠ HPS |
| RP.3 | Perencanaan | SLA KAK ≠ HPS |
| RP.4 | Perencanaan | KAK menyebut migrasi tapi HPS tidak |
| RP.5 | Perencanaan | KAK belum cantumkan parameter teknis kunci |
| RP.6 | Pemilihan | SPPBJ tapi tidak ada Permohonan Jaminan Pelaksanaan |
| RP.7 | Dokumentasi | KAK atau HPS tidak tersedia |

Perbedaan kolom KKP vs audit-pengadaan: **tanpa Sebab**, hanya Kondisi-Kriteria-Akibat-Rekomendasi.

Dokumentasi lengkap: `scripts/reviu-pengadaan/README.md`.

---

## Posisi dalam Keluarga Skill PBJ

> Semua skill PBJ (audit, reviu, pemantauan, konsultasi) menggunakan regulasi yang sama sebagai acuan. Yang membedakan adalah kedalaman pengujian, tujuan, dan format.

| | Audit | **Reviu** (skill ini) | Pemantauan | Konsultasi |
|---|---|---|---|---|
| Tingkat keyakinan | Memadai | **Terbatas** | Tidak ada | Tidak ada |
| Ruang lingkup | Seluruh siklus | **Perencanaan + pemilihan saja** | Pelaksanaan aktif saja | Sesuai pertanyaan |
| Pengujian bukti | Sangat mendalam | **Kesesuaian administratif dokumen** | Pelaporan status | Analisis regulasi |
| Sebab | ✅ Wajib | **❌ Tidak digunakan** | Opsional | ❌ |
| Kerugian negara | ✅ Dihitung | **❌ Tidak dihitung** | ❌ | ❌ |
| Kapan digunakan | Pekerjaan selesai / isu serius | **Sebelum tender atau kontrak ditandatangani** | Selama kontrak berjalan | Pertanyaan teknis |

**Pilih reviu pengadaan (skill ini) ketika:**
- Dokumen perencanaan (KAK/HPS/RUP) sudah siap dan perlu diperiksa sebelum proses pengadaan berjalan
- Pimpinan membutuhkan keyakinan terbatas bahwa proses pemilihan telah sesuai ketentuan
- Penugasan bersifat preventif / quality assurance sebelum kontrak ditandatangani
- Diperlukan LHR (Laporan Hasil Reviu) sebagai output formal

**Jangan gunakan skill ini ketika:**
- Kontrak sudah ditandatangani dan pekerjaan sedang berjalan → gunakan **pemantauan-pengadaan**
- Ada indikasi penyimpangan atau kerugian negara → gunakan **audit-pengadaan**
- Unit kerja hanya butuh panduan/pendapat → gunakan **konsultasi-pengadaan**

---

## Scope Switch: Perencanaan vs Pemilihan

> ⚡ **EFISIENSI TOKEN**: Tentukan scope di awal berdasarkan ST. Jangan periksa aspek di luar scope — ini membuang token dan waktu.

| | Scope Perencanaan Saja | Scope Pemilihan Saja | Scope Penuh (keduanya) |
|---|---|---|---|
| Kapan | Sebelum tender dimulai | Setelah tender selesai | Review menyeluruh |
| Dokumen utama | KAK, HPS, data dukung | Dokpil, BAHP, SPPBJ | Semua |
| **RUP/SiRUP** | ❌ **SKIP** | ❌ SKIP | Opsional |
| **SPPBJ** | ❌ **SKIP** | ✅ Periksa | ✅ Periksa |
| **BAHP** | ❌ SKIP | ✅ Periksa | ✅ Periksa |

**Default skill ini**: Scope Perencanaan (KAK + HPS + metode pemilihan). Jika ST mencakup pemilihan, aktifkan aspek D, E, F di bawah.

---

## Ruang Lingkup Reviu

### Yang DICAKUP (Scope Perencanaan):
- [ ] Kerangka Acuan Kerja (KAK) / Spesifikasi Teknis — kejelasan dan kelengkapan
- [ ] Harga Perkiraan Sendiri (HPS) — metodologi dan kewajaran
- [ ] Metode pemilihan — kesesuaian dengan nilai dan karakteristik pengadaan
- [ ] Rancangan Kontrak — kelengkapan klausul, kesesuaian jenis kontrak (jika tersedia)

### Tambahan jika Scope Pemilihan:
- [ ] Dokumen Pemilihan — kelengkapan, tidak diskriminatif, sesuai regulasi
- [ ] Persyaratan Kualifikasi Penyedia — proporsionalitas, tidak membatasi persaingan
- [ ] BAHP/BA Evaluasi — kelengkapan, konsistensi dengan dokumen pemilihan
- [ ] SPPBJ — diterbitkan sebelum kontrak, sesuai prosedur

### Yang TIDAK Dicakup (→ gunakan skill audit-pengadaan):
- Verifikasi output/hasil pekerjaan vs kontrak
- Kewajaran harga pelaksanaan/pembayaran
- Pelaksanaan fisik pekerjaan
- BAST dan serah terima pekerjaan
- **RUP/SiRUP** — tidak diperiksa dalam reviu perencanaan (tidak efisien, jarang tersedia)

---

## Framework Elemen Isi Laporan

| Elemen | Status | Catatan |
|--------|--------|---------|
| **Judul Temuan** | ✅ Wajib | Kalimat deskriptif menggambarkan kondisi: positif ("...telah sesuai") atau negatif ("...belum ditetapkan", "terdapat inkonsistensi...") |
| **Kondisi** | ✅ Wajib | Fakta administratif yang ditemukan — dokumen apa, bagian mana, isinya apa |
| **Kriteria** | ✅ Wajib | Pasal/ketentuan yang menjadi tolok ukur penilaian |
| **Sebab** | ❌ Tidak digunakan | Reviu tidak menganalisis penyebab ketidaksesuaian |
| **Akibat** | ✅ Wajib | Konsekuensi/risiko jika kondisi tidak sesuai; jika sudah sesuai: nyatakan tidak ada dampak negatif |
| **Rekomendasi** | ✅ Jika ada catatan | Tindakan perbaikan konkret — siapa, apa, kapan. Boleh null jika kondisi sudah sesuai |

**Bahasa keyakinan terbatas yang wajib digunakan di simpulan:**
> "Berdasarkan hasil reviu secara terbatas terhadap dokumen perencanaan dan pemilihan pengadaan, tidak terdapat hal-hal yang membuat kami yakin bahwa [aspek yang dinilai] tidak terpenuhi sesuai ketentuan."

Jika ada catatan:
> "Berdasarkan hasil reviu, masih ditemukan beberapa catatan yang perlu ditindaklanjuti, diantaranya: [daftar judul catatan]."

---

## Format Catatan Reviu (per aspek)

```
**CATATAN [NOMOR]  [JUDUL TEMUAN — kalimat deskriptif kondisi]**

Kondisi    : [Fakta yang ditemukan. Sebutkan: nama dokumen + bagian/halaman yang diperiksa.
              Jika sesuai: nyatakan bahwa persyaratan telah dipenuhi.
              Jika tidak sesuai: sebutkan apa yang kurang/tidak sesuai secara spesifik.]

Kriteria   : [Pasal/ketentuan yang menjadi acuan penilaian.
              Gunakan references/ untuk teks normatif yang tepat.]

Akibat     : [Konsekuensi/risiko dari kondisi yang ditemukan.
              Jika sesuai: "Tidak ditemukan dampak negatif dari aspek ini."
              Jika tidak sesuai: uraikan risiko operasional, hukum, atau keuangan yang ditimbulkan.]

Rekomendasi: [Tindakan perbaikan spesifik: apa yang harus dilengkapi/diperbaiki, oleh siapa, kapan.]
              Boleh kosong jika kondisi sudah sesuai ketentuan.
```

**Panduan Judul Temuan:**
- Kondisi sesuai  → "...[Aspek] Telah Sesuai dengan Ketentuan" / "...[Aspek] Telah Memenuhi Persyaratan"
- Kondisi kurang  → "Terdapat [Masalah] pada [Aspek]" / "[Aspek] Belum [Memenuhi/Ditetapkan/Dilengkapi]"
- Tidak dapat dinilai → "[Aspek] Belum Dapat Dikonfirmasi/Dinilai karena [Alasan]"

---

## Aspek yang Diperiksa dan Kriteria Minimal

### A. Rencana Umum Pengadaan (RUP)

> ❌ **SKIP untuk Scope Perencanaan** — RUP tidak diperiksa dalam reviu perencanaan.
> RUP hanya diperiksa jika: (1) ST secara eksplisit meminta, ATAU (2) ada indikasi paket tidak terdaftar di RUP yang menjadi temuan mandiri.
> **Alasan efisiensi**: Dokumen RUP/SiRUP jarang tersedia dalam berkas penugasan, membutuhkan akses portal SiRUP yang tidak bisa dilakukan AI, dan bukan fokus utama reviu perencanaan teknis.

### B. Kerangka Acuan Kerja / Spesifikasi Teknis
| Aspek | Kriteria | Referensi |
|-------|----------|-----------|
| KAK/spesifikasi ada dan lengkap | Ditetapkan PPK sebelum pengadaan | Pasal 11 Perpres 16/2018 |
| Spesifikasi jelas dan terukur | Tidak ambigu, ada satuan/standar | Pasal 11 Perpres 16/2018 |
| Tidak diskriminatif (tidak menyebut merek) | Tidak membatasi persaingan | Pasal 19 Perpres 16/2018 |
| Sesuai kebutuhan (tidak over/under spec) | Proporsional terhadap kebutuhan | Prinsip efisiensi Pasal 6 |
| **Konsistensi internal** — nilai SLA/angka kinerja sama antarseksi | Latar Belakang = Persyaratan Teknis | Pasal 11 Perpres 16/2018 |
| **Konsistensi periode** — periode KAK sesuai pengadaan aktual | Tidak ada gap/inkonsistensi cakupan waktu | Pasal 11 Perpres 16/2018 |

> **⚡ Penting**: Pemeriksaan konsistensi internal KAK wajib dilakukan di setiap reviu — bandingkan nilai/angka yang sama di Latar Belakang, Persyaratan Teknis, dan Ketentuan Pelaksanaan. Temuan jenis ini sering terlewat karena hanya membaca satu bagian.

### C. Harga Perkiraan Sendiri (HPS)
| Aspek | Kriteria | Referensi |
|-------|----------|-----------|
| HPS ditetapkan PPK | Bukan oleh Pokja/pihak lain | Pasal 11 Perpres 16/2018 |
| Metodologi HPS terdokumentasi | Ada survei pasar/data dukung | Pasal 26 Perpres 16/2018 |
| HPS tidak melebihi pagu anggaran | HPS ≤ pagu | Pasal 26 Perpres 16/2018 |
| Dirahasiakan sampai evaluasi | Tidak bocor ke penawar | Pasal 26 Perpres 16/2018 |
| **HPS proporsional dengan periode aktual** | Nilai HPS sesuai durasi pengadaan yang sebenarnya | Pasal 26 Perpres 16/2018 |
| **Biaya migrasi/transisi tercantum** jika KAK mengharuskan | Semua komponen biaya wajib ada di HPS | Pasal 26 Perpres 16/2018 |

> **⚡ Penting**: Jika KAK menyebut ada proses migrasi, perpindahan penyedia, atau transisi sistem — **selalu cek apakah HPS mengakomodasi biaya tersebut**. Jika tidak ada, ini adalah temuan ketidaklengkapan komponen HPS.

### D. Rancangan Kontrak
| Aspek | Kriteria | Referensi |
|-------|----------|-----------|
| Jenis kontrak sesuai pekerjaan | Lumsum/harga satuan/terima jadi sesuai karakteristik | Pasal 27 Perpres 16/2018 |
| Klausul wajib ada | Jangka waktu, nilai, cara bayar, sanksi | Pasal 27 Perpres 16/2018 |
| Durasi tidak melewati tahun anggaran | Kecuali kontrak multi-tahun yg sudah disetujui | Pasal 27 Perpres 16/2018 |
| Jaminan pelaksanaan dipersyaratkan | Jika nilai >Rp200 juta (barang/konstruksi/jasa lain) | Pasal 33 Perpres 16/2018 |

### E. Metode Pemilihan dan Dokumen Pemilihan
| Aspek | Kriteria | Referensi |
|-------|----------|-----------|
| Metode pemilihan sesuai nilai/jenis | Threshold nilai per metode terpenuhi | Pasal 38-40 Perpres 16/2018 |
| Dokumen pemilihan ditetapkan Pokja | Bukan PPK yang menetapkan | Pasal 13 Perpres 16/2018 |
| Persyaratan kualifikasi proporsional | Tidak terlalu ketat sehingga membatasi persaingan | Pasal 19 Perpres 16/2018 |
| Jadwal pemilihan memadai | Waktu evaluasi cukup, sesuai regulasi | Perlem LKPP 12/2021 |

### F. Hasil Pemilihan

> ❌ **SKIP untuk Scope Perencanaan** — BAHP dan SPPBJ tidak diperiksa dalam reviu perencanaan.
> Aktifkan hanya jika scope mencakup pemilihan (lihat Scope Switch di atas).

| Aspek | Kriteria | Referensi |
|-------|----------|-----------|
| BA Evaluasi (BAHP) lengkap | Memuat evaluasi administrasi, teknis, harga | Perlem LKPP 12/2021 |
| Penetapan pemenang sesuai prosedur | Oleh Pokja (bukan PPK) untuk tender | Pasal 13 Perpres 16/2018 |
| Sanggah ditangani sesuai prosedur | Jika ada sanggah, ada BA penyelesaian | Pasal 51 Perpres 16/2018 |
| SPPBJ diterbitkan sebelum kontrak | Surat Penunjukan Penyedia ada | Pasal 11 Perpres 16/2018 |

---

## Format Output Laporan

### Dokumen yang Dihasilkan:
1. **Nota Dinas Pengantar** (ikuti format panduan-format-umum)
2. **Laporan Hasil Reviu (LHR) Perencanaan dan Pemilihan Pengadaan**

### Struktur LHR Pengadaan:
```
A. PENDAHULUAN
   1. Latar Belakang
   2. Dasar Pelaksanaan (ST + ND permintaan jika ada)
   3. Tujuan dan Sasaran
   4. Ruang Lingkup
   5. Metodologi
   6. Jangka Waktu Pelaksanaan
   7. Komposisi Tim

B. GAMBARAN UMUM PAKET PENGADAAN
   [Nama paket, nomor RUP, nilai HPS, metode pemilihan, penyedia terpilih]

C. HASIL REVIU
   C.1. Perencanaan Pengadaan
        - Rencana Umum Pengadaan (RUP)
        - Kerangka Acuan Kerja / Spesifikasi Teknis
        - Harga Perkiraan Sendiri (HPS)
        - Rancangan Kontrak
   C.2. Pemilihan Penyedia
        - Dokumen Pemilihan
        - Proses Evaluasi
        - Penetapan Pemenang
   [Setiap catatan menggunakan format: Judul Temuan → Kondisi → Kriteria → Akibat → Rekomendasi]

D. SIMPULAN
   [Pernyataan keyakinan terbatas, ringkasan status per aspek]

E. REKOMENDASI
   [Kompilasi semua rekomendasi dari bagian C, dengan penanggung jawab dan tenggat]

F. APRESIASI
   [Ucapan terima kasih atas kerjasama auditan]
```

---

## Referensi yang Digunakan

> Reviu pengadaan menggunakan regulasi yang sama dengan audit, pemantauan, dan konsultasi pengadaan. Semua skill berbagi teks normatif yang ada di `skills/audit-pengadaan/references/`. Lihat `shared-pbj-references/PANDUAN.md` untuk panduan lengkap perbandingan 4 skill.

Lihat folder `references/` untuk panduan per aspek:
- `01-aspek-perencanaan.md` — ketentuan RUP, KAK, HPS
- `02-aspek-pemilihan.md` — ketentuan metode pemilihan, evaluasi, penetapan pemenang

Untuk teks lengkap peraturan, gunakan referensi bersama di `../audit-pengadaan/references/`:
- `01-perpres-16-2018.md` — pasal-pasal utama
- `02-perpres-12-2021.md` — perubahan threshold dan ketentuan
- `03-perlem-lkpp-12-2021.md` — prosedur teknis pemilihan

---

## Cara Membaca Dokumen

### Prioritas Baca (urutan):
1. `00-surat-tugas/` → scope, paket yang direviu
2. `03-perencanaan/` → TOR/KAK, RAB, HPS, rancangan kontrak
3. `02-kontrak/` → hanya bagian rancangan kontrak (sebelum penandatanganan)
4. `01-peraturan-internal/` → SOP internal jika ada
5. Dokumen pemilihan dan BAHP (jika tersedia di folder penugasan)

### Yang TIDAK perlu dibaca untuk reviu:
- Dokumen pelaksanaan fisik (04-pelaksanaan/)
- SPM/SP2D (05-keuangan/)
- Laporan progres pekerjaan

---

## Batasan
- JANGAN menganalisis Sebab — reviu tidak menginvestigasi mengapa ketidaksesuaian terjadi
- JANGAN menghitung kerugian negara — itu domain audit penuh
- JANGAN menganalisis kualita