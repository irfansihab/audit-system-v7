"""
cross_check.py — Deterministic cross-check engine antara TOR-JSON dan RAB-JSON.

Usage:
    python cross_check.py <tor.json> <rab.json> [-o anomalies.json]
    python cross_check.py --batch --tor-dir <DIR> --rab-dir <DIR> [-o anomalies-master.json]
"""

from __future__ import annotations
import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


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


# ============================================================
# RULES (existing 21)
# ============================================================

def rule_a3_sbm_belum_terbit(tor: dict, rab: dict, tahun_reviu: int = 2027) -> dict | None:
    """A.3 — SBM tahun anggaran yang direviu belum terbit."""
    return _rule(
        "A.3", INFO, "A",
        f"Keterbatasan referensi SBM TA {tahun_reviu} - verifikasi kewajaran tidak penuh",
        f"PMK SBM TA {tahun_reviu} perlu dikonfirmasi ketersediaannya saat reviu.",
        bukti={"tahun_reviu": tahun_reviu},
        draft={
            "kondisi": f"PMK SBM TA {tahun_reviu} belum tersedia saat reviu.",
            "kriteria": "Pasal 61 ayat (2) huruf a PMK 107/2024.",
            "akibat": f"Potensi perubahan nominal pada tahap Pagu Anggaran.",
            "rekomendasi": f"Bersiap menyesuaikan satuan biaya saat PMK SBM TA {tahun_reviu} terbit.",
        }
    )


def rule_a2_sewa_kendaraan_pejabat(tor: dict, rab: dict) -> dict | None:
    """A.2 — Sewa kendaraan untuk Menteri/Dirjen."""
    items = rab.get("indices", {}).get("menteri_dirjen_items", [])
    sewa_items = [x for x in items if "sewa" in x.get("deskripsi", "").lower()]
    if not sewa_items:
        return None
    total = sum(x.get("total") or 0 for x in sewa_items)
    if total == 0:
        return None
    return _rule(
        "A.2", PERINGATAN, "A",
        f"Sewa kendaraan untuk pejabat eselon I/II - total Rp {total:,}",
        f"Ditemukan {len(sewa_items)} line item sewa kendaraan untuk Menteri/Dirjen/Direktur.",
        bukti={"items": sewa_items[:8], "total": total},
        draft={
            "kondisi": f"RAB mengalokasikan sewa kendaraan untuk Menteri/Dirjen pada {len(sewa_items)} item.",
            "kriteria": "Pasal 14 PMK 62/2023.",
            "akibat": "Alokasi tidak proporsional menurunkan value for money.",
            "rekomendasi": "Delegasi commissioning kepada tim teknis Eselon III/IV.",
        }
    )


def rule_b1_akun_526_untuk_sewa(tor: dict, rab: dict) -> dict | None:
    """B.1 — Akun 526xxx dipakai untuk 'sewa' (struktur)."""
    hits = []
    for k in rab.get("komponen", []):
        for a in k.get("akun", []):
            if a.get("kode_akun", "").startswith("526"):
                sewa_rincian = [r for r in a.get("rincian", []) if "sewa" in r.get("deskripsi", "").lower()]
                if sewa_rincian or "bantuan" in (a.get("nama_akun") or "").lower():
                    hits.append({"komponen": k["kode"], "akun": a["kode_akun"],
                                 "nama_akun": a.get("nama_akun"),
                                 "sewa_rincian_count": len(sewa_rincian),
                                 "total_akun": a.get("total")})
    if not hits:
        return None
    return _rule("B.1", PERINGATAN, "B",
                 "Akun 526xxx digunakan untuk line-item sewa",
                 f"Ditemukan {len(hits)} akun 526 dengan rincian sewa.",
                 bukti={"hits": hits},
                 draft={"kondisi": f"RAB pakai akun {hits[0]['akun']} untuk sewa.",
                        "kriteria": "PMK 102/2018 jo. PMK 187/2019.",
                        "akibat": "Ketidaktepatan klasifikasi.",
                        "rekomendasi": "Migrasikan ke akun 522191/522141."})


def rule_b2_522191_untuk_konstruksi(tor: dict, rab: dict) -> dict | None:
    """B.2 — Akun 522191 dipakai untuk konstruksi."""
    hits = []
    for k in rab.get("komponen", []):
        for a in k.get("akun", []):
            if a.get("kode_akun", "") == "522191":
                konstruksi = [r for r in a.get("rincian", [])
                              if re.search(r"konstruksi|panggung|properti", r.get("deskripsi", ""), re.I)]
                if konstruksi:
                    hits.append({"komponen": k["kode"], "akun": a["kode_akun"],
                                 "konstruksi_count": len(konstruksi)})
    raw_join = "\n".join(rab.get("raw_text_pages", []) or [])
    if not hits and re.search(r"522191.{0,500}?konstruksi\s+panggung", raw_join, re.S | re.I):
        hits.append({"komponen": "unknown", "akun": "522191", "konstruksi_count": "?"})
    if not hits:
        return None
    return _rule("B.2", PERINGATAN, "B",
                 "Akun 522191 digunakan untuk konstruksi",
                 "Konstruksi umumnya masuk Belanja Barang Non-Operasional/Modal.",
                 bukti={"hits": hits},
                 draft={"kondisi": "Akun 522191 untuk konstruksi.",
                        "kriteria": "PMK 102/2018.",
                        "akibat": "Berpotensi koreksi klasifikasi.",
                        "rekomendasi": "Pilah konstruksi ke 521xxx; sewa ke 522141."})


def rule_b3_duplikasi_komponen(tor: dict, rab: dict) -> dict | None:
    """B.3 — Line-item duplikasi antar komponen."""
    items = rab.get("indices", {}).get("sewa_kendaraan_items", [])
    per_komp = {}
    for x in items:
        per_komp.setdefault(x["komponen"], []).append(x)
    if len(per_komp) < 2:
        return None
    komponen_list = sorted(per_komp.keys())
    return _rule("B.3", PERINGATAN, "B",
                 f"Sewa kendaraan muncul di {len(per_komp)} komponen",
                 f"Komponen: {', '.join(komponen_list)}.",
                 bukti={"per_komponen": {k: [x["deskripsi"][:80] for x in v[:3]] for k, v in per_komp.items()}},
                 draft={"kondisi": f"Sewa kendaraan di {len(per_komp)} komponen.",
                        "kriteria": "Pasal 14 PMK 62/2023.",
                        "akibat": "Risiko duplikasi biaya.",
                        "rekomendasi": "Pisahkan jadwal/peserta tiap komponen."})


def rule_c1_penandaan_ganda(tor: dict, rab: dict) -> dict | None:
    """C.1 — Penandaan ganda Cluster 1+2 (struktur)."""
    pen = tor.get("penandaan_cluster", {})
    c1 = pen.get("cluster_1", [])
    c2 = pen.get("cluster_2", [])
    if len(c1) > 0 and len(c2) > 0:
        return _rule("C.1", PERINGATAN, "C",
                     "Penandaan ganda Cluster 1 dan 2",
                     f"Cluster 1: {c1}; Cluster 2: {c2}.",
                     bukti={"cluster_1": c1, "cluster_2": c2},
                     draft={"kondisi": "Cluster 1 dan 2 ditandai bersamaan.",
                            "kriteria": "Pasal 61 ayat (2) huruf c PMK 107/2024.",
                            "akibat": "Over-statement capaian.",
                            "rekomendasi": "Tetapkan satu cluster utama."})
    return None


def rule_d1_dasar_hukum_tanpa_pasal(tor: dict, rab: dict) -> dict | None:
    """D.1 — Dasar hukum tanpa pasal/ayat."""
    dh = tor.get("dasar_hukum", [])
    if not dh:
        return None
    with_pasal = sum(1 for d in dh if d.get("memuat_pasal_ayat"))
    if with_pasal == len(dh):
        return None
    miss = len(dh) - with_pasal
    return _rule("D.1", PERINGATAN, "D",
                 f"Dasar hukum: {miss}/{len(dh)} butir tanpa pasal/ayat",
                 "Kriteria IR2 butir 1.a.",
                 bukti={"total_butir": len(dh), "tanpa_pasal": miss},
                 draft={"kondisi": f"{miss}/{len(dh)} butir tanpa pasal/ayat.",
                        "kriteria": "Kriteria IR2 butir 1.a.",
                        "akibat": "Penelusuran landasan hukum sulit.",
                        "rekomendasi": "Tambahkan pasal/ayat relevan."})


def rule_d2_regulasi_tidak_relevan(tor: dict, rab: dict) -> dict | None:
    """D.2 — Dasar hukum sektor lain."""
    ro_name = (tor.get("identitas_ro", {}) or {}).get("ro", "") or ""
    topic_m = re.search(r"Sektor\s+(\w+)", ro_name, re.I)
    topic = topic_m.group(1).lower() if topic_m else None
    if not topic:
        return None
    suspicious = []
    for d in tor.get("dasar_hukum", []):
        teks = (d.get("teks") or "").lower()
        foreign_sectors = {"energi", "kesehatan", "pendidikan", "pangan"} - {topic}
        for fs in foreign_sectors:
            if fs == "pangan" and topic == "pertanian":
                continue
            if fs in teks and topic not in teks:
                suspicious.append({"butir": d.get("butir"),
                                   "regulasi": f"{d.get('jenis_regulasi')} {d.get('nomor')}/{d.get('tahun')}" if d.get("nomor") else d.get("teks", "")[:80],
                                   "sektor_asing_terdeteksi": fs})
    if not suspicious:
        return None
    return _rule("D.2", PERINGATAN, "D",
                 f"{len(suspicious)} regulasi sektor lain di dasar hukum",
                 f"RO bertema '{topic}'.",
                 bukti={"suspicious": suspicious, "topic_ro": topic},
                 draft={"kondisi": f"{len(suspicious)} regulasi tampak merujuk sektor lain.",
                        "kriteria": "Kriteria IR2 butir 1.a.",
                        "akibat": "Kualitas justifikasi turun.",
                        "rekomendasi": "Ganti regulasi tidak relevan."})


def rule_d3_iro_inkonsistensi(tor: dict, rab: dict) -> dict | None:
    """D.3 — IRO inkonsisten antar dokumen."""
    iro_h = (tor.get("identitas_ro", {}) or {}).get("iro_header") or ""
    iro_d = ((tor.get("kpi", {}) or {}).get("iro_bagian_d") or {}).get("nama") if tor.get("kpi", {}).get("iro_bagian_d") else None
    iro_r = (rab.get("identitas_ro", {}) or {}).get("iro") or ""
    norm_h = iro_h[:80].lower().strip() if iro_h else ""
    norm_d = iro_d[:80].lower().strip() if iro_d else ""
    norm_r = iro_r[:80].lower().strip() if iro_r else ""
    unique = set(filter(None, [norm_h, norm_d, norm_r]))
    if len(unique) <= 1:
        return None
    return _rule("D.3", PERINGATAN, "D",
                 f"Inkonsistensi IRO: {len(unique)} variasi",
                 "IRO TOR header, bagian D, dan RAB berbeda.",
                 bukti={"tor_header": iro_h[:200], "tor_bagian_d": iro_d[:200] if iro_d else None, "rab": iro_r[:200] if iro_r else None},
                 draft={"kondisi": f"{len(unique)} formulasi IRO berbeda.",
                        "kriteria": "Kriteria IR2 butir 2.b.",
                        "akibat": "Sulit pengukuran capaian.",
                        "rekomendasi": "Samakan IRO seluruh bagian."})


def rule_d5_mr_belum_lengkap(tor: dict, rab: dict) -> dict | None:
    """D.5 — Matriks MR belum lengkap."""
    mr = tor.get("manajemen_risiko", {})
    if not mr:
        return None
    missing = []
    if not mr.get("memuat_residual"): missing.append("risiko residual")
    if not mr.get("memuat_strategis_operasional"): missing.append("strategis/operasional")
    if not mr.get("memuat_led_tahun_sebelumnya"): missing.append("LED tahun sebelumnya")
    if not mr.get("memuat_keselarasan_aplikasi_mr"): missing.append("aplikasi MR K/L")
    if not missing:
        return None
    return _rule("D.5", PERINGATAN, "D",
                 f"Matriks MR belum memuat {len(missing)} elemen",
                 f"Belum ada: {', '.join(missing)}.",
                 bukti=mr,
                 draft={"kondisi": f"MR belum memuat: {', '.join(missing)}.",
                        "kriteria": "Kriteria IR2 butir 7.",
                        "akibat": "Mitigasi tidak menjawab risiko riil.",
                        "rekomendasi": f"Lengkapi MR dengan {', '.join(missing)}."})


def rule_e1_lokasi_non_target_disebut(tor: dict, rab: dict) -> dict | None:
    """E.1 — Lokasi non-target disebut (struktur)."""
    target = set(tor.get("lokasi", {}).get("lokasi_target", []) or [])
    mentions = tor.get("lokasi", {}).get("mentions_lokasi_non_target", []) or []
    suspects = [l for l in mentions if l not in target
                and l not in {"Sragen", "Jakarta", "Kota Jakarta"}
                and len(l) > 3]
    suspects_filtered = [l for l in suspects if l in {"Banjarnegara", "Limapuluh", "Kota"}] or suspects[:5]
    if not suspects_filtered:
        return None
    return _rule("E.1", PERINGATAN, "E",
                 f"TOR menyebut {len(suspects_filtered)} lokasi non-target",
                 f"Target: {sorted(target)}; non-target: {suspects_filtered[:5]}.",
                 bukti={"lokasi_target": sorted(target), "non_target": suspects_filtered[:10]},
                 draft={"kondisi": f"Target {len(target)} lokasi; narasi sebut {', '.join(suspects_filtered[:5])}.",
                        "kriteria": "Kriteria IR2 butir 3.b.",
                        "akibat": "Inkonsistensi lokasi.",
                        "rekomendasi": "Periksa narasi lokasi."})


def rule_e2_sektor_asing_di_narasi(tor: dict, rab: dict) -> dict | None:
    """E.2 — Sektor lain di narasi (struktur)."""
    leaks = tor.get("timeline_narasi", {}).get("sector_keyword_leaks", []) or []
    ro_name = (tor.get("identitas_ro", {}) or {}).get("ro", "") or ""
    topic_m = re.search(r"Sektor\s+(\w+)", ro_name, re.I)
    topic = topic_m.group(1).lower() if topic_m else ""
    real_leaks = []
    for leak in leaks:
        kw = leak.get("keyword", "")
        samples = leak.get("samples", [])
        filtered = [s for s in samples if not re.search(r"6\s+[Ss]ektor|Sektor\s+Strategis", s)]
        if filtered and kw != topic:
            real_leaks.append({"keyword": kw, "count_filtered": len(filtered), "samples": filtered[:2]})
    if not real_leaks:
        return None
    return _rule("E.2", PERINGATAN, "E",
                 f"Sektor lain di TOR sektor '{topic}': {[l['keyword'] for l in real_leaks]}",
                 "Kemungkinan copy-paste dari TOR sektor lain.",
                 bukti={"leaks": real_leaks, "topic_ro": topic},
                 draft={"kondisi": f"TOR Sektor {topic.title()} memuat narasi sektor lain.",
                        "kriteria": "Kriteria IR2 butir 3.b.",
                        "akibat": "Menurunkan kredibilitas.",
                        "rekomendasi": "Find-and-replace TOR."})


def rule_e3_baseline_inkonsisten(tor: dict, rab: dict) -> dict | None:
    """E.3 — Inkonsistensi baseline."""
    bl = tor.get("baseline", {})
    mentions = bl.get("narasi_mention_jumlah_kelompok", []) or []
    tabel = bl.get("tabel_baseline_rows", 0) or 0
    big = [n for n in mentions if n >= 10]
    if tabel > 0 and big and tabel != max(big):
        return _rule("E.3", PERINGATAN, "E",
                     f"Baseline inkonsisten: narasi {big}, tabel {tabel}",
                     "Perlu rekonsiliasi.",
                     bukti=bl,
                     draft={"kondisi": f"Narasi {big}; tabel {tabel}.",
                            "kriteria": "Kriteria IR2 butir 1.b.3.",
                            "akibat": "Sulit menilai kewajaran.",
                            "rekomendasi": "Rekonsiliasi narasi-tabel."})
    return None


def rule_e4_cba_cost_inkonsisten(tor: dict, rab: dict) -> dict | None:
    """E.4 — BCR denominator vs total pagu."""
    cba = tor.get("cba", {})
    denom = cba.get("bcr_denominator")
    total_tor = tor.get("biaya", {}).get("total")
    total_rab = rab.get("total_pagu")
    truth = total_rab or total_tor
    if not denom or not truth:
        return None
    if denom != truth and abs(denom - truth) > truth * 0.05:
        num = cba.get("bcr_numerator") or 0
        bcr_full = num / truth if truth else 0
        return _rule("E.4", PERINGATAN, "E",
                     f"CBA cost Rp {denom:,} vs pagu Rp {truth:,}",
                     f"BCR {num/denom:.2f}; jika pakai pagu penuh = {bcr_full:.2f}.",
                     bukti={"bcr_numerator": num, "bcr_denominator": denom, "pagu_RO": truth},
                     draft={"kondisi": f"BCR pakai cost Rp {denom:,}; pagu Rp {truth:,}.",
                            "kriteria": "Kriteria IR2 butir 6.",
                            "akibat": "Skor CBA dipertanyakan.",
                            "rekomendasi": "Hitung ulang BCR pakai pagu."})
    return None


def rule_e5_tenaga_ahli_tidak_di_rab(tor: dict, rab: dict) -> dict | None:
    """E.5 — TA TOR tidak di RAB (struktur)."""
    ta = tor.get("tenaga_ahli", {})
    if not ta.get("disebut"):
        return None
    rab_ta = rab.get("indices", {}).get("tenaga_ahli_items", []) or []
    if rab_ta:
        return None
    return _rule("E.5", PERINGATAN, "E",
                 "Tenaga Ahli TOR tidak di RAB",
                 "TOR menyebut TA, RAB tidak.",
                 bukti={"tor_mencantumkan": ta, "rab_items_tenaga_ahli": len(rab_ta)},
                 draft={"kondisi": "TOR mencantumkan TA; RAB tidak.",
                        "kriteria": "Kriteria IR2 butir 3.a dan 5.",
                        "akibat": "TA tidak teralokasi.",
                        "rekomendasi": "Tambahkan line-item Honor TA."})


def rule_f1_asta_cita_banyak(tor: dict, rab: dict) -> dict | None:
    """F.1 — >= 3 Asta Cita."""
    ac = tor.get("asta_cita", {})
    if ac.get("jumlah", 0) < 3:
        return None
    return _rule("F.1", INFO, "F",
                 f"Narasi merujuk {ac['jumlah']} Asta Cita",
                 "Penandaan terlalu luas.",
                 bukti=ac,
                 draft={"kondisi": f"TOR mengutip {ac['jumlah']} Asta Cita.",
                        "kriteria": "Kriteria IR2 sheet Aspek Reviu.",
                        "akibat": "Mengaburkan fokus evaluasi.",
                        "rekomendasi": "Tetapkan satu Asta Cita utama."})


def rule_e6_rasio_perangkat_iot(tor: dict, rab: dict) -> dict | None:
    """E.6 — rasio IoT vs target."""
    iot = rab.get("indices", {}).get("sewa_iot_items", []) or []
    if not iot:
        return None
    vol = sum((x.get("volume") or 0) for x in iot if x.get("satuan", "").lower() in ("unit", "pkt"))
    target = (tor.get("identitas_ro", {}) or {}).get("volume_int")
    if not target or not vol:
        return None
    rasio = target / vol if vol else 0
    if rasio < 3:
        return None
    return _rule("E.6", PERINGATAN, "E",
                 f"Rasio IoT {rasio:.1f} orang/unit",
                 f"Target {target} orang vs {vol} unit.",
                 bukti={"target_orang": target, "total_unit": vol, "rasio": round(rasio, 2)},
                 draft={"kondisi": f"{vol} unit IoT untuk {target} orang.",
                        "kriteria": "Kriteria IR2 butir 1.b.",
                        "akibat": "Ambiguitas model manfaat.",
                        "rekomendasi": "Tambah narasi pemanfaatan IoT."})


def rule_d6_cba_vs_penerima_manfaat(tor: dict, rab: dict) -> dict | None:
    """D.6 — Penerima manfaat vs CBA."""
    pm = tor.get("penerima_manfaat", []) or []
    if len(pm) <= 1:
        return None
    return _rule("D.6", PERINGATAN, "D",
                 f"CBA mungkin tidak inline {len(pm)} kelompok PM",
                 f"TOR mengidentifikasi {len(pm)} kelompok.",
                 bukti={"jumlah_pm": len(pm), "kelompok": [p.get("ringkasan", "")[:80] for p in pm[:6]]},
                 draft={"kondisi": f"{len(pm)} kelompok PM.",
                        "kriteria": "Kriteria IR2 butir 2.",
                        "akibat": "BCR under-estimated.",
                        "rekomendasi": "Perluas CBA."})


def rule_a1_honor_output_konsentrasi(tor: dict, rab: dict) -> dict | None:
    """A.1 — Honor output di Persiapan."""
    hits = []
    for k in rab.get("komponen", []):
        if k.get("kode", "").endswith(".051") or "persiapan" in (k.get("nama") or "").lower():
            for a in k.get("akun", []):
                if a.get("kode_akun") == "521213":
                    long_h = [r for r in a.get("rincian", [])
                              if (r.get("satuan") or "").upper() in ("OK", "BLN")
                              and (r.get("volume") or 0) >= 10]
                    if long_h:
                        hits.append({"komponen": k["kode"], "akun": a["kode_akun"],
                                     "honor_total": a.get("total")})
    if not hits:
        return None
    total = sum(h.get("honor_total") or 0 for h in hits)
    return _rule("A.1", PERINGATAN, "A",
                 f"Honor di Persiapan durasi panjang (Rp {total:,})",
                 "Honor 10+ bulan terkonsentrasi di Persiapan.",
                 bukti={"hits": hits, "total_honor": total},
                 draft={"kondisi": f"Honor 521213 di Persiapan Rp {total:,}.",
                        "kriteria": "Pasal 14 PMK 62/2023.",
                        "akibat": "Distorsi proporsi biaya.",
                        "rekomendasi": "Realokasi honor sesuai durasi tiap komponen."})


def rule_d4_formula_kpi_belum_operasional(tor: dict, rab: dict) -> dict | None:
    """D.4 — Formula KPI tidak operasional."""
    kpi = tor.get("kpi", {}) or {}
    issues = []
    ikp = kpi.get("ikp_program") or {}
    if ikp.get("ada_formula") and not ikp.get("formula_operasional"):
        issues.append({"level": "IKP", "nama": ikp.get("nama"), "masalah": "tidak operasional"})
    ikk = kpi.get("ikk_kegiatan") or {}
    if ikk.get("ada_formula") and ikk.get("formula_konvensional") is False:
        issues.append({"level": "IKK", "nama": ikk.get("nama"), "masalah": "non-konvensional"})
    if not issues:
        return None
    return _rule("D.4", PERINGATAN, "D",
                 f"Formula KPI tidak operasional ({len(issues)} level)",
                 "Parameter tidak memenuhi standar operasional.",
                 bukti={"issues": issues},
                 draft={"kondisi": "; ".join(f"{i['level']}: {i['masalah']}" for i in issues),
                        "kriteria": "Kriteria IR2 butir 2.b.",
                        "akibat": "Capaian tidak terukur.",
                        "rekomendasi": "Cantumkan bobot dan metode ukur eksplisit."})


def rule_f2_rpjmn_pn_tanpa_butir(tor: dict, rab: dict) -> dict | None:
    """F.2 — RPJMN PN tanpa butir spesifik (struktur)."""
    pen = tor.get("penandaan_cluster", {}) or {}
    c2 = pen.get("cluster_2", []) or []
    rpjmn_pns = [x for x in c2 if "RPJMN PN" in x]
    if not rpjmn_pns:
        return None
    raw = "\n".join(tor.get("raw_text_pages", []) or [])
    has_specific = bool(re.search(r"(kegiatan\s+prioritas|program\s+prioritas|PP\s+\d+|KP\s+\d+)", raw, re.I))
    if has_specific:
        return None
    return _rule("F.2", INFO, "F",
                 f"Penandaan {rpjmn_pns[0]} tanpa butir spesifik",
                 "Tidak merujuk pada Kegiatan/Program Prioritas tertentu.",
                 bukti={"cluster_2": rpjmn_pns},
                 draft={"kondisi": f"Mencentang {rpjmn_pns[0]} tanpa butir.",
                        "kriteria": "Kriteria IR2 sheet Aspek Reviu.",
                        "akibat": "Sulit rekapitulasi kontribusi PN.",
                        "rekomendasi": "Tambahkan kutipan bab/butir RPJMN."})


# ============================================================
# HELPERS
# ============================================================

def _tor_full_text(tor: dict) -> str:
    """Return full TOR text untuk regex/keyword matching, urut prioritas:
    1. raw_text_pages (full body, dari digest_tor.py terbaru)
    2. raw_text / body_text / full_text (legacy fields)
    3. penandaan_cluster.raw_snippet (last resort, hanya 1500 char)
    """
    parts = []
    rp = tor.get("raw_text_pages") or []
    if rp:
        parts.extend(rp)
    if not parts:
        for key in ("raw_text", "body_text", "full_text"):
            v = tor.get(key)
            if isinstance(v, str) and v:
                parts.append(v)
                break
    snip = (tor.get("penandaan_cluster", {}) or {}).get("raw_snippet") or ""
    if snip:
        parts.append(snip)
    return "\n".join(parts)


def _rab_full_text(rab: dict) -> str:
    parts = []
    rp = rab.get("raw_text_pages") or []
    if rp:
        parts.extend(rp)
    if not parts:
        for key in ("raw_text", "body_text", "full_text"):
            v = rab.get(key)
            if isinstance(v, str) and v:
                parts.append(v)
                break
    return "\n".join(parts)


def _parse_num(s: str) -> int:
    if not s:
        return 0
    s = re.sub(r"[\.,]", "", s)
    try:
        return int(s)
    except ValueError:
        return 0


def _rab_line_items(rab: dict) -> list:
    items = []
    for k in rab.get("komponen", []) or []:
        for a in k.get("akun", []) or []:
            ak = a.get("kode_akun", "") or ""
            for r in a.get("rincian", []) or []:
                items.append({
                    "akun": ak,
                    "deskripsi": r.get("deskripsi", "") or "",
                    "satuan": (r.get("satuan") or "").lower(),
                    "harga_satuan": r.get("harga_satuan") or 0,
                    "volume": r.get("volume") or 0,
                    "total": r.get("total") or 0,
                })
    raw = _rab_full_text(rab)
    if not raw:
        return items
    current_akun = ""
    for ln in raw.splitlines():
        ln_strip = ln.strip()
        if not ln_strip:
            continue
        m = re.match(r"^(5\d{5})\b", ln_strip)
        if m:
            current_akun = m.group(1)
            continue
        sat_m = re.search(r"\b(\d+(?:[\.,]\d+)?)\s*(unit|pkt|paket|orang|bln|jam|kali|kegiatan|lokasi|set|buah|tahun|thn|hari|ok|pks)\b",
                          ln_strip, re.I)
        nums = re.findall(r"(?<![\d\.])\d{1,3}(?:[\.,]\d{3}){2,}|\d{7,}", ln_strip)
        try:
            vol_val = float(sat_m.group(1).replace(",", ".")) if sat_m else 0
        except ValueError:
            vol_val = 0
        items.append({
            "akun": current_akun,
            "deskripsi": ln_strip[:200],
            "satuan": (sat_m.group(2).lower() if sat_m else ""),
            "volume": vol_val,
            "harga_satuan": _parse_num(nums[-2]) if len(nums) >= 2 else 0,
            "total": _parse_num(nums[-1]) if nums else 0,
        })
    return items


# ============================================================
# 18 ALT RULES
# ============================================================

def rule_b_alt_1_akun_526_sewa(tor, rab):
    kws = ["sewa", "rental", "lease", "berlangganan", "penyewaan", "domain", "ssl", "hosting"]
    hits = []
    for it in _rab_line_items(rab):
        akun = it.get("akun", "") or ""
        desc = (it.get("deskripsi") or "").lower()
        if akun.startswith("526") and any(kw in desc for kw in kws):
            hits.append({"akun": akun, "deskripsi": it["deskripsi"][:160]})
    if not hits:
        return None
    ro = (tor.get("identitas_ro", {}) or {}).get("ro") or "RO ini"
    return _rule("B.alt-1", PERINGATAN, "B",
                 "Akun belanja barang persediaan (526xxx) digunakan untuk sewa",
                 f"Ditemukan {len(hits)} line-item RAB dengan akun 526xxx untuk sewa/berlangganan.",
                 bukti={"hits": hits[:8]},
                 draft={"kondisi": f"RAB {ro} memuat {len(hits)} line-item akun 526xxx untuk sewa.",
                        "kriteria": "PMK 102/2018 jo. PMK 187/2019.",
                        "akibat": "Mismatch klasifikasi akun.",
                        "rekomendasi": "Reklasifikasi ke 522141."})


def rule_b_alt_2_521_untuk_modal(tor, rab):
    kws_modal = ["pembelian server", "pembelian laptop", "pembelian komputer",
                 "pengadaan perangkat keras", "pengadaan hardware"]
    hits = []
    for it in _rab_line_items(rab):
        akun = it.get("akun", "") or ""
        desc = (it.get("deskripsi") or "").lower()
        if not akun.startswith("521"):
            continue
        match_kw = any(kw in desc for kw in kws_modal)
        sat = (it.get("satuan") or "").lower()
        harga = it.get("harga_satuan") or 0
        match_unit = (sat == "unit" and harga > 5_000_000)
        if match_kw or match_unit:
            hits.append({"akun": akun, "deskripsi": it["deskripsi"][:160], "satuan": sat, "harga_satuan": harga})
    if not hits:
        return None
    ro = (tor.get("identitas_ro", {}) or {}).get("ro") or "RO ini"
    return _rule("B.alt-2", PERINGATAN, "B",
                 "Akun belanja barang operasional (521xxx) digunakan untuk barang modal",
                 f"Ditemukan {len(hits)} line-item.",
                 bukti={"hits": hits[:8]},
                 draft={"kondisi": f"RAB {ro} {len(hits)} item modal di 521xxx.",
                        "kriteria": "PMK 102/2018 jo. PMK 187/2019.",
                        "akibat": "Berdampak pada BMN.",
                        "rekomendasi": "Reklasifikasi ke 53xxxx."})


def rule_b_alt_3_honor_narsum_lebih_8jam(tor, rab):
    hits = []
    for it in _rab_line_items(rab):
        desc = (it.get("deskripsi") or "").lower()
        sat = (it.get("satuan") or "").lower()
        vol = it.get("volume") or 0
        if ("honor narasumber" in desc or "honor narsum" in desc) and sat == "jam" and vol > 8:
            hits.append({"akun": it.get("akun"), "deskripsi": it["deskripsi"][:160], "volume": vol})
    if not hits:
        return None
    ro = (tor.get("identitas_ro", {}) or {}).get("ro") or "RO ini"
    return _rule("B.alt-3", PERINGATAN, "B",
                 "Honor narasumber melebihi 8 jam per orang per kegiatan",
                 f"Ditemukan {len(hits)} item honor narasumber >8 jam.",
                 bukti={"hits": hits[:8]},
                 draft={"kondisi": f"RAB {ro} honor narasumber >8 jam.",
                        "kriteria": "PMK SBM - maks 8 jam/orang/kegiatan.",
                        "akibat": "Dikoreksi penelaahan.",
                        "rekomendasi": "Sesuaikan ambang SBM."})


def rule_b_alt_4_konsumsi_diatas_sbm(tor, rab):
    kws = ["makan", "minum", "konsumsi", "snack"]
    hits = []
    for it in _rab_line_items(rab):
        akun = it.get("akun", "") or ""
        desc = (it.get("deskripsi") or "").lower()
        harga = it.get("harga_satuan") or 0
        if akun.startswith("521") and any(kw in desc for kw in kws) and harga > 100_000:
            hits.append({"akun": akun, "deskripsi": it["deskripsi"][:160], "harga_satuan": harga})
    if not hits:
        return None
    ro = (tor.get("identitas_ro", {}) or {}).get("ro") or "RO ini"
    return _rule("B.alt-4", PERINGATAN, "B",
                 "Konsumsi melebihi SBM 2026 (>Rp 100.000/orang)",
                 f"Ditemukan {len(hits)} item konsumsi >Rp 100k.",
                 bukti={"hits": hits[:8]},
                 draft={"kondisi": f"RAB {ro} memuat konsumsi >Rp 100k. Ambang SBM 2026 (PMK 32/2025): Rp 50k-80k/orang.",
                        "kriteria": "PMK 32/2025 SBM TA 2026.",
                        "akibat": "Dikoreksi penelaahan.",
                        "rekomendasi": "Sesuaikan ambang SBM 2026."})


def rule_b_alt_5_persiapan_lebih_30pct(tor, rab):
    total = rab.get("total_pagu") or (tor.get("biaya", {}) or {}).get("total") or 0
    if not total:
        return None
    persiapan_total = 0
    kandidat = []
    for k in rab.get("komponen", []) or []:
        nama = (k.get("nama") or "").lower()
        kode = (k.get("kode") or "")
        if "persiapan" in nama or kode.endswith(".051"):
            tot = k.get("total") or 0
            if not tot:
                tot = sum((a.get("total") or 0) for a in (k.get("akun") or []))
            persiapan_total += tot
            kandidat.append({"kode": kode, "nama": k.get("nama"), "total": tot})
    if not kandidat or persiapan_total <= 0:
        return None
    pct = persiapan_total / total
    if pct <= 0.30:
        return None
    ro = (tor.get("identitas_ro", {}) or {}).get("ro") or "RO ini"
    return _rule("B.alt-5", PERINGATAN, "B",
                 "Komponen Persiapan menyerap >30% pagu RO",
                 f"Persiapan {pct*100:.1f}% (Rp {persiapan_total:,}/Rp {total:,}).",
                 bukti={"komponen": kandidat, "total_pagu": total, "rasio": round(pct, 4)},
                 draft={"kondisi": f"Persiapan {ro} {pct*100:.1f}% pagu.",
                        "kriteria": "Pasal 14 PMK 62/2023.",
                        "akibat": "Distorsi proporsi.",
                        "rekomendasi": "Realokasi ke pelaksanaan."})


def rule_c_alt_1_cluster_ganda_eksplisit(tor, rab):
    raw = _tor_full_text(tor)
    if not raw:
        return None
    has_c1 = bool(re.search(r"\bCluster\s*1\b", raw, re.I))
    has_c2 = bool(re.search(r"\bCluster\s*2\b", raw, re.I))
    if not (has_c1 and has_c2):
        return None
    snippets = re.findall(r"Cluster\s*[12]\b.{0,40}", raw, re.I)
    has_or = any(re.search(r"\b(atau|or)\b", s, re.I) for s in snippets)
    if has_or:
        return None
    return _rule("C.alt-1", PERINGATAN, "C",
                 "TOR menyebut Cluster 1 dan Cluster 2 secara eksplisit",
                 "Penandaan ganda tanpa konteks 'atau'.",
                 bukti={"snippets": snippets[:4]},
                 draft={"kondisi": "Cluster 1 dan 2 disebut bersamaan.",
                        "kriteria": "Pedoman penandaan Bappenas/Kemenkeu.",
                        "akibat": "Sulit rekapitulasi tematik.",
                        "rekomendasi": "Tetapkan satu cluster utama."})


def rule_c_alt_2_penandaan_tematik_inkonsisten(tor, rab):
    kws = ["Prioritas Nasional", "Major Project", "Belanja Wajib", "Belanja Operasional"]
    raw_tor = _tor_full_text(tor).lower()
    raw_rab = _rab_full_text(rab).lower()
    diffs = []
    for kw in kws:
        in_tor = kw.lower() in raw_tor
        in_rab = kw.lower() in raw_rab
        if in_tor != in_rab:
            diffs.append({"keyword": kw, "in_tor": in_tor, "in_rab": in_rab})
    if not diffs:
        return None
    return _rule("C.alt-2", INFO, "C",
                 f"Penandaan tematik tidak konsisten TOR vs RAB ({len(diffs)} keyword)",
                 f"Keyword di salah satu dokumen saja: {[d['keyword'] for d in diffs]}.",
                 bukti={"diffs": diffs},
                 draft={"kondisi": "Penandaan TOR vs RAB beda.",
                        "kriteria": "Pasal 61 PMK 107/2024.",
                        "akibat": "Sulit rekapitulasi.",
                        "rekomendasi": "Selaraskan penandaan."})


def rule_c_alt_3_berkesinambungan_tanpa_baseline(tor, rab):
    raw = _tor_full_text(tor)
    if not raw:
        return None
    kws = ["berkesinambungan", "lanjutan", "kontinu"]
    found = [kw for kw in kws if re.search(r"\b" + kw + r"\b", raw, re.I)]
    if not found:
        return None
    has_2026 = bool(re.search(r"\bTA\s*2026\b|\btahun\s+anggaran\s+2026\b", raw, re.I))
    if has_2026:
        return None
    return _rule("C.alt-3", INFO, "C",
                 "RO 'berkesinambungan' tanpa referensi baseline TA 2026",
                 f"Keyword '{found[0]}' tetapi tidak ada TA 2026.",
                 bukti={"keyword_ditemukan": found},
                 draft={"kondisi": f"RO ditandai '{found[0]}' tanpa referensi TA 2026.",
                        "kriteria": "Kriteria IR2 butir 1.b.",
                        "akibat": "Sulit menilai kewajaran.",
                        "rekomendasi": "Tambahkan baseline RO TA 2026."})


def rule_e_alt_1_lokasi_target_inkonsisten(tor, rab):
    raw = _tor_full_text(tor)
    if not raw:
        return None
    has_nas = bool(re.search(r"\b(nasional|seluruh\s+Indonesia|Indonesia)\b", raw, re.I))
    if not has_nas:
        return None
    cities = ["Jakarta", "Surabaya", "Bandung", "Medan", "Semarang", "Yogyakarta",
              "Makassar", "Denpasar", "Palembang", "Banjarmasin", "Pontianak",
              "Manado", "Padang", "Pekanbaru", "Balikpapan", "Bogor"]
    found = [c for c in cities if re.search(r"\b" + c + r"\b", raw)]
    has_pj = bool(re.search(r"Pulau\s+Jawa", raw, re.I))
    # Threshold: nasional = 38 provinsi / ~500 kab-kota. Jika TOR menyebut <10 kota
    # eksplisit dan mengklaim nasional, tetap inkonsisten (cakupan tidak merata).
    if len(found) >= 10:
        return None
    if not found and not has_pj:
        return None
    ro = (tor.get("identitas_ro", {}) or {}).get("ro") or "RO ini"
    return _rule("E.alt-1", PERINGATAN, "E",
                 "Inkonsistensi target nasional vs lokasi yang disebut TOR",
                 f"TOR menargetkan cakupan nasional namun lokasi spesifik yang disebut hanya {len(found)} kota: {found}.",
                 bukti={"cities_disebut": found, "has_pulau_jawa": has_pj, "klaim_nasional": has_nas},
                 draft={"kondisi": f"TOR {ro} menyatakan target nasional tetapi lokasi yang disebut hanya {found or ['Pulau Jawa']}.",
                        "kriteria": "Konsistensi narasi target dan lokasi pada TOR.",
                        "akibat": "Risiko output tidak mewakili sasaran nasional.",
                        "rekomendasi": "Perluas lokasi pelaksanaan atau revisi narasi target."})


def rule_e_alt_2_sektor_leakage(tor, rab):
    raw = _tor_full_text(tor)
    if not raw:
        return None
    ro_name = ((tor.get("identitas_ro", {}) or {}).get("ro") or "").lower()
    foreign = ["pertanian", "kesehatan", "pendidikan", "perikanan", "kelautan"]
    leaks = []
    for kw in foreign:
        if kw in ro_name:
            continue
        all_m = re.findall(r".{0,50}\b" + kw + r"\b.{0,50}", raw, re.I)
        filtered = [m for m in all_m if not re.search(r"6\s+[Ss]ektor|sektor\s+strategis", m, re.I)]
        if len(filtered) > 5:
            leaks.append({"keyword": kw, "count": len(filtered), "samples": [m.strip()[:120] for m in filtered[:2]]})
    if not leaks:
        return None
    return _rule("E.alt-2", PERINGATAN, "E",
                 "Sektor leakage substansial dalam narasi TOR",
                 f"Sektor lain disebut >5 kali: {[l['keyword'] for l in leaks]}.",
                 bukti={"leaks": leaks},
                 draft={"kondisi": f"Sektor lain ({', '.join(l['keyword'] for l in leaks)}) >5 mention.",
                        "kriteria": "Kriteria IR2 butir 3.b.",
                        "akibat": "Menurunkan kredibilitas.",
                        "rekomendasi": "Find-and-replace TOR."})


def rule_e_alt_3_tenaga_ahli_tor_tidak_di_rab(tor, rab):
    raw_tor = _tor_full_text(tor)
    ta = (tor.get("tenaga_ahli", {}) or {}).get("disebut") or False
    if not ta and raw_tor:
        ta = bool(re.search(r"\b(tenaga\s+ahli)\b", raw_tor, re.I))
    if not ta:
        return None
    raw_rab = _rab_full_text(rab).lower()
    kws = ["tenaga ahli", "konsultan", "narasumber expert"]
    if any(kw in raw_rab for kw in kws):
        return None
    has_522 = False
    for it in _rab_line_items(rab):
        ak = it.get("akun", "") or ""
        if ak.startswith("522") and any(kw in (it.get("deskripsi") or "").lower() for kw in kws):
            has_522 = True
            break
    if has_522:
        return None
    ro = (tor.get("identitas_ro", {}) or {}).get("ro") or "RO ini"
    return _rule("E.alt-3", PERINGATAN, "E",
                 "Tenaga Ahli disebut di TOR tetapi tidak ditemukan line-item RAB",
                 "TOR menyebut kebutuhan Tenaga Ahli tetapi RAB tidak memuat line-item Tenaga Ahli (perlu verifikasi apakah ter-cover via akun 522131 Jasa Konsultan).",
                 bukti={"tor_sebut_ta": True, "rab_ada_line_ta": False},
                 draft={"kondisi": f"TOR {ro} menyebut TA; RAB tidak memuat line-item TA/Konsultan eksplisit.",
                        "kriteria": "Kriteria IR2 butir 3.a dan 5.",
                        "akibat": "Eksekusi terhambat atau memicu revisi.",
                        "rekomendasi": "Tambahkan line-item TA atau revisi narasi TOR."})


def rule_e_alt_4_unit_cost_tinggi(tor, rab):
    total = rab.get("total_pagu") or (tor.get("biaya", {}) or {}).get("total") or 0
    if not total:
        return None
    ir = tor.get("identitas_ro", {}) or {}
    vol = ir.get("volume_int") or ir.get("volume")
    vol_int = None
    if isinstance(vol, int):
        vol_int = vol
    elif isinstance(vol, str):
        m = re.search(r"\d+", vol)
        if m:
            vol_int = int(m.group())
    if not vol_int or vol_int <= 0:
        return None
    uc = total / vol_int
    if uc <= 4_000_000_000:
        return None
    ro = ir.get("ro") or "RO ini"
    return _rule("E.alt-4", PERINGATAN, "E",
                 f"Unit cost per output sangat tinggi (Rp {uc/1_000_000:.0f} jt/output)",
                 f"Volume {vol_int} dengan pagu Rp {total:,} menghasilkan unit cost Rp {int(uc):,}/output.",
                 bukti={"volume": vol_int, "pagu": total, "unit_cost": int(uc)},
                 draft={"kondisi": f"{ro} memiliki volume target {vol_int} dengan pagu Rp {total:,}, sehingga unit cost ~Rp {int(uc):,}/output.",
                        "kriteria": "Prinsip kewajaran biaya per unit output.",
                        "akibat": "Unit cost tinggi berisiko menjadi temuan kewajaran.",
                        "rekomendasi": "Justifikasi rinci komponen biaya per output."})


def rule_e_alt_5_duplikasi_ro_cross(tor, rab):
    """Placeholder. Cross-RO check via cross_check_batch."""
    return None


def rule_e_alt_6_tidak_ada_baseline(tor, rab):
    raw = _tor_full_text(tor)
    if not raw:
        return None
    kws = ["baseline", "tahun sebelumnya", "TA 2026", "kondisi awal"]
    if any(re.search(r"\b" + re.escape(kw) + r"\b", raw, re.I) for kw in kws):
        return None
    ro = (tor.get("identitas_ro", {}) or {}).get("ro") or "RO ini"
    return _rule("E.alt-6", INFO, "E",
                 "TOR tidak mencantumkan baseline tahun sebelumnya secara eksplisit",
                 "TOR tidak menyajikan baseline (capaian tahun sebelumnya).",
                 bukti={"keywords_tidak_ditemukan": kws},
                 draft={"kondisi": f"TOR {ro} tidak memuat baseline.",
                        "kriteria": "PMK 107/2024.",
                        "akibat": "Sulit mengukur peningkatan kinerja.",
                        "rekomendasi": "Cantumkan baseline TA 2026."})


def rule_f_alt_1_asta_cita_generik(tor, rab):
    raw = _tor_full_text(tor)
    if not raw:
        return None
    matches = list(re.finditer(r"Asta\s*Cita", raw, re.I))
    if not matches:
        return None
    has_specific = False
    for m in matches:
        # Look only AFTER the "Asta Cita" mention untuk angka 1-8 (bukan tahun seperti 2025-2029)
        window = raw[m.end():m.end() + 30]
        # Strip year-like patterns (4 digits or year ranges) untuk hindari false positive
        cleaned = re.sub(r"\b\d{4}(?:[-/]\d{4})?\b", "", window)
        if re.search(r"\b[1-8]\b|ke[-\s]*[1-8]\b", cleaned):
            has_specific = True
            break
    if has_specific:
        return None
    ro = (tor.get("identitas_ro", {}) or {}).get("ro") or "RO ini"
    sample = raw[matches[0].start():matches[0].start() + 80].strip()
    return _rule("F.alt-1", INFO, "F",
                 "Asta Cita disebut generik tanpa nomor spesifik (1-8)",
                 "TOR merujuk Asta Cita tanpa nomor misi presiden spesifik.",
                 bukti={"sample": sample},
                 draft={"kondisi": f"TOR {ro} sebut Asta Cita tanpa nomor.",
                        "kriteria": "Pedoman penandaan tematik 2025-2029.",
                        "akibat": "Sulit telusuri kontribusi misi presiden.",
                        "rekomendasi": "Cantumkan Asta Cita ke-N (1-8) untuk traceability."})


def rule_f_alt_2_rpjmn_pn_tanpa_butir(tor, rab):
    raw = _tor_full_text(tor)
    if not raw:
        return None
    has_ruj = bool(re.search(r"\b(RPJMN|Prioritas\s+Nasional|\bPN\b)", raw, re.I))
    if not has_ruj:
        return None
    has_spec = bool(re.search(r"\bPN\s*\d+\b|\bBab\s*[IVX]+\.\d+", raw, re.I))
    if has_spec:
        return None
    ro = (tor.get("identitas_ro", {}) or {}).get("ro") or "RO ini"
    return _rule("F.alt-2", INFO, "F",
                 "RPJMN/Prioritas Nasional disebut tanpa nomor PN spesifik",
                 "TOR merujuk RPJMN/PN namun tidak mencantumkan nomor PN spesifik.",
                 bukti={"has_rujukan_generik": True, "has_pn_spesifik": False},
                 draft={"kondisi": f"TOR {ro} sebut RPJMN/PN tanpa nomor.",
                        "kriteria": "Pedoman penandaan RPJMN 2025-2029.",
                        "akibat": "Sulit telusuri kontribusi PN.",
                        "rekomendasi": "Cantumkan PN-N spesifik (mis. PN 4 / Bab IV.2)."})


def rule_f_alt_3_major_project_tor_tidak_di_rab(tor, rab):
    raw_tor = _tor_full_text(tor)
    raw_rab = _rab_full_text(rab)
    if not bool(re.search(r"\bMajor\s+Project\b", raw_tor)):
        return None
    if bool(re.search(r"\bMajor\s+Project\b", raw_rab)):
        return None
    ro = (tor.get("identitas_ro", {}) or {}).get("ro") or "RO ini"
    return _rule("F.alt-3", INFO, "F",
                 "Major Project disebut di TOR tidak konsisten dengan RAB",
                 "TOR mereferensikan 'Major Project' tetapi RAB tidak.",
                 bukti={"has_mp_tor": True, "has_mp_rab": False},
                 draft={"kondisi": f"TOR {ro} sebut MP; RAB tidak.",
                        "kriteria": "Konsistensi penandaan tematik TOR-RAB.",
                        "akibat": "Sulit rekapitulasi MP.",
                        "rekomendasi": "Tambahkan penandaan MP pada RAB atau koreksi TOR."})


def rule_f_alt_4_tjsl_sdg_tidak_relevan(tor, rab):
    raw = _tor_full_text(tor)
    if not raw:
        return None
    has = bool(re.search(r"\b(TJSL|Tanggung\s+Jawab\s+Sosial|SDG|Sustainable\s+Development\s+Goal)\b", raw, re.I))
    if not has:
        return None
    sdg_nums = re.findall(r"SDG\s*[#]?\s*(\d{1,2})", raw, re.I)
    sdg_nums = [int(n) for n in sdg_nums if 1 <= int(n) <= 17]
    if not sdg_nums:
        return _rule("F.alt-4", INFO, "F",
                     "TJSL/SDG disebut tanpa nomor SDG spesifik",
                     "TOR merujuk TJSL/SDG tanpa mencantumkan nomor SDG (1-17).",
                     bukti={"has_tjsl_sdg": True, "sdg_nomor_ditemukan": []},
                     draft={"kondisi": "TJSL/SDG tanpa nomor.",
                            "kriteria": "Pedoman SDG/TJSL.",
                            "akibat": "Sulit petakan kontribusi SDG.",
                            "rekomendasi": "Cantumkan nomor SDG (1-17)."})
    ro_name = ((tor.get("identitas_ro", {}) or {}).get("ro") or "").lower()
    mismatches = []
    if 14 in sdg_nums and not re.search(r"perikanan|kelautan|laut|maritim", ro_name):
        mismatches.append({"sdg": 14, "alasan": "SDG 14 di RO non-kelautan"})
    if 2 in sdg_nums and not re.search(r"pangan|pertanian|gizi", ro_name):
        mismatches.append({"sdg": 2, "alasan": "SDG 2 di RO non-pangan"})
    if not mismatches:
        return None
    return _rule("F.alt-4", INFO, "F",
                 "TJSL/SDG referensi tampak tidak match kategori RO",
                 f"SDG yang dirujuk tampak tidak relevan: {mismatches}.",
                 bukti={"sdg_nomor": sdg_nums, "potential_mismatch": mismatches},
                 draft={"kondisi": f"TOR rujuk SDG {sdg_nums} sebagian tidak relevan.",
                        "kriteria": "Konsistensi pemetaan SDG.",
                        "akibat": "Pemetaan SDG tidak relevan.",
                        "rekomendasi": "Tinjau ulang nomor SDG."})


# ============================================================
# CROSS-RO RULES (mode batch)
# ============================================================

def cross_rule_e_alt_5_duplikasi_target(tor_list, rab_list):
    stop = {"dan", "yang", "untuk", "dengan", "pada", "ke", "di", "dari", "atau",
            "the", "of", "and", "for", "to", "a", "an", "layanan", "kegiatan",
            "rincian", "output", "ro", "ta"}

    def kw_of(nm):
        if not nm:
            return set()
        words = re.findall(r"[A-Za-zÀ-ÿ]+", nm.lower())
        words = [w for w in words if w not in stop and len(w) > 2]
        return set(words[:5])

    keys = []
    for i, t in enumerate(tor_list):
        nm = ((t.get("identitas_ro", {}) or {}).get("ro") or "") or \
             ((t.get("metadata", {}) or {}).get("source_file") or "")
        keys.append({"idx": i, "nama": nm, "keywords": kw_of(nm)})

    found = []
    n = len(keys)
    for i in range(n):
        for j in range(i + 1, n):
            ki = keys[i]["keywords"]
            kj = keys[j]["keywords"]
            if not ki or not kj:
                continue
            inter = ki & kj
            if not inter:
                continue
            min_len = min(len(ki), len(kj))
            ov = len(inter) / min_len if min_len > 0 else 0
            if ov > 0.70:
                found.append({"ro_a_idx": i, "ro_a_nama": keys[i]["nama"],
                              "ro_b_idx": j, "ro_b_nama": keys[j]["nama"],
                              "overlap_keyword": sorted(inter),
                              "overlap_rasio": round(ov, 2)})
    results = []
    for f in found:
        a = _rule("E.alt-5", PERINGATAN, "E",
                  f"Indikasi duplikasi/mismatch RO {f['ro_a_nama']} vs RO {f['ro_b_nama']}",
                  f"Overlap kata kunci output {f['overlap_keyword']} antara RO #{f['ro_a_idx']+1} dan RO #{f['ro_b_idx']+1} ({f['overlap_rasio']*100:.0f}%).",
                  bukti=f,
                  draft={"kondisi": f"RO #{f['ro_a_idx']+1} dan #{f['ro_b_idx']+1} bersinggungan tema.",
                         "kriteria": "Prinsip non-duplikasi RO.",
                         "akibat": "Risiko duplikasi pengukuran.",
                         "rekomendasi": "Konsolidasi atau pertegas pemisahan output."})
        a["ro_pair"] = [f["ro_a_idx"] + 1, f["ro_b_idx"] + 1]
        results.append(a)
    return results


# ============================================================
# REGISTRY
# ============================================================

ALL_RULES = [
    rule_a1_honor_output_konsentrasi,
    rule_a2_sewa_kendaraan_pejabat,
    rule_a3_sbm_belum_terbit,
    rule_b1_akun_526_untuk_sewa,
    rule_b2_522191_untuk_konstruksi,
    rule_b3_duplikasi_komponen,
    rule_c1_penandaan_ganda,
    rule_d1_dasar_hukum_tanpa_pasal,
    rule_d2_regulasi_tidak_relevan,
    rule_d3_iro_inkonsistensi,
    rule_d4_formula_kpi_belum_operasional,
    rule_d5_mr_belum_lengkap,
    rule_d6_cba_vs_penerima_manfaat,
    rule_e1_lokasi_non_target_disebut,
    rule_e2_sektor_asing_di_narasi,
    rule_e3_baseline_inkonsisten,
    rule_e4_cba_cost_inkonsisten,
    rule_e5_tenaga_ahli_tidak_di_rab,
    rule_e6_rasio_perangkat_iot,
    rule_f1_asta_cita_banyak,
    rule_f2_rpjmn_pn_tanpa_butir,
    # 18 ALT-RULES (Mei 2026)
    rule_b_alt_1_akun_526_sewa,
    rule_b_alt_2_521_untuk_modal,
    rule_b_alt_3_honor_narsum_lebih_8jam,
    rule_b_alt_4_konsumsi_diatas_sbm,
    rule_b_alt_5_persiapan_lebih_30pct,
    rule_c_alt_1_cluster_ganda_eksplisit,
    rule_c_alt_2_penandaan_tematik_inkonsisten,
    rule_c_alt_3_berkesinambungan_tanpa_baseline,
    rule_e_alt_1_lokasi_target_inkonsisten,
    rule_e_alt_2_sektor_leakage,
    rule_e_alt_3_tenaga_ahli_tor_tidak_di_rab,
    rule_e_alt_4_unit_cost_tinggi,
    rule_e_alt_5_duplikasi_ro_cross,
    rule_e_alt_6_tidak_ada_baseline,
    rule_f_alt_1_asta_cita_generik,
    rule_f_alt_2_rpjmn_pn_tanpa_butir,
    rule_f_alt_3_major_project_tor_tidak_di_rab,
    rule_f_alt_4_tjsl_sdg_tidak_relevan,
]


def run_checks(tor, rab):
    results = []
    for rfn in ALL_RULES:
        try:
            r = rfn(tor, rab)
            if r:
                results.append(r)
        except Exception as e:
            results.append({"rule_id": rfn.__name__, "severity": "ERROR", "error": str(e)})
    return results


def cross_check_batch(tor_paths, rab_paths):
    def _suf(p):
        m = re.search(r"(\d+)\.json$", str(p))
        return int(m.group(1)) if m else -1

    tm = {_suf(p): p for p in tor_paths if _suf(p) >= 0}
    rm = {_suf(p): p for p in rab_paths if _suf(p) >= 0}
    common = sorted(set(tm.keys()) & set(rm.keys()))

    all_t = []
    all_r = []
    all_a = []
    per_ro = []

    for rid in common:
        t = json.loads(Path(tm[rid]).read_text(encoding="utf-8"))
        r = json.loads(Path(rm[rid]).read_text(encoding="utf-8"))
        all_t.append(t)
        all_r.append(r)
        nm = ((t.get("identitas_ro", {}) or {}).get("ro") or
              ((t.get("metadata", {}) or {}).get("source_file") or f"RO #{rid}"))
        anoms = run_checks(t, r)
        for a in anoms:
            a["ro_id"] = rid
            a["ro_nama"] = nm
            all_a.append(a)
        per_ro.append({"ro_id": rid, "ro_nama": nm, "jumlah_anomali": len(anoms)})

    cross = cross_rule_e_alt_5_duplikasi_target(all_t, all_r)
    for a in cross:
        if a.get("ro_pair"):
            ia = a["ro_pair"][0] - 1
            if 0 <= ia < len(common):
                a["ro_id"] = common[ia]
                a["ro_nama"] = ((all_t[ia].get("identitas_ro", {}) or {}).get("ro") or "")
    all_a.extend(cross)

    summ = {"total_ro": len(common),
            "ro_dengan_anomali": sum(1 for r in per_ro if r["jumlah_anomali"] > 0),
            "total_anomali": len(all_a),
            "per_severity": {}, "per_aspek": {}, "per_rule_id": {}, "per_ro": per_ro}
    for a in all_a:
        sv = a.get("severity", "?")
        asp = a.get("aspek", "?")
        rid = a.get("rule_id", "?")
        summ["per_severity"][sv] = summ["per_severity"].get(sv, 0) + 1
        summ["per_aspek"][asp] = summ["per_aspek"].get(asp, 0) + 1
        summ["per_rule_id"][rid] = summ["per_rule_id"].get(rid, 0) + 1

    return {"penugasan": "Reviu RKA-K/L (batch mode)", "tanggal_pipeline": None,
            "ringkasan": summ, "anomalies": all_a}


def _self_check_ast():
    import ast
    try:
        ast.parse(open(__file__, "r", encoding="utf-8").read())
    except SyntaxError as e:
        print(f"Self-check AST gagal di {__file__}: {e}", file=sys.stderr)
        sys.exit(2)


def main(argv=None):
    _self_check_ast()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("tor_json", nargs="?")
    ap.add_argument("rab_json", nargs="?")
    ap.add_argument("-o", "--output", default=None)
    ap.add_argument("--batch", action="store_true")
    ap.add_argument("--tor-dir", default=None)
    ap.add_argument("--rab-dir", default=None)
    args = ap.parse_args(argv)

    if args.batch:
        if not args.tor_dir or not args.rab_dir:
            ap.error("--batch membutuhkan --tor-dir dan --rab-dir")
        tps = sorted(Path(args.tor_dir).glob("tor-*.json"))
        rps = sorted(Path(args.rab_dir).glob("rab-*.json"))
        if not tps:
            ap.error(f"Tidak ada tor-*.json di {args.tor_dir}")
        if not rps:
            ap.error(f"Tidak ada rab-*.json di {args.rab_dir}")
        out = cross_check_batch(tps, rps)
        op = args.output or "anomalies-master.json"
        Path(op).write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"=== CROSS-CHECK BATCH RESULT ===")
        print(f"Total RO: {out['ringkasan']['total_ro']}")
        print(f"Total anomalies: {out['ringkasan']['total_anomali']}")
        print(f"By Severity: {out['ringkasan']['per_severity']}")
        print(f"By Aspek: {out['ringkasan']['per_aspek']}")
        print(f"Top rule_id: {dict(sorted(out['ringkasan']['per_rule_id'].items(), key=lambda x: -x[1])[:10])}")
        print(f"Output: {op}")
        return 0

    if not args.tor_json or not args.rab_json:
        ap.error("Single-RO mode butuh tor_json dan rab_json")

    tor = json.loads(Path(args.tor_json).read_text(encoding="utf-8"))
    rab = json.loads(Path(args.rab_json).read_text(encoding="utf-8"))
    anoms = run_checks(tor, rab)

    out = {"metadata": {"tor_source": tor.get("metadata", {}).get("source_file"),
                        "rab_source": rab.get("metadata", {}).get("source_file"),
                        "total_rules_tested": len(ALL_RULES),
                        "total_anomalies_found": len(anoms)},
           "summary_by_aspek": {}, "summary_by_severity": {}, "anomalies": anoms}
    for a in anoms:
        asp = a.get("aspek", "?")
        sv = a.get("severity", "?")
        out["summary_by_aspek"][asp] = out["summary_by_aspek"].get(asp, 0) + 1
        out["summary_by_severity"][sv] = out["summary_by_severity"].get(sv, 0) + 1

    op = args.output or "anomalies.json"
    Path(op).write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"=== CROSS-CHECK RESULT ===")
    print(f"Tested: {len(ALL_RULES)} rules")
    print(f"Found: {len(anoms)} anomalies")
    print(f"By Aspek: {out['summary_by_aspek']}")
    print(f"By Severity: {out['summary_by_severity']}")
    print(f"Output: {op}")
    print()
    print("--- DETAIL ---")
    for a in anoms:
        print(f"  [{a.get('severity', '?'):11s}] {a.get('rule_id', '?'):8s} ({a.get('aspek', '?')}) - {a.get('judul', '?')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
