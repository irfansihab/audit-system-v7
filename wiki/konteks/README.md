# Konteks — Knowledge Base Pendukung Agen

Folder ini berisi **informasi pendukung** untuk agen di luar pattern temuan. Beda dengan `temuan-patterns/`, file di sini bukan template temuan tapi **cheat sheet** yang dibaca agen sebelum menulis KKP.

## File yang tersedia

| File | Isi | Kapan dibaca agen |
|------|-----|-------------------|
| [`pola-temuan-berulang.md`](pola-temuan-berulang.md) | 9 pola akar masalah lintas LHP/LHR 2025–2026 | **Wajib dibaca di awal** setiap penugasan untuk re-orientasi |
| [`glossary-komdigi.md`](glossary-komdigi.md) | Definisi akronim + profil vendor mitra | Setiap kali menemukan istilah teknis/akronim di dokumen |
| [`regulasi-kunci.md`](regulasi-kunci.md) | Pasal-ayat baku regulasi yang sering dirujuk + kutipan | Sebelum menulis bagian "kriteria" di temuan |

## Tujuan halaman ini

1. **Mengurangi halusinasi** — agen tidak ngarang definisi istilah, sitasi pasal, atau pola temuan.
2. **Meningkatkan konsistensi** — semua KKP merujuk vocabulary yang sama.
3. **Mempercepat onboarding agen baru** — knowledge base terdokumentasi.

## Cara akses dari agen

Agen memanggil MCP tools yang ada di `backend/app/tools/wiki_tools.py`:

```python
# List konteks yang tersedia
list_konteks()
# Return: [{"id": "KONTEKS-POLA-BERULANG", "judul": "...", "file": "konteks/pola-temuan-berulang.md"}, ...]

# Baca isi spesifik
get_konteks(kategori="pola-berulang")  # atau "glossary" atau "regulasi"
# Return: { "id": "...", "body_markdown": "...", "tanggal_update": "..." }
```

## Format file di folder ini

Sama seperti pattern, setiap file diawali YAML frontmatter:

```markdown
---
id: KONTEKS-XXX
kategori: konteks
judul: "Judul Halaman"
sumber: "Sumber data"
tanggal_update: "YYYY-MM-DD"
tags: [tag1, tag2]
---

# Judul

Body markdown...
```

**Field wajib**:
- `id` — unique identifier diawali `KONTEKS-` (mis. `KONTEKS-POLA-BERULANG`).
- `kategori` — selalu `konteks`.
- `judul` — string deskriptif.
- `tanggal_update` — kapan terakhir diperbarui.

## Cara menambahkan konteks baru

1. Identifikasi kebutuhan (mis. profil vendor baru, regulasi baru, framework baru).
2. Buat file `.md` di folder ini dengan ID `KONTEKS-{slug}`.
3. Isi frontmatter + body.
4. Update tabel di README ini.
5. (Opsional) Update `wiki_tools.py` bila perlu kategori baru di mapping ID.

## Lihat juga

- [`../README.md`](../README.md) — README utama wiki
- [`../temuan-patterns/`](../temuan-patterns/) — pattern temuan
- `backend/app/tools/wiki_tools.py` — bridge agen ke wiki
