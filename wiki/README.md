# Wiki — Audit AI v7

Knowledge base yang dapat diakses agen Anggota Tim (AT) dan Ketua Tim (KT) saat menjalankan reviu. Folder ini ditujukan untuk **diisi & dikelola oleh auditor manusia** sebagai pengetahuan kumulatif tim Inspektorat II.

Saat agen menjalankan analisis, dia akan:
1. Memanggil `list_temuan_patterns(skill)` untuk mendapat daftar pattern yang tersedia
2. Memanggil `get_temuan_pattern(pattern_id)` untuk membaca pattern spesifik yang relevan
3. Pakai pattern sebagai **referensi format & checklist** — bukan template copy-paste

Pattern = "rumus" temuan yang sudah pernah teruji. Misalnya pattern `RP-08` mengatur bagaimana menulis temuan "HPS hanya 1 sumber harga valid" — frasa, kriteria peraturan, sumber bukti yang harus dicari. Auditor menambahkan pattern baru kalau temuan jenis itu sering muncul.

## Struktur folder

```
wiki/
├── README.md                          # file ini
├── temuan-patterns/
│   ├── reviu-pengadaan/
│   │   ├── README.md                  # index pattern reviu-pengadaan
│   │   ├── RP-08-hps-rfi-minimum.md   # contoh pattern
│   │   └── ...                        # auditor menambahkan pattern di sini
│   └── reviu-rka-kl/
│       ├── README.md                  # index pattern reviu-rka-kl
│       ├── RKA-01-tor-7-blok.md       # contoh pattern
│       └── ...                        # auditor menambahkan pattern di sini
└── (rencana ke depan) peraturan/, glossary/
```

## Format file pattern

Setiap pattern adalah file `.md` dengan YAML frontmatter di atas, lalu konten markdown. Skema minimal:

```markdown
---
id: RP-08
skill: reviu-pengadaan
kategori: PBJ-HPS
severity: CRITICAL
judul: "HPS Tidak Didukung Minimum 2 Sumber Harga Independen"
kriteria_baku: "Perpres 16/2018 jo. Perpres 12/2021 Pasal 26 ayat (5)"
tags: [hps, rfi, perpres-16]
---

# RP-08: HPS Tidak Didukung Minimum 2 Sumber Harga Independen

## Pattern Kondisi
Deskripsi pola kondisi yang menjadi indikator temuan...

## Kriteria
Peraturan yang dilanggar, lengkap dengan pasal & ayat...

## Akibat
Risiko yang muncul bila kondisi tidak diperbaiki...

## Bukti Yang Harus Dicari
- Dokumen HPS: section "Sumber Penjajakan Harga"
- Dokumen RFI per vendor: pastikan berisi penawaran harga, bukan surat penolakan
- ...

## Contoh Kasus Sebelumnya
(opsional) Anonimkan kasus historis untuk konteks
```

**Field wajib** di frontmatter:
- `id` — unique identifier (mis. `RP-08`, `RKA-15`)
- `skill` — `reviu-pengadaan` | `reviu-rka-kl`
- `kategori` — bebas (PBJ-HPS, RKA-TOR, dll)
- `severity` — `CRITICAL` | `HIGH` | `MEDIUM` | `LOW` | `INFO`
- `judul` — string

**Field opsional:**
- `kriteria_baku` — peraturan inti yang dilanggar
- `tags` — array string untuk pencarian

## Penamaan file

Pola: `{ID}-{slug-judul-pendek}.md`

Contoh:
- `RP-08-hps-rfi-minimum.md` ✓
- `RKA-15-sbm-tahun-anggaran.md` ✓
- `pattern-hps.md` ✗ (tidak ada ID prefix, sulit dilacak)

## Cara menambahkan pattern baru

1. Tentukan ID yang belum dipakai (cek README.md per skill)
2. Buat file `.md` di subfolder skill yang sesuai
3. Isi frontmatter + konten
4. Update README.md per skill (tambah baris di tabel index)
5. Commit ke git supaya tim lain bisa pakai

## Diakses oleh

- Agen Anggota Tim (`anggota_tim`) saat susun KKP
- Agen Ketua Tim (`ketua_tim`) saat susun LHR + rekomendasi

Path resolusi via env var `APP_WIKI_PATH` di `.env`.

## Lihat juga

- `backend/app/tools/wiki_tools.py` — implementasi bridge agen → wiki
- `../README.md` § "Wiki / Pattern Library"
