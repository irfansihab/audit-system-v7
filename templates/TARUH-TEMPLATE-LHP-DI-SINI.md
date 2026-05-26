# Folder: templates/

> **16 template sudah tersedia** — lihat **[TEMPLATE-INDEX.md](TEMPLATE-INDEX.md)** untuk mapping lengkap jenis pengawasan → template.
> Script pemilihan template otomatis ada di `scripts/prepare_lhp.py`.

Folder ini menyimpan **template laporan** per jenis pengawasan. Claude akan membaca template ini dan mengisi placeholder yang ada — **tidak menulis laporan dari nol**.

---

## Struktur Folder yang Direkomendasikan

```
templates/
├── reviu-pengadaan/
│   └── template-lhp.docx
├── audit-pengadaan/
│   └── template-lhp.docx
├── pemantauan-pengadaan/
│   └── template-lhp.docx
├── reviu-kinerja/
│   └── template-lhp.docx
├── reviu-spip/
│   └── template-lhp.docx
├── evaluasi-reformasi-birokrasi/
│   └── template-lhp.docx
├── evaluasi-manajemen-risiko/
│   └── template-lhp.docx
└── template-lhp.docx        ← template generik (fallback jika tidak ada yang spesifik)
```

---

## Cara Membuat Template

Template adalah file Word (.docx) yang berisi teks statis (kop surat, bagian-bagian laporan, format tanda tangan) dan **placeholder** untuk bagian yang diisi Claude.

### Placeholder yang harus ada di template:

| Placeholder | Keterangan |
|------------|------------|
| `[NOMOR_LHP]` | Diisi auditor secara manual setelah draft jadi |
| `[TANGGAL_LHP]` | Diisi auditor secara manual |
| `[NOMOR_ST]` | Nomor Surat Tugas |
| `[TANGGAL_ST]` | Tanggal Surat Tugas |
| `[NOMOR_ND_PERMINTAAN]` | Nomor ND permintaan (kosong jika dari PKPT) |
| `[NAMA_OBYEK]` | Nama paket/unit yang diawasi |
| `[UNIT_DIAWASI]` | Unit organisasi yang diawasi |
| `[PENERIMA_LHP]` | Jabatan penerima laporan |
| `[NAMA_KETUA_TIM]` | Ketua Tim |
| `[NAMA_TIM_LENGKAP]` | Seluruh anggota tim |
| `[PENANGGUNG_JAWAB]` | Penanggung Jawab / Inspektur |
| `[PERIODE]` | Periode pengawasan |
| `[LINK_SIMWAS]` | URL survei kepuasan (jika ada) |
| `[URAIAN_CATATAN]` | Blok uraian per catatan — Claude mengisi di sini |
| `[TABEL_RINGKASAN]` | Tabel ringkasan catatan/temuan |
| `[SIMPULAN]` | Paragraf simpulan dengan bahasa keyakinan |
| `[TABEL_REKOMENDASI]` | Tabel rekomendasi final |
| `[NAMA_INSPEKTUR]` | Diisi manual |
| `[NIP_INSPEKTUR]` | Diisi manual |

### Tips membuat template:
- Gunakan format instansi yang sudah ada (ambil dari LHP yang pernah ditandatangani)
- Hapus isi yang spesifik (nama, tanggal, temuan) dan ganti dengan placeholder di atas
- Pertahankan kop surat, format halaman, footer, dan format tanda tangan
- Simpan sebagai .docx (bukan .pdf)

---

## Jika Template Belum Tersedia

Claude akan menggunakan **format standar built-in** (lihat Task 04). Tambahkan template kapan saja — mulai dari yang paling sering digunakan (misal: reviu-pengadaan).

---

## Prioritas Penambahan Template (saran urutan):
1. `reviu-pengadaan/template-lhp.docx` ← paling sering digunakan
2. `pemantauan-pengadaan/template-lhp.docx`
3. `audit-pengadaan/template-lhp.docx`
4. `evaluasi-reformasi-birokrasi/template-lhp.docx`
5. Template lainnya sesuai kebutuhan
