# Template Standar KP + PKP — Indeks dan Konvensi

**Versi**: 1.0 (April 2026)
**Pemilik**: Inspektorat II, Kementerian Komunikasi dan Digital RI
**Digunakan oleh**: Task 02b — Jalur B (Template Standar)

---

## Tujuan

Menstandarkan Kartu Penugasan (KP) dan Program Kerja Pengawasan (PKP) untuk 6 jenis pengawasan yang **struktur sasaran dan langkah kerjanya stabil** dari penugasan ke penugasan. Dengan template ini, pembuatan KP + PKP cukup dengan mengganti 4 variabel dinamis:
1. **Objek** pengawasan (unit/satker yang diperiksa)
2. **Tanggal** pengawasan (mulai–selesai, termasuk tahun)
3. **Tim** auditor (PM/PT/KT/AT dari ST)
4. **Tingkat Risiko** unit/aktivitas (dari ST atau auditor)

Hal lain (tujuan, sasaran, ruang lingkup, metodologi, langkah kerja, alokasi hari kerja) sudah terstandar sesuai regulasi dan SKILL.md masing-masing jenis.

---

## Cakupan — 6 Jenis Pengawasan

| No | Skill | Kode Surat | Dasar Hukum Utama |
|----|-------|------------|-------------------|
| 1 | `reviu-rka-kl` | PW.04.04 | PMK 107/2024 |
| 2 | `pemantauan-pengadaan` | PW.04.06 | Perpres 16/2018 jo. 12/2021 |
| 3 | `evaluasi-sakip` | PW.04.05 | PermenPAN-RB 88/2021 |
| 4 | `evaluasi-spip` | PW.04.05 | PP 60/2008, Perka BPKP 5/2021 |
| 5 | `evaluasi-reformasi-birokrasi` | PW.04.03 | PermenPAN-RB 3/2023 |
| 6 | `evaluasi-manajemen-risiko` | PW.04.05 | Pedoman Menkomdigi 6/2017, ISO 31000:2018 |

**Tidak termasuk (tetap bespoke / Jalur A):**
- `audit-kinerja` — butuh penajaman sasaran via Memo SP
- `audit-pengadaan` — langkah per paket pengadaan
- `reviu-pengadaan` — langkah per paket pengadaan
- `konsultasi-pengadaan` — advisory ad-hoc

---

## Struktur Folder

```
audit-system-v2/templates/kp-pkp/
├── TEMPLATE-INDEX-KP-PKP.md               ← file ini
├── reviu-rka-kl/
│   ├── KP-template.docx
│   └── PKP-template.docx
├── pemantauan-pengadaan/
│   ├── KP-template.docx
│   └── PKP-template.docx
├── evaluasi-sakip/
│   ├── KP-template.docx
│   └── PKP-template.docx
├── evaluasi-spip/
│   ├── KP-template.docx
│   └── PKP-template.docx
├── evaluasi-reformasi-birokrasi/
│   ├── KP-template.docx
│   └── PKP-template.docx
└── evaluasi-manajemen-risiko/
    ├── KP-template.docx
    └── PKP-template.docx
```

Total: **12 file .docx** (6 KP + 6 PKP).

---

## Konvensi Placeholder

Semua placeholder menggunakan format `{{NAMA_FIELD}}` (huruf kapital + garis bawah). Task 02b akan melakukan **find-replace** pada `word/document.xml` setelah unpack.

### A. Placeholder Identitas Penugasan (semua template)

| Placeholder | Deskripsi | Sumber | Contoh |
|-------------|-----------|--------|--------|
| `{{OBJEK}}` | Nama unit/satker/program yang diperiksa | ST | `Direktorat Jenderal Aplikasi Informatika` |
| `{{TAHUN}}` | Tahun anggaran/penugasan | ST | `2026` |
| `{{TGL_MULAI}}` | Tanggal mulai pengawasan | ST | `15 April 2026` |
| `{{TGL_SELESAI}}` | Tanggal selesai pengawasan | ST | `5 Mei 2026` |
| `{{JUMLAH_HARI}}` | Total hari kerja penugasan | Dihitung | `15 hari kerja` |
| `{{NOMOR_ST}}` | Nomor Surat Tugas | ST | `ST/254/IJ.3/KP.01.06/04/2026` |
| `{{TGL_ST}}` | Tanggal penerbitan ST | ST | `14 April 2026` |
| `{{TINGKAT_RISIKO}}` | Tinggi / Sedang / Rendah | ST atau auditor | `Sedang` |
| `{{CATATAN_PENUGASAN}}` | Catatan khusus di KP (opsional) | Auditor | `—` atau teks catatan |
| `{{CATATAN_PKP}}` | Catatan khusus di PKP (opsional) | Auditor | `—` atau teks catatan |

### B. Placeholder Tim Auditor (semua template)

Urutan tim: **Pengendali Mutu (PM) → Pengendali Teknis (PT) → Ketua Tim (KT) → Anggota Tim 1 (AT1) → Anggota Tim 2 (AT2)**.

| Placeholder | Deskripsi |
|-------------|-----------|
| `{{PM_NAMA}}` / `{{PM_NIP}}` / `{{PM_JABFUNG}}` | Pengendali Mutu — biasanya Inspektur |
| `{{PT_NAMA}}` / `{{PT_NIP}}` / `{{PT_JABFUNG}}` | Pengendali Teknis |
| `{{KT_NAMA}}` / `{{KT_NIP}}` / `{{KT_JABFUNG}}` | Ketua Tim |
| `{{AT1_NAMA}}` / `{{AT1_NIP}}` / `{{AT1_JABFUNG}}` | Anggota Tim 1 |
| `{{AT2_NAMA}}` / `{{AT2_NIP}}` / `{{AT2_JABFUNG}}` | Anggota Tim 2 (isi `-` jika tim hanya 4 orang) |
| `{{INSPEKTUR_NAMA}}` / `{{INSPEKTUR_NIP}}` | Penandatangan KP (umumnya = PM) |

### C. Placeholder Alokasi Waktu (PKP)

| Placeholder | Deskripsi | Default |
|-------------|-----------|---------|
| `{{HK_PERSIAPAN}}` | Hari kerja tahap persiapan | 2 |
| `{{HK_PELAKSANAAN}}` | Hari kerja tahap pelaksanaan | `JUMLAH_HARI − PERSIAPAN − PELAPORAN` |
| `{{HK_PELAPORAN}}` | Hari kerja tahap pelaporan | 3 |

### D. Placeholder Khusus per Jenis

| Placeholder | Dipakai oleh | Keterangan |
|-------------|--------------|------------|
| `{{TRIWULAN}}` | `evaluasi-reformasi-birokrasi` | Diisi `I`, `II`, `III`, atau `IV` sesuai periode evaluasi on-going |

---

## Aturan Anti-Halusinasi

1. **Field kosong → `[DIISI AUDITOR]`**. Jangan mengarang data yang tidak tersedia di ST.
2. **Jangan ubah struktur template** — hanya ganti `{{...}}`. Struktur (tabel, heading, urutan, bobot hari kerja) sudah sesuai regulasi.
3. **Jumlah hari di PKP = JUMLAH_HARI di KP**. Konsistensi wajib.
4. **Tim urut sesuai ST** (PM → PT → KT → AT1 → AT2). Jangan swap peran.
5. **Perubahan substansial** (tambah/ubah langkah kerja) hanya dilakukan atas permintaan auditor dengan alasan spesifik, dan **didokumentasikan** di `{{CATATAN_PKP}}`.

---

## Prosedur Generate (ringkas)

```
1. Baca context.md → Skill, Objek, Tanggal, Tim, Tingkat Risiko
2. Pilih folder template berdasarkan Skill
3. Hitung placeholder turunan (JUMLAH_HARI, HK_*, TRIWULAN)
4. Unpack template → edit XML (find-replace {{...}}) → repack
5. Simpan ke _KP/KP-[nomor-ST].docx dan _PKP/PKP-[nomor-ST].docx
6. Validate .docx (scripts/office/validate.py)
7. Update context.md
8. Minta konfirmasi auditor (GATE)
```

Detail prosedur ada di `tasks/02b-generate-kp-pkp.md` — BAGIAN C.

---

## Maintenance

### Menambahkan Placeholder Baru
1. Update template .docx (unpack → edit → pack → validate).
2. Tambahkan baris di tabel konvensi di atas.
3. Update `tasks/02b-generate-kp-pkp.md` → BAGIAN C.2.
4. Test dengan satu contoh penugasan end-to-end.

### Update Substansi Template (langkah kerja, sasaran, dll)
1. Update SKILL.md jenis tersebut terlebih dahulu (sumber kebenaran).
2. Regenerate template dengan `outputs/generate-kp-pkp-templates.js` (atau setara).
3. Validate semua 12 file dengan `scripts/office/validate.py`.
4. Tambahkan changelog di bagian bawah file ini.

### Menambah Jenis Baru ke Jalur B
1. Pastikan SKILL.md jenis tersebut memiliki: namaJenis, kodeSurat, keyakinan, dasarHukum, tujuan, sasaran (stabil), ruangLingkup, metodologi, output, jangkaWaktu, langkahKerja (stabil).
2. Tambahkan folder `templates/kp-pkp/[jenis]/`.
3. Tambahkan entry ke generator script.
4. Update routing di `tasks/02b-generate-kp-pkp.md` (tabel Jalur A/B dan tabel C.1).
5. Update tabel cakupan di file ini.

---

## Changelog

| Tanggal | Versi | Perubahan |
|---------|-------|-----------|
| 2026-04-16 | 1.0 | Rilis awal — 6 jenis standar (reviu-rka-kl, pemantauan-pengadaan, evaluasi-sakip, evaluasi-spip, evaluasi-reformasi-birokrasi, evaluasi-manajemen-risiko) |
