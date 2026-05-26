# Indeks Template LHP

> **Cara kerja**: Saat `isi-laporan` dijalankan, script `prepare_lhp.py` membaca `Jenis Pengawasan`
> dari `context.md` dan mencari template di folder ini. Template aktif disimpan dalam format `.docx`
> dan langsung disalin ke `_LHP/`. Google Doc ID tetap dicatat sebagai sumber master untuk update.

---

## Mapping: Jenis Pengawasan → Template

| Jenis Pengawasan | File Template | Google Doc ID (sumber master) |
|---|---|---|
| Audit Pengadaan | `Laporan Hasil Audit.docx` | `115W-Kh3UXqD4g6x9pbY9171Zd4f8FhSubIKMg6wyMe0` |
| Audit Kinerja | `Laporan Hasil Audit.docx` | `115W-Kh3UXqD4g6x9pbY9171Zd4f8FhSubIKMg6wyMe0` |
| Survei Pendahuluan Audit Kinerja | `Laporan Hasil Survei Pendahuluan Audit Kinerja.docx` | `1rEZbVDCXYvDuIZKjZEiBORYVzIvkcty5fSr6DoGkA-g` |
| Reviu Pengadaan | `Laporan Hasil Reviu Pengadaan.docx` | `1ICMT4v_lCJ3YQSg2HGMQUu-2fFhQEpSut6nn21KBJ_M` |
| Reviu RKA-KL / Reviu Rencana Kerja dan Anggaran | `Laporan Hasil Reviu Rencana Kerja dan Anggaran.docx` | `134YS99_T-NDcIWCrRCOlRVMzuj9_U_iDNlFiIXZ2NWU` |
| Reviu Revisi Rencana Kerja | `Laporan Hasil Reviu Revisi Rencana Kerja.docx` | `19X_0DmRqPshZVEJir5F7Tkrf1ihRV6jGHFluOhyed8o` |
| Reviu Dokumen Kontrak | `Laporan Hasil Reviu Dokumen Kontrak.docx` | `1XxKlUp9KzS9y-qenue2oku7Ck8ohfWLQsxAHSWDTJeU` |
| Reviu Laporan Kinerja | `Laporan Hasil Reviu Laporan Kinerja.docx` | `1W0OJo44guXMkvLSncIkvaVII7MRIPqC65Fv7Z-LEShs` |
| Reviu Dokumen Alokasi Anggaran / Direktif | `Laporan Hasil Reviu Dokumen Alokasi Anggaran untuk Pemenuhan Prioritas Direktif.docx` | `1--lKEHEa8LzdQyGXTqVIvi9gI9eSKbpCrVP4juD2P6c` |
| Evaluasi SAKIP / AKIP | `Laporan Hasil Evaluasi SAKIP.docx` | `1eYQB9isgX5DzNPYMlIDT19Xf0stM68L8gCc6qxKDemU` |
| Evaluasi Reformasi Birokrasi (RB) | `Laporan Hasil Evaluasi RB.docx` | `10blWGVjHqY_8H9k_3xpEuhGHeppcL2JSPaeH2b9LaLo` |
| Evaluasi Manajemen Risiko | `Laporan Hasil Evaluasi Manajemen Risiko.docx` | `1JSOCfPgSmSrDk8r5r6lpp-GSn0Trgw78lEAFGgrbsTw` |
| Evaluasi SPIP / Penjaminan Kualitas SPIP | `Laporan Hasil Penjaminan Kualitas Pelaksanaan SPIP.docx` | `1LA3rxYpOmllYZa-EeKAn1ZqFN5QafYU2d9c2nviNYbc` |
| Penjaminan Kualitas Penilaian Mandiri SPIP | `Laporan Hasil Penjaminan Kualitas atas Penilaian Mandiri Pelaksanaan SPIP.docx` | `19u-Q-SVPhxxxA-Z9hJM3zob8zW24V8Us5Z3KCchE9jo` |
| Pemantauan (umum) / Pemantauan Pengadaan | `Laporan Hasil Pemantauan.docx` | `1Brde5-7bYUIoVeo19CamwA_4OXWkFbbEkya25gtkSYY` |
| Pemantauan TLHP | `Laporan Hasil Pemantauan TLHP.docx` | `1ozzZmjoVTbl4C2Hgw8ivmYd15b7I6mhEC7TDAzteFuY` |
| Pendampingan Akuntabilitas PBJ | `Laporan Hasil Pendampingan Akuntabilitas Pengadaan Barang Jasa.docx` | `1VjyIYOru96iPX2NgLu2RSPDBOxEd9Ep8L-aNZRwVXPw` |

---

## Status Template

| Kategori | Template Tersedia | Format |
|---|---|---|
| ✅ Audit | 2 template | `.docx` |
| ✅ Reviu | 6 template | `.docx` |
| ✅ Evaluasi | 4 template | `.docx` |
| ✅ Pemantauan | 2 template | `.docx` |
| ✅ Pendampingan/Penjaminan | 3 template | `.docx` |

**Total: 16 template tersedia** (semua dalam format `.docx` lokal — dihapus 6 Mei 2026 dari shortcut `.gdoc` yang duplikat)

> **Catatan migrasi**: Sejak 6 Mei 2026, file shortcut `.gdoc` (187 byte) dihapus karena duplikat. Template aktif kini hanya `.docx` lokal.
> Master sumber tetap di Google Drive (lihat kolom Google Doc ID) — perubahan format dilakukan di Drive lalu re-export ke `.docx`.

---

## Cara Menambah / Update Template

1. Buka Google Doc master (lihat kolom **Google Doc ID** di tabel atas) di drive `inspektorat2.kominfo.2@gmail.com`
2. Edit sesuai kebutuhan (tambah/ubah placeholder, kop surat, dll.)
3. Export ke `.docx` (File → Download → Microsoft Word)
4. Replace file `.docx` di folder `templates/` dengan hasil export

Untuk menambah template baru:
1. Buat Google Doc baru dengan format yang diinginkan, salin Doc ID dari URL
2. Export ke `.docx` dan simpan di folder ini
3. Tambahkan entri di tabel mapping di atas (nama file `.docx` + Google Doc ID)

---

## Placeholder Standar

Placeholder ini harus ada di setiap template agar skill `isi-laporan` bisa mengisi otomatis:

| Placeholder | Diisi oleh | Keterangan |
|---|---|---|
| `[NOMOR_ST]` | Script otomatis | Nomor Surat Tugas |
| `[TANGGAL_ST]` | Script otomatis | Tanggal Surat Tugas |
| `[NAMA_OBYEK]` | Claude (Task 04) | Nama paket/unit yang diawasi |
| `[UNIT_DIAWASI]` | Claude (Task 04) | Unit organisasi yang diawasi |
| `[NAMA_KETUA_TIM]` | Claude (Task 04) | Ketua Tim |
| `[NAMA_TIM_LENGKAP]` | Claude (Task 04) | Seluruh anggota tim |
| `[URAIAN_CATATAN]` | Claude (Task 04) | Blok uraian per temuan/catatan |
| `[SIMPULAN]` | Claude (Task 04) | Paragraf simpulan keyakinan |
| `[TABEL_REKOMENDASI]` | Claude (Task 04) | Tabel rekomendasi final |
| `[NOMOR_LHP]` | Auditor (manual, pasca-Task 04) | Diisi dari SIMWAS |
| `[TANGGAL_LHP]` | Auditor (manual, pasca-Task 04) | Diisi di Word |
| `[PENERIMA_LHP]` | Auditor (manual, pasca-Task 04) | Jabatan penerima laporan |
| `[NAMA_INSPEKTUR]` | Auditor (manual, pasca-Task 04) | Diisi di Word |
| `[NIP_INSPEKTUR]` | Auditor (manual, pasca-Task 04) | Diisi di Word |
