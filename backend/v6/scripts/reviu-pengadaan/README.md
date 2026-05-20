# Pipeline Reviu Pengadaan — v0.1

Pipeline untuk skill `reviu-pengadaan` (Keyakinan Terbatas, cakupan sampai penandatanganan kontrak).

## Reuse Komponen dari audit-pengadaan

Reviu-pengadaan menggunakan **digest yang sama** dengan audit-pengadaan (`scripts/audit-pengadaan/digest_pengadaan.py`). Perbedaan hanya di cross-check rules dan renderer.

```
folder penugasan ─► scripts/audit-pengadaan/digest_pengadaan.py ─► pengadaan-digest.json
                                                                         │
                                                                         ▼
                                        scripts/reviu-pengadaan/cross_check.py (7 rules)
                                                                         │
                                                                         ▼
                                                                 anomalies.json
                                                                         │
                                                                         ▼
                                        scripts/reviu-pengadaan/render_lhr.py (TBD)
                                                                         │
                                                                         ▼
                                                           LHR-REVIU-PENGADAAN.docx
```

## Cara Pakai

```bash
cd audit-system-v4
PENUGASAN=penugasan/2026-XXX-reviu-pengadaan-XXX

# 1. Digest (reuse audit-pengadaan)
python3 scripts/audit-pengadaan/digest_pengadaan.py \
  "$PENUGASAN" \
  -o "$PENUGASAN/_KKP/pengadaan-digest.json"

# 2. Cross-check reviu-pengadaan (rules limited assurance)
python3 scripts/reviu-pengadaan/cross_check.py \
  "$PENUGASAN/_KKP/pengadaan-digest.json" \
  -o "$PENUGASAN/_KKP/anomalies.json"

# 3. Render LHR — pakai render_lhr.py dari reviu-rka-kl dengan adaptasi template kolom
#    (render_lhr.py native untuk reviu-pengadaan dibangun di v0.2)
```

## 7 Rules (v0.1)

| ID | Aspek | Severity | Rule |
|---|---|---|---|
| RP.1 | Perencanaan | PERINGATAN | HPS tanpa dokumen pembentuk harga |
| RP.2 | Perencanaan | PERINGATAN | Periode KAK ≠ HPS |
| RP.3 | Perencanaan | PERINGATAN | SLA KAK ≠ HPS |
| RP.4 | Perencanaan | PERINGATAN | KAK menyebut migrasi, HPS tidak |
| RP.5 | Perencanaan | PERINGATAN | KAK belum cantumkan parameter teknis kunci (SLA/kapasitas/periode) |
| RP.6 | Pemilihan | PERINGATAN | SPPBJ tapi tidak ada Permohonan Jaminan Pelaksanaan |
| RP.7 | Dokumentasi | PERINGATAN | KAK atau HPS tidak tersedia |

## Perbedaan dengan audit-pengadaan

| Aspek | audit-pengadaan | reviu-pengadaan |
|---|---|---|
| Paradigma | Keyakinan Memadai | Keyakinan Terbatas |
| Cakupan | s.d. Pembayaran | s.d. Penandatanganan Kontrak |
| Kolom KKP | No, Judul, Kondisi, Kriteria, **Sebab**, Akibat | No, Judul, Kondisi, Kriteria, Akibat |
| Jumlah rules | 11 | 7 |
| Bahasa catatan | "temuan" + rekomendasi kongkret | "catatan" + saran preventif |

## Roadmap v0.2

- Bangun `render_lhr.py` native untuk reviu-pengadaan (kolom tanpa Sebab, tone preventif)
- Tambah rules: kewajaran HPS vs benchmark, lokasi pengadaan, spektek terukur
- Handling pengadaan konsultansi (berbeda dengan barang/jasa lainnya)
