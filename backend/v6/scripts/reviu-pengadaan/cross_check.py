"""
cross_check.py — Rule-based cross-check untuk reviu-pengadaan.

Reuse digest dari audit-pengadaan/digest_pengadaan.py (input JSON sama).
Scope reviu-pengadaan: Keyakinan TERBATAS, hanya sampai tahap Pemilihan/
Penandatanganan Kontrak. Tidak mencakup Pembayaran (itu audit-pengadaan).

Kolom KKP: No, Judul, Kondisi, Kriteria, Akibat (TANPA Sebab — limited assurance
tidak analisis akar masalah).

Usage:
    python cross_check.py <pengadaan-digest.json> [-o anomalies.json]
"""

from __future__ import annotations
import argparse
import json
import re
import sys
from pathlib import Path

KRITIS = "KRITIS"
PERINGATAN = "PERINGATAN"
INFO = "INFO"


def _rule(rule_id, severity, aspek, judul, deskripsi, bukti=None, draft=None):
    return {
        "rule_id": rule_id,
        "severity": severity,
        "aspek": aspek,
        "judul": judul,
        "deskripsi": deskripsi,
        "bukti": bukti or {},
        "draft_catatan": draft,
    }


def _first(digest: dict, doc_type: str) -> dict | None:
    items = digest.get("dokumen", {}).get(doc_type, [])
    return items[0] if items else None


def _parsed(entry):
    return (entry or {}).get("parsed") or {}


# ============================================================
# RULES — Reviu Pengadaan (Keyakinan Terbatas)
# Fokus: KAK quality, HPS quality, Konsistensi KAK-HPS, Dok Pemilihan
# ============================================================

def rule_rp1_hps_tanpa_pembentuk_harga(digest):
    """RP.1 — HPS tidak didukung dokumen pembentuk harga."""
    hps = _parsed(_first(digest, "hps"))
    if not hps or hps.get("ada_dokumen_pembentuk_harga"):
        return None
    if digest.get("dokumen", {}).get("rfi") or digest.get("dokumen", {}).get("hps_detail"):
        return None
    return _rule(
        "RP.1", PERINGATAN, "Perencanaan",
        "HPS belum didukung dokumen pembentuk harga yang lengkap",
        "HPS tidak menyebut penawaran vendor/market research/RFI.",
        bukti={"hps_total": hps.get("total")},
        draft={
            "kondisi": f"HPS bernilai Rp {hps.get('total') or '—'} tidak didukung dokumen "
                       f"pembentuk harga yang dapat ditelusuri.",
            "kriteria": "Perpres 16/2018 jo. Perpres 12/2021 Pasal 26 — HPS disusun berdasarkan "
                        "keahlian dan data yang dapat dipertanggungjawabkan.",
            "akibat": "Kewajaran nilai HPS tidak dapat diverifikasi pada tahap reviu; berpotensi "
                      "penetapan nilai tidak sesuai pasar.",
        }
    )


def rule_rp2_kak_hps_periode_beda(digest):
    """RP.2 — Periode KAK ≠ HPS."""
    kak = _parsed(_first(digest, "kak"))
    hps = _parsed(_first(digest, "hps"))
    if not (kak and hps):
        return None
    pk, ph = kak.get("periode"), hps.get("periode")
    if not (pk and ph) or pk.strip() == ph.strip():
        return None
    return _rule(
        "RP.2", PERINGATAN, "Perencanaan",
        f"Periode KAK ({pk}) berbeda dengan HPS ({ph})",
        "Inkonsistensi periode pengadaan antara KAK dan HPS.",
        bukti={"kak_periode": pk, "hps_periode": ph},
        draft={
            "kondisi": f"KAK menyebutkan periode {pk}, HPS menghitung untuk periode {ph}.",
            "kriteria": "Perpres 16/2018 Pasal 26 — HPS dibuat sesuai KAK.",
            "akibat": "Nilai HPS tidak proporsional dengan ruang lingkup KAK; berisiko "
                      "over/under-budgeting.",
        }
    )


def rule_rp3_kak_hps_sla_beda(digest):
    """RP.3 — SLA KAK vs HPS: 3 kasus.

    (a) KAK punya SLA, HPS tidak alokasi → KRITIS (HPS tidak cover biaya jaminan SLA)
    (b) Nilai SLA berbeda → PERINGATAN (klasik mismatch)
    (c) Keduanya tidak punya SLA → SKIP
    """
    kak = _parsed(_first(digest, "kak"))
    hps = _parsed(_first(digest, "hps"))
    if not (kak and hps):
        return None
    sk, sh = kak.get("sla_value"), hps.get("sla_value")
    kak_sla_disebut = kak.get("sla_disebut", False)
    hps_sla_disebut = hps.get("sla_disebut", False)

    # Kasus (a): KAK menetapkan SLA tapi HPS tidak alokasi sama sekali
    if kak_sla_disebut and not hps_sla_disebut:
        return _rule(
            "RP.3", KRITIS, "Perencanaan",
            f"KAK menetapkan SLA ({sk or 'disebut tanpa angka'}) namun HPS tidak mengalokasikan komponen biaya jaminan SLA",
            "HPS tidak memuat komponen biaya untuk pemenuhan/jaminan/monitoring SLA.",
            bukti={"kak_sla": sk, "hps_sla": None,
                   "kak_disebut": kak_sla_disebut, "hps_disebut": hps_sla_disebut},
            draft={
                "kondisi": (f"KAK menetapkan SLA{' sebesar ' + sk if sk else ''} sebagai persyaratan layanan, "
                            f"namun HPS tidak memuat line item komponen biaya untuk: jaminan/penalti SLA, "
                            f"monitoring uptime, atau laporan SLA bulanan."),
                "kriteria": ("Perpres 16/2018 Pasal 26 — HPS harus mencakup seluruh komponen biaya sesuai "
                             "ruang lingkup KAK. SLA tinggi (mis. 99,9%+) berimplikasi cost untuk redundansi, "
                             "monitoring 24/7, dan SLA reporting yang harus terhitung di HPS."),
                "akibat": ("Penyedia berpotensi menolak komitmen SLA atau meminta addendum biaya setelah kontrak. "
                           "Penalti SLA tidak dapat ditegakkan karena tidak ada baseline biaya jaminan SLA."),
            }
        )

    # Kasus (b): Keduanya punya SLA tapi nilai berbeda
    if sk and sh and sk != sh:
        return _rule(
            "RP.3", PERINGATAN, "Perencanaan",
            f"SLA berbeda antara KAK ({sk}) dan HPS ({sh})",
            "Nilai SLA tidak konsisten antar dokumen perencanaan.",
            bukti={"kak": sk, "hps": sh},
            draft={
                "kondisi": f"KAK menetapkan SLA {sk}, HPS menghitung dengan asumsi {sh}.",
                "kriteria": "Perpres 16/2018 Pasal 19 — persyaratan teknis harus konsisten lintas dokumen.",
                "akibat": "Kewajiban kontraktual penyedia ambigu; risiko penalti SLA tidak dapat ditegakkan.",
            }
        )
    return None


def rule_rp11_sla_internal_inkonsisten_kak(digest):
    """RP.11 — KAK menyebut multiple nilai SLA berbeda (inkonsistensi internal).

    Menggunakan field `sla_all_values` dari parser (scan SELURUH halaman KAK),
    bukan _raw_first_chars yang hanya 2500 char awal.
    """
    kak = _parsed(_first(digest, "kak"))
    if not kak:
        return None
    sla_values = kak.get("sla_all_values") or []
    # Normalisasi: buang trailing '%' dan dedupe lagi (defensive)
    norm = []
    for v in sla_values:
        v = str(v).rstrip("%").strip()
        if v and v not in norm:
            norm.append(v)
    if len(norm) < 2:
        return None
    return _rule(
        "RP.11", KRITIS, "Perencanaan",
        f"KAK menyebutkan {len(norm)} nilai SLA berbeda: {', '.join(norm[:5])}%",
        "Nilai SLA inkonsisten DI DALAM dokumen KAK sendiri (terdeteksi pada halaman berbeda).",
        bukti={"sla_values_found": norm[:10], "count": len(norm),
               "scope": "seluruh halaman KAK (full text scan)"},
        draft={
            "kondisi": (f"KAK mencantumkan beberapa nilai SLA yang berbeda ({', '.join(norm[:5])}%) "
                        f"di bagian-bagian dokumen yang berbeda, tanpa klarifikasi mana yang akhirnya mengikat."),
            "kriteria": ("Setiap dokumen perencanaan pengadaan wajib mencantumkan parameter teknis (termasuk SLA) "
                         "secara konsisten dan tegas (Perpres 16/2018 Pasal 19). Inkonsistensi internal "
                         "menyulitkan penyedia menyusun penawaran dan menjadi sumber sengketa interpretasi kontrak."),
            "akibat": ("Penyedia kesulitan menentukan komitmen SLA yang harus dipenuhi; risiko sengketa "
                       "interpretasi kontrak; kewajiban kontraktual ambigu — formula penalti pembayaran "
                       "berdasar pencapaian SLA mana yang berlaku?"),
        }
    )


def rule_rp4_kak_migrasi_tidak_di_hps(digest):
    """RP.4 — KAK sebut migrasi, HPS tidak alokasikan."""
    kak = _parsed(_first(digest, "kak"))
    hps = _parsed(_first(digest, "hps"))
    if not (kak and hps):
        return None
    if not kak.get("migrasi_disebut") or hps.get("migrasi_disebut"):
        return None
    return _rule(
        "RP.4", PERINGATAN, "Perencanaan",
        "KAK menyebut migrasi namun HPS tidak mengalokasikan komponen migrasi",
        "Komponen migrasi tidak tercermin di HPS.",
        bukti={},
        draft={
            "kondisi": "KAK mencantumkan kebutuhan migrasi, namun HPS tidak memuat komponen biaya migrasi.",
            "kriteria": "Perpres 16/2018 Pasal 26 — HPS harus mencakup seluruh komponen biaya sesuai KAK.",
            "akibat": "Biaya migrasi berpotensi menjadi addendum (memperbesar pagu) atau penyedia "
                      "menolak melakukan migrasi.",
        }
    )


def rule_rp5_kak_inkonsistensi_internal(digest):
    """RP.5 — Kapasitas disebut di KAK tapi tidak detail atau berbeda-beda."""
    kak = _parsed(_first(digest, "kak"))
    if not kak:
        return None
    # Simpel: jika KAK sla/migrasi/kapasitas ada, tapi tidak lengkap semua
    fields = {
        "SLA": kak.get("sla_value"),
        "Kapasitas": kak.get("kapasitas_disebut"),
        "Periode": kak.get("periode"),
    }
    missing = [k for k, v in fields.items() if not v]
    if len(missing) < 2:
        return None
    return _rule(
        "RP.5", PERINGATAN, "Perencanaan",
        f"KAK belum mencantumkan {len(missing)} parameter teknis kunci: {', '.join(missing)}",
        "KAK perlu memuat SLA, kapasitas, dan periode secara tegas.",
        bukti={"missing_fields": missing, "present_fields": {k: v for k, v in fields.items() if v}},
        draft={
            "kondisi": f"KAK belum mencantumkan parameter teknis berikut secara tegas: "
                       f"{', '.join(missing)}.",
            "kriteria": "Kriteria IR2 — KAK/TOR harus mencantumkan spesifikasi teknis terukur "
                        "(SLA, kapasitas, periode, kualitas) agar penyedia dapat menawarkan "
                        "harga dan kinerja yang tepat.",
            "akibat": "Penyedia kesulitan memahami ekspektasi teknis; risiko penawaran tidak "
                      "sesuai kebutuhan K/L dan sengketa saat pelaksanaan.",
        }
    )


def rule_rp6_sppbj_tanpa_jaminan(digest):
    """RP.6 — SPPBJ tapi tidak ada dokumen permohonan jaminan pelaksanaan."""
    sppbj = _first(digest, "sppbj")
    jaminan = _first(digest, "permohonan_jaminan")
    if not sppbj:
        return None
    if jaminan:
        return None
    return _rule(
        "RP.6", PERINGATAN, "Pemilihan",
        "SPPBJ diterbitkan namun tidak ditemukan dokumen Permohonan Jaminan Pelaksanaan",
        "Penyedia seharusnya mengajukan jaminan pelaksanaan sebelum kontrak.",
        bukti={"sppbj": sppbj.get("filename")},
        draft={
            "kondisi": "SPPBJ sudah diterbitkan, namun dokumen Permohonan Jaminan Pelaksanaan "
                       "belum ditemukan di folder penugasan.",
            "kriteria": "Perpres 16/2018 Pasal 33 — penyedia wajib menyerahkan Jaminan Pelaksanaan "
                        "sebelum penandatanganan kontrak untuk pengadaan > Rp 200 juta.",
            "akibat": "Kontrak berpotensi ditandatangani tanpa jaminan finansial yang sesuai; "
                      "risiko kesulitan recovery apabila penyedia wanprestasi.",
        }
    )


def rule_rp7_dokumen_kunci_missing(digest):
    """RP.7 — KAK atau HPS tidak tersedia."""
    missing = [t for t in ["kak", "hps"] if t in digest.get("missing_types", [])]
    if not missing:
        return None
    return _rule(
        "RP.7", PERINGATAN, "Dokumentasi",
        f"Dokumen kunci perencanaan tidak ditemukan: {', '.join(missing)}",
        "Reviu perencanaan tidak dapat dilakukan penuh.",
        bukti={"missing": missing},
        draft={
            "kondisi": f"Dokumen {', '.join(missing).upper()} tidak ditemukan di folder penugasan.",
            "kriteria": "Perpres 16/2018 Pasal 25 — dokumen perencanaan pengadaan wajib tersedia.",
            "akibat": "Reviu perencanaan tidak dapat menguji konsistensi antar dokumen; keyakinan "
                      "terbatas tidak dapat diberikan pada aspek perencanaan.",
        }
    )


def rule_rp8_hps_multi_source(digest):
    """RP.8 — HPS hanya berbasis 1 RFI valid (tidak memenuhi multi-source).

    Perpres 16/2018 Pasal 26 ayat 5: HPS dibuat dari minimal 2 sumber
    harga independen. Kalau RFI yang dikumpulkan auditee mayoritas refusal
    participation, HPS tidak punya benchmark valid.
    """
    rfi_list = (digest.get("dokumen", {}) or {}).get("rfi", []) or []
    if not rfi_list:
        return None
    valid_count = 0
    refusal_count = 0
    refusal_vendors = []
    for rfi in rfi_list:
        p = rfi.get("parsed") or {}
        if p.get("memberikan_harga"):
            valid_count += 1
        if p.get("menolak_partisipasi"):
            refusal_count += 1
            v = p.get("vendor_terdeteksi") or rfi.get("filename", "?")
            refusal_vendors.append(v)
    if valid_count >= 2:
        return None  # multi-source terpenuhi
    return _rule(
        "RP.8", KRITIS, "Perencanaan",
        f"HPS tidak memenuhi multi-source: hanya {valid_count} RFI valid (sisanya refusal/tidak ada harga).",
        "HPS berbasis kurang dari 2 sumber harga independen — tidak memenuhi Perpres 16/2018 Pasal 26.",
        bukti={"total_rfi": len(rfi_list), "rfi_dengan_harga": valid_count,
               "rfi_menolak": refusal_count, "vendor_menolak": refusal_vendors},
        draft={
            "kondisi": (f"Dari {len(rfi_list)} RFI yang dikumpulkan, hanya {valid_count} RFI yang memberikan "
                        f"harga, sisanya menolak partisipasi atau tidak memuat harga. "
                        f"Vendor menolak: {', '.join(refusal_vendors) if refusal_vendors else '—'}."),
            "kriteria": "Perpres 16/2018 Pasal 26 ayat 5 — HPS dibuat dari paling sedikit 2 (dua) sumber harga independen.",
            "akibat": "HPS berisiko over/under-priced karena tidak ada benchmark pembanding; "
                      "validitas HPS sebagai dasar pemilihan penyedia dapat dipertanyakan.",
        }
    )


def rule_rp9_sbm_year_mismatch(digest):
    """RP.9 — Dasar hukum HPS rujuk SBM/Pedoman tahun != TA pelaksanaan."""
    hps_list = (digest.get("dokumen", {}) or {}).get("hps", []) or []
    if not hps_list:
        return None
    hps0 = hps_list[0].get("parsed") or {}
    raw = hps0.get("_raw_first_chars", "") or ""
    if not raw:
        return None
    ta_match = re.search(r"DIPA[-\s]\s*[\d.]+/(\d{4})", raw, re.I)
    if not ta_match:
        ta_match = re.search(r"Tahun\s+Anggaran\s+(\d{4})", raw, re.I)
    if not ta_match:
        return None
    ta_pelaksanaan = int(ta_match.group(1))
    sbm_match = re.search(r"Standar\s+Biaya\s+Masukan\s+\(?SBM\)?\s+Tahun\s+(\d{4})", raw, re.I)
    pedoman_match = re.search(r"Pedoman\s+Pelaksanaan\s+Anggaran\s+(?:Tahun\s+Anggaran\s+)?(\d{4})", raw, re.I)
    mismatches = []
    if sbm_match and int(sbm_match.group(1)) != ta_pelaksanaan:
        mismatches.append(f"SBM rujuk Tahun {sbm_match.group(1)} (TA pelaksanaan {ta_pelaksanaan})")
    if pedoman_match and int(pedoman_match.group(1)) != ta_pelaksanaan:
        mismatches.append(f"Pedoman Pelaksanaan Anggaran rujuk Tahun {pedoman_match.group(1)} (TA pelaksanaan {ta_pelaksanaan})")
    if not mismatches:
        return None
    return _rule(
        "RP.9", PERINGATAN, "Perencanaan",
        f"Tahun rujukan dasar hukum HPS tidak sesuai TA pelaksanaan ({ta_pelaksanaan}).",
        "Dasar hukum HPS perlu disesuaikan dengan TA pelaksanaan untuk memastikan harga valid.",
        bukti={"ta_pelaksanaan": ta_pelaksanaan, "mismatches": mismatches},
        draft={
            "kondisi": (f"HPS untuk pengadaan TA {ta_pelaksanaan} mencantumkan dasar hukum: " + "; ".join(mismatches) + "."),
            "kriteria": ("HPS harus disusun berdasarkan dasar hukum yang berlaku pada TA pelaksanaan, "
                         "termasuk SBM (PMK Standar Biaya Masukan) dan Pedoman Pelaksanaan Anggaran TA tersebut."),
            "akibat": ("Harga di HPS berpotensi tidak valid bila tarif SBM/aturan biaya yang dirujuk "
                       "sudah deprecated atau berbeda dari TA pelaksanaan. Perlu klarifikasi auditee."),
        }
    )


def rule_rp10_hps_tanpa_breakdown(digest):
    """RP.10 - HPS hanya 1 line item total tanpa breakdown komponen detail."""
    hps_list = (digest.get("dokumen", {}) or {}).get("hps", []) or []
    if not hps_list:
        return None
    komponen_total = 0
    for hps in hps_list:
        p = hps.get("parsed") or {}
        komponen_total += p.get("komponen_count", 0) or 0
    has_detail_file = False
    all_dokumen = digest.get("dokumen", {}) or {}
    if all_dokumen.get("hps_detail"):
        has_detail_file = True
    for hps in hps_list:
        fn = (hps.get("filename") or "").lower()
        if "tabel" in fn or "rincian" in fn or "detail" in fn or "komponen" in fn:
            has_detail_file = True
            break
    if komponen_total >= 2 or has_detail_file:
        return None
    return _rule(
        "RP.10", PERINGATAN, "Perencanaan",
        "HPS hanya 1 line item total - tidak ada breakdown komponen detail.",
        "Sulit untuk verifikasi kewajaran tiap komponen biaya tanpa breakdown.",
        bukti={"komponen_count": komponen_total, "has_detail_file": has_detail_file},
        draft={
            "kondisi": ("HPS yang ditemukan hanya berisi 1 line item total tanpa breakdown komponen biaya."),
            "kriteria": ("Perpres 16/2018 Pasal 26 mensyaratkan HPS disusun berdasarkan rincian komponen biaya."),
            "akibat": ("Validasi kewajaran HPS terhadap SBM/SBK tidak dapat dilakukan."),
        }
    )


ALL_RULES = [
    rule_rp1_hps_tanpa_pembentuk_harga,
    rule_rp2_kak_hps_periode_beda,
    rule_rp3_kak_hps_sla_beda,
    rule_rp4_kak_migrasi_tidak_di_hps,
    rule_rp5_kak_inkonsistensi_internal,
    rule_rp6_sppbj_tanpa_jaminan,
    rule_rp7_dokumen_kunci_missing,
    rule_rp8_hps_multi_source,
    rule_rp9_sbm_year_mismatch,
    rule_rp10_hps_tanpa_breakdown,
    rule_rp11_sla_internal_inkonsisten_kak,
]


def run_checks(digest):
    out = []
    for fn in ALL_RULES:
        try:
            r = fn(digest)
            if r:
                out.append(r)
        except Exception as e:
            out.append({"rule_id": fn.__name__, "severity": "ERROR", "error": str(e)})
    return out


def _self_check_ast() -> None:
    import ast
    try:
        ast.parse(open(__file__, "r", encoding="utf-8").read())
    except SyntaxError as e:
        print(f"Self-check AST gagal: {e}", file=sys.stderr)
        sys.exit(2)


def main(argv=None):
    _self_check_ast()
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("digest_json")
    ap.add_argument("-o", "--output", default="anomalies.json")
    args = ap.parse_args(argv)
    digest = json.loads(Path(args.digest_json).read_text(encoding="utf-8"))
    anomalies = run_checks(digest)
    out = {
        "metadata": {"total_rules_tested": len(ALL_RULES), "total_anomalies_found": len(anomalies)},
        "summary_by_aspek": {},
        "summary_by_severity": {},
        "anomalies": anomalies,
    }
    for a in anomalies:
        out["summary_by_aspek"][a.get("aspek", "?")] = out["summary_by_aspek"].get(a.get("aspek", "?"), 0) + 1
        out["summary_by_severity"][a.get("severity", "?")] = out["summary_by_severity"].get(a.get("severity", "?"), 0) + 1
    Path(args.output).write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"OK: {args.output}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
