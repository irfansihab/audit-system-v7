"""
digest_tor.py — Parser TOR/KAK RKA-K/L → JSON terstruktur.

Usage:
    python digest_tor.py <path-to-tor.pdf> [-o output.json]

Ekstrak blok-blok substansi TOR sesuai Kriteria IR2:
    1. Identitas RO (program/kegiatan/KRO/RO/volume/penandaan)
    2. Latar Belakang (dasar hukum, urgensi, deskripsi, lokasi)
    3. Penerima Manfaat
    4. KPI (Indikator Program/Kegiatan/RO)
    5. Strategi Pencapaian (metode pelaksanaan, timeline, deliverables)
    6. Kurun Waktu Pencapaian
    7. Biaya
    8. CBA (Cost-Benefit Analysis)
    9. Manajemen Risiko

Pendekatan: heuristik regex atas teks PDF (tidak full semantic parsing).
Akurasi target 80–90% untuk field struktural; sisanya disimpan sebagai
raw_text_pages untuk fallback inspeksi Claude.
"""

from __future__ import annotations
import argparse
import json
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import Any


# ------------- helpers -------------

def _clean_ws(text: str) -> str:
    """Collapse whitespace."""
    return re.sub(r"\s+", " ", text).strip()


def _rupiah_to_int(s: str) -> int | None:
    """Parse 'Rp10.500.000.000' or '10,500,000,000' or '10.500 M' to int."""
    if s is None:
        return None
    s = s.strip()
    m = re.search(r"Rp?\s*([\d\.,]+)", s)
    if not m:
        m = re.search(r"([\d\.,]+)", s)
    if not m:
        return None
    num = m.group(1).replace(".", "").replace(",", "")
    try:
        return int(num)
    except ValueError:
        return None


def _pdftotext_pages(path: str | Path) -> list[str]:
    """Extract text per halaman pakai pdftotext -layout. Lebih cepat & robust dari pdfplumber.

    Fallback ke pdfplumber jika pdftotext tidak tersedia.
    """
    if not shutil.which("pdftotext"):
        # Fallback: pdfplumber legacy path
        try:
            import pdfplumber
        except ImportError:
            sys.exit("ERROR: pdftotext tidak tersedia di PATH dan pdfplumber tidak terinstall. "
                     "Install poppler-utils (Linux/macOS) atau pip install pdfplumber.")
        with pdfplumber.open(str(path)) as pdf:
            return [(p.extract_text() or "") for p in pdf.pages]
    # pdftotext -layout: page break sebagai \f (form feed)
    result = subprocess.run(
        ["pdftotext", "-layout", str(path), "-"],
        capture_output=True, text=True, timeout=120,
        encoding="utf-8", errors="replace",
    )
    full = result.stdout or ""
    # Split per halaman by form feed
    pages = full.split("\f")
    # pdftotext biasanya append empty page di akhir — drop kalau kosong
    if pages and not pages[-1].strip():
        pages.pop()
    return pages


def _extract_pages(pdf_path: Path) -> list[str]:
    """Return list of page texts (delegate ke pdftotext)."""
    return _pdftotext_pages(pdf_path)


def _find_page_with(pages: list[str], pattern: str, flags=re.I) -> tuple[int, str] | None:
    """Return (page_idx, match_text) of first page containing pattern."""
    for i, t in enumerate(pages):
        m = re.search(pattern, t, flags)
        if m:
            return i, m.group(0)
    return None


# ------------- section parsers -------------

def parse_identitas(pages: list[str]) -> dict:
    """Parse page 2-ish: Kementerian, Program, Kegiatan, KRO, RO, Volume, Satuan, dll."""
    # gabung 3 halaman awal — field identitas biasanya di halaman 2
    head = "\n".join(pages[:3])

    # v0.2: RO regex harus NOT match "Klasifikasi Rincian Output" dan "Indikator Rincian Output".
    # Gunakan (?:^|\n) untuk memastikan awal baris, BUKAN kelanjutan kata lain.
    fields_patterns = {
        "kementerian": r"Kementerian\s+Negara\s*/\s*Lembaga\s*:\s*(.+?)(?=\n[A-Z])",
        "unit_eselon_i": r"Unit\s+Eselon\s+I\s*:\s*(.+?)(?=\n[A-Z])",
        "program_nama": r"(?:^|\n)Program\s*:\s*(.+?)(?=\n[A-Z])",
        "sasaran_program": r"Sasaran\s+Program\s*:\s*(.+?)(?=\n[A-Z])",
        "ikp": r"Indikator\s+Kinerja\s+Program\s*:\s*(.+?)(?=\n[A-Z])",
        "kegiatan_nama": r"(?:^|\n)Kegiatan\s*:\s*(.+?)(?=\n[A-Z])",
        "sasaran_kegiatan": r"Sasaran\s+Kegiatan\s*:\s*(.+?)(?=\n[A-Z])",
        "ikk": r"Indikator\s+Kinerja\s+Kegiatan\s*:\s*(.+?)(?=\n[A-Z])",
        "kro": r"Klasifikasi\s+Rincian\s+Output\s*:\s*(.+?)(?=\n[A-Z])",
        # v0.2: RO harus sebagai standalone heading, bukan bagian dari "Klasifikasi/Indikator"
        "ro": r"(?:^|\n)Rincian\s+Output\s*:\s*(.+?)(?=\n[A-Z])",
        "iro_header": r"Indikator\s+RO\s*:\s*(.+?)(?=\n[A-Z])",
        "volume": r"Volume\s+RO\s*:\s*(.+?)(?=\n[A-Z])",
        "satuan": r"Satuan\s+Ukur\s+Keluaran\s*:\s*(.+?)(?=\n[A-Z])",
    }

    out = {}
    for key, pat in fields_patterns.items():
        m = re.search(pat, head, re.M | re.DOTALL)
        if m:
            out[key] = _clean_ws(m.group(1))
        else:
            out[key] = None

    # program kode (mis. 059.GK) — dari cover page
    cover = pages[0] if pages else ""
    km = re.search(r"Program\s+(\d{3}\.[A-Z]{2})", cover)
    out["program_kode"] = km.group(1) if km else None
    km = re.search(r"Kegiatan\s+(\d{4})", cover)
    out["kegiatan_kode"] = km.group(1) if km else None
    km = re.search(r"(QDC|QDB|QDA|QMA|QMB|RBA|RBB|RCL)\s", cover)
    out["kro_kode"] = km.group(1) if km else None

    # parse volume as int
    if out.get("volume"):
        vm = re.search(r"(\d+)", out["volume"])
        if vm:
            out["volume_int"] = int(vm.group(1))

    return out


def parse_penandaan(pages: list[str]) -> dict:
    """Parse cluster penandaan dari halaman 2 TOR.
    Cluster 1 (Prioritas Presiden): MBG, Koperasi Merah Putih, Swasembada Pangan, dsb.
    Cluster 2 (di luar Prioritas Presiden): RPJMN PN, Direktif Menteri, dsb.
    Cluster 3: di luar cluster 1 dan 2.

    v0.2: Heuristik — karena pdfplumber sering gagal bedakan ☑ vs ◻, kita flag
    indeterminate jika tidak ada sinyal kuat. Sinyal kuat untuk "ditandai":
      - karakter (cid:X), ✓, ●, ■, ◼ persis sebelum teks item, DAN
      - tidak ada ◻/☐ tepat di depan item itu.
    Jika semua item Cluster 1 diawali ◻ → Cluster 1 tidak ditandai (likely).
    Field tambahan: `indeterminate` flag supaya rule C.1 bisa skip jika ragu.
    """
    head = "\n".join(pages[:3])
    out = {"cluster_1": [], "cluster_2": [], "cluster_3": False,
           "indeterminate": False, "raw_snippet": ""}

    # region cluster 1
    m = re.search(r"Cluster\s*1(.+?)Cluster\s*2", head, re.S | re.I)
    if m:
        seg = m.group(1)
        # items: sekumpulan string setelah karakter checkbox
        # baris yang DITANDAI biasanya tidak punya ◻ di depan (atau ada ✓)
        # heuristik: cari line yang ada kata "pangan", "MBG", dll. dan tidak diawali ◻
        known_pn = [
            "MBG", "Koperasi Merah Putih", "Sekolah Rakyat", "Digitalisasi Bansos",
            "Swasembada Pangan", "Digitalisasi Pendidikan", "Cek Kesehatan Gratis",
            "30 Juta Rumah",
        ]
        for kw in known_pn:
            # find context: ada 20 char sebelum keyword
            km = re.search(r"(.{0,5})" + re.escape(kw), seg)
            if km:
                prefix = km.group(1)
                # ditandai kalau prefix TIDAK berisi karakter empty box ◻
                has_empty = "◻" in prefix or "☐" in prefix
                if not has_empty and kw.lower() in seg.lower():
                    # masih rawan false positive; tambah patokan ada (cid:X) atau ✓ atau ● atau ■
                    if re.search(r"(cid:\d+|✓|●|■|◼)", prefix) or prefix.strip() == "":
                        out["cluster_1"].append(kw)

    # region cluster 2
    m = re.search(r"Cluster\s*2(.+?)Cluster\s*3", head, re.S | re.I)
    if m:
        seg = m.group(1)
        # cari RPJMN PN XX
        pn_match = re.search(r"RPJMN\s*:\s*PN\s*(\d+)", seg)
        if pn_match:
            # cek marker ditandai
            ctx = seg[max(0, pn_match.start() - 20):pn_match.start()]
            if "◻" not in ctx and "☐" not in ctx:
                out["cluster_2"].append(f"RPJMN PN {pn_match.group(1)}")
        # Direktif/Layanan/Manajemen
        for kw in ["Direktif Menteri", "Layanan Publik", "Manajemen dan Operasional"]:
            km = re.search(r"(.{0,10})" + re.escape(kw), seg)
            if km and "◻" not in km.group(1) and "☐" not in km.group(1):
                if re.search(r"(cid:\d+|✓|●|■|◼)", km.group(1)):
                    out["cluster_2"].append(kw)

    # region cluster 3
    m = re.search(r"Cluster\s*3.{0,20}?di\s*luar\s*cluster", head, re.S | re.I)
    if m:
        ctx = head[max(0, m.start() - 20):m.start()]
        out["cluster_3"] = bool(re.search(r"(cid:\d+|✓|●|■|◼)", ctx))

    out["raw_snippet"] = head[:1500]
    return out


def parse_dasar_hukum(pages: list[str]) -> list[dict]:
    """Parse bagian A.1 Dasar Hukum."""
    text = "\n".join(pages)
    m = re.search(r"A\.\s*LATAR\s+BELAKANG.*?1\.\s*Dasar\s+Hukum(.+?)2\.\s*Gambaran\s+Umum",
                  text, re.S | re.I)
    if not m:
        return []
    seg = m.group(1)
    out = []
    # items dimulai dengan huruf a–z + titik
    items = re.findall(r"(?:^|\n)\s*([a-z])\.\s*(.+?)(?=(?:\n\s*[a-z]\.|$))", seg, re.S)
    for letter, body in items:
        body = _clean_ws(body)
        # deteksi pasal/ayat spesifik
        has_pasal = bool(re.search(r"pasal\s+\d+", body, re.I))
        has_ayat = bool(re.search(r"ayat\s+\(?\d+", body, re.I))
        # v0.2: deteksi jenis regulasi lebih fleksibel — handle variasi "No.", "Nomor", "Nomer"
        reg_pattern = (
            r"(Undang[-\s]?Undang\s+RI|Undang[-\s]?Undang|UU(?:\s+RI)?|PP|"
            r"Peraturan\s+Presiden(?:\s+RI)?|Perpres|"
            r"Peraturan\s+Menteri\s+Keuangan|PMK|"
            r"Peraturan\s+Menteri\s+Komdigi|"
            r"Peraturan\s+Menteri(?:\s+\w+)*|Permen[\w]*|"
            r"Keputusan\s+Presiden(?:\s+RI)?|Keppres|"
            r"Kepmen[\w]*|"
            r"Peraturan\s+Lembaga|Perlem)"
            r"\s*"
            r"(?:No\.|Nomor|Nomer)?\s*(\d+)\s*Tahun\s*(\d{4})"
        )
        reg = re.search(reg_pattern, body, re.I)
        # normalisasi jenis regulasi
        jenis = None
        if reg:
            raw_jenis = reg.group(1).lower()
            if "undang" in raw_jenis or raw_jenis.startswith("uu"):
                jenis = "UU"
            elif "perpres" in raw_jenis or "peraturan presiden" in raw_jenis:
                jenis = "Perpres"
            elif "pmk" in raw_jenis or "keuangan" in raw_jenis:
                jenis = "PMK"
            elif "komdigi" in raw_jenis:
                jenis = "Permenkomdigi"
            elif "permen" in raw_jenis or "peraturan menteri" in raw_jenis:
                jenis = "Permen"
            elif "keppres" in raw_jenis or "keputusan presiden" in raw_jenis:
                jenis = "Keppres"
            elif "kepmen" in raw_jenis:
                jenis = "Kepmen"
            elif raw_jenis == "pp" or "peraturan pemerintah" in raw_jenis:
                jenis = "PP"
            elif "perlem" in raw_jenis:
                jenis = "Perlem"
        out.append({
            "butir": letter,
            "teks": body,
            "jenis_regulasi": jenis,
            "nomor": reg.group(2) if reg else None,
            "tahun": reg.group(3) if reg else None,
            "memuat_pasal_ayat": has_pasal or has_ayat,
        })
    return out


def parse_penerima_manfaat(pages: list[str]) -> list[dict]:
    """Parse bagian C Penerima Manfaat (tabel)."""
    text = "\n".join(pages)
    m = re.search(r"C\.\s*PENERIMA\s+MANFAAT(.+?)(?=D\.|E\.|\Z)", text, re.S | re.I)
    if not m:
        return []
    seg = m.group(1)
    # format tabel: No. | Penerima | Manfaat | Peran — tiap baris diawali digit
    rows = re.findall(r"\n\s*(\d+)\s+(.+?)(?=\n\s*\d+\s+|\Z)", seg, re.S)
    out = []
    for no, body in rows:
        body_clean = _clean_ws(body)
        # ambil 60 char pertama sebagai label
        label = body_clean[:100].split(".")[0] if body_clean else ""
        out.append({
            "no": int(no),
            "ringkasan": body_clean[:300],
        })
    return out


def parse_kpi(pages: list[str]) -> dict:
    """Parse bagian D (KPI / Indikator) — IKP, IKK, IRO.

    v0.2: Simpler detection — heading "D. KEY PERFORMANCE INDIKATOR (KPI)" bisa
    berbentuk tabular sehingga parsing narasi seringkali gagal. Daripada extract
    isi penuh, kita deteksi presence + kelengkapan (formula operasional, kriteria).
    """
    text = "\n".join(pages)
    m = re.search(r"D\.\s*KEY\s+PERFORMANCE\s+INDIKATOR(.*?)(?=E\.\s*KURUN|E\.\s*BIAYA|\Z)",
                  text, re.S | re.I)
    if not m:
        return {"ikp_program": None, "ikk_kegiatan": None, "iro_bagian_d": None,
                "section_found": False}
    seg = m.group(1)

    # v0.2.1: Pakai keyword matching yang robust thd layout tabular.
    # Heading "Indikator Kinerja Program" dan "(Eselon I)" sering terpisah di
    # kolom PDF — kita cek keberadaan masing-masing di segment.

    # IKP Program (Eselon I)
    ikp = None
    has_eselon_i = bool(re.search(r"\(Eselon\s*I\)", seg, re.I))
    has_ikp_name = bool(re.search(r"Persentase\s+Tingkat\s+[A-Za-z]+\s+Adopsi", seg))
    if has_eselon_i or has_ikp_name:
        # deteksi formula variabel abstrak TA = (W X), W_1 X_1, W X
        has_formula_abstract = bool(re.search(r"[A-Z]{1,2}\s*=\s*\(\s*[Ww]\s*[Xx]\s*\)", seg)) or bool(
            re.search(r"[Ww]\s*\d+\s*[Xx]?\s*\d*", seg))
        # bobot operasional: "W1 = 0.3" atau "Bobot: 30%"
        has_bobot_value = bool(re.search(r"[Ww]\d*\s*=\s*\d+[\.,]\d+", seg)) or bool(
            re.search(r"[Bb]obot\s*[:=]\s*\d+[\.,]\d+", seg))
        # Target 10% untuk IKP
        tm = re.search(r"Produktivitas\s+Adopsi\s+Teknologi\s+Baru.{0,300}?(\d+[,.]?\d*)\s*%",
                       seg, re.S | re.I)
        ikp = {
            "nama": "Persentase Tingkat Produktivitas Adopsi Teknologi Baru",
            "ada_formula": has_formula_abstract,
            "formula_operasional": has_bobot_value,
            "target": (tm.group(1) + "%") if tm else None,
        }

    # IKK Kegiatan (Eselon II)
    ikk = None
    has_eselon_ii = bool(re.search(r"\(Eselon\s*II\)", seg, re.I))
    has_ikk_name = bool(re.search(r"pertumbuhan\s+adopsi\s+usecase\s+teknologi\s+digital", seg, re.I))
    if has_eselon_ii or has_ikk_name:
        # formula P = A/(A+B) × 100%  — cek bentuk tidak konvensional
        has_formula = bool(re.search(r"P\s*=", seg)) or bool(re.search(r"A\s*/?\s*\(\s*A\s*\+\s*B\s*\)", seg))
        uses_total_denominator = bool(re.search(r"A\s*/?\s*\(\s*A\s*\+\s*B\s*\)", seg)) or bool(
            re.search(r"A\s*\+\s*B", seg))  # fallback: ada 'A+B' = non-konvensional
        ikk = {
            "nama": "Persentase pertumbuhan adopsi usecase teknologi digital",
            "ada_formula": has_formula,
            "formula_konvensional": not uses_total_denominator,
        }
        tm = re.search(r"0[\.,]5\s*%", seg)
        if tm:
            ikk["target"] = tm.group(0)

    # IRO bagian D
    iro = None
    iro_match = re.search(r"Indikator\s+Rincian\s+Output\s*\(IRO\)\s*:\s*(.+?)(?=\n[A-Z]\.|E\.|\Z)",
                          seg, re.S | re.I)
    if iro_match:
        body = _clean_ws(iro_match.group(1))
        kriteria = re.findall(r"\d+\.\s*([^\n.]+?)(?:\s+\d+\.|\s+\d+\s*Orang|\Z)", body, re.S)
        tm = re.search(r"(\d+)\s*Orang", body, re.I)
        iro = {
            "nama": body[:250],
            "kriteria": [_clean_ws(k)[:150] for k in kriteria[:5]],
            "jumlah_kriteria": len(kriteria),
            "target": int(tm.group(1)) if tm else None,
        }

    return {"ikp_program": ikp, "ikk_kegiatan": ikk, "iro_bagian_d": iro,
            "section_found": True}


def parse_lokasi(pages: list[str]) -> dict:
    """Parse bagian B Lokasi — daftar kabupaten target."""
    text = "\n".join(pages)
    m = re.search(r"B\.\s*Lokasi(.+?)(?=C\.|Alasan\s+pemilihan|\Z)", text, re.S | re.I)
    out = {"lokasi_target": [], "mentions_lokasi_non_target": []}
    if m:
        seg = m.group(1)
        # cari "Kab. XXX (Provinsi)" pattern
        for km in re.finditer(r"Kab(?:upaten)?\.?\s+([A-Z][a-zA-Z\s]+?)(?:\s*\(|,)", seg):
            name = _clean_ws(km.group(1))
            if name not in out["lokasi_target"] and len(name) < 30:
                out["lokasi_target"].append(name)

    # cari lokasi lain yang disebut di TOR (di luar bagian B)
    other_text = text
    all_kabs = set(re.findall(r"Kab(?:upaten)?\.?\s+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)?)", other_text))
    target_set = set(out["lokasi_target"])
    for k in all_kabs:
        kn = _clean_ws(k)
        if kn and kn not in target_set and len(kn) < 30:
            out["mentions_lokasi_non_target"].append(kn)
    out["mentions_lokasi_non_target"] = list(set(out["mentions_lokasi_non_target"]))[:20]
    return out


def parse_biaya(pages: list[str]) -> dict:
    """Parse bagian F (atau E) BIAYA YANG DIPERLUKAN."""
    text = "\n".join(pages)
    m = re.search(r"F\.\s*BIAYA.{0,200}?sebesar\s+Rp\s*([\d\.,]+)", text, re.S | re.I)
    if not m:
        m = re.search(r"Anggaran.{0,200}?sebesar\s+Rp\s*([\d\.,]+)", text, re.S | re.I)
    out = {"total": None, "sumber_dana": None}
    if m:
        out["total"] = _rupiah_to_int("Rp" + m.group(1))
    sm = re.search(r"DIPA\s+([^\s]+(?:\s+[A-Z][a-z]+)*)", text)
    if sm:
        out["sumber_dana"] = _clean_ws(sm.group(0))
    return out


def parse_cba(pages: list[str]) -> dict:
    """Parse bagian G CBA — BCR, skor per aspek, skor total."""
    text = "\n".join(pages)
    m = re.search(r"G\.\s*BENEFIT\s+ANALYSIS(.+?)(?=H\.|\Z)", text, re.S | re.I)
    if not m:
        return {}
    seg = m.group(1)
    out = {}
    # BCR
    bcr = re.search(r"BCR\s*\)?\s*=\s*([\d\.,]+)\s*[÷/:]\s*([\d\.,]+)\s*[≈=]\s*([\d\.,]+)", seg)
    if bcr:
        out["bcr_numerator"] = _rupiah_to_int(bcr.group(1))
        out["bcr_denominator"] = _rupiah_to_int(bcr.group(2))
        out["bcr_ratio"] = float(bcr.group(3).replace(",", "."))
    # Skor per aspek
    aspek_scores = {}
    for asp in ["Ekonomi", "Sosial", "Kelembagaan", "Lingkungan"]:
        sm = re.search(rf"Aspek\s+{asp}[^=]*=\s*([\d,\.]+)", seg)
        if sm:
            aspek_scores[asp.lower()] = float(sm.group(1).replace(",", "."))
    out["skor_aspek"] = aspek_scores
    total_m = re.search(r"Skor\s+Total\s*=\s*([\d,\.]+)\s*=\s*(Sangat\s+Layak|Layak|Kurang\s+Layak|Tidak\s+Layak)",
                        seg, re.I)
    if total_m:
        out["skor_total"] = float(total_m.group(1).replace(",", "."))
        out["interpretasi"] = total_m.group(2)
    return out


def parse_manajemen_risiko(pages: list[str]) -> dict:
    """Parse bagian H Manajemen Risiko — cek kelengkapan matriks."""
    text = "\n".join(pages)
    m = re.search(r"H\.\s*MANAJEMEN\s+R[EI]S[I]?KO(.+?)\Z", text, re.S | re.I)
    out = {
        "ada_matriks": False,
        "memuat_residual": False,
        "memuat_strategis_operasional": False,
        "memuat_led_tahun_sebelumnya": False,
        "memuat_keselarasan_aplikasi_mr": False,
        "jumlah_risiko_eselon_i": 0,
        "jumlah_risiko_eselon_ii": 0,
    }
    if not m:
        return out
    seg = m.group(1)
    out["ada_matriks"] = bool(re.search(r"Pernyataan\s+Risiko", seg, re.I))
    out["memuat_residual"] = bool(re.search(r"residual", seg, re.I))
    out["memuat_strategis_operasional"] = (
        bool(re.search(r"risiko\s+strategis", seg, re.I))
        and bool(re.search(r"risiko\s+operasional", seg, re.I))
    )
    out["memuat_led_tahun_sebelumnya"] = bool(re.search(r"Loss\s+Event\s+Database|LED", seg, re.I))
    out["memuat_keselarasan_aplikasi_mr"] = bool(re.search(r"aplikasi\s+(?:manajemen\s+)?r[ei]s[i]?ko", seg, re.I))

    # count baris: baris yang diawali kata kerja risiko di tabel
    es1 = re.search(r"Eselon\s+I(.+?)Eselon\s+II", seg, re.S | re.I)
    if es1:
        out["jumlah_risiko_eselon_i"] = len(re.findall(r"(?:Kurang|Tidak|Kegagalan|Keterlambatan|Koordinasi|Perencanaan|Ketersediaan|Ketidak)", es1.group(1)))
    es2 = re.search(r"Eselon\s+II(.+?)\Z", seg, re.S | re.I)
    if es2:
        out["jumlah_risiko_eselon_ii"] = len(re.findall(r"(?:Kurang|Tidak|Kegagalan|Keterlambatan|Koordinasi|Perencanaan|Ketersediaan|Ketidak)", es2.group(1)))
    return out


def parse_asta_cita(pages: list[str]) -> dict:
    """Parse narasi Asta Cita di TOR — berapa banyak yang disebut."""
    text = "\n".join(pages)
    # pola "Asta Cita 2, 5, dan 6" atau "Asta cita 2:"
    nums = set()
    for m in re.finditer(r"Asta\s*[Cc]ita\s*[:\-]?\s*(\d+[,\s\d]*)", text):
        for n in re.findall(r"\d+", m.group(1)):
            nums.add(int(n))
    return {"asta_cita_disebut": sorted(nums), "jumlah": len(nums)}


def parse_timeline_narasi(pages: list[str]) -> dict:
    """Deteksi narasi 'perikanan' atau sektor lain di TOR sektor pertanian."""
    text = "\n".join(pages)
    out = {"sector_keyword_leaks": []}
    # jika RO tentang "pertanian", cek apakah ada kata "perikanan" dll.
    ro_m = re.search(r"Rincian\s+Output\s*:\s*Pemanfaatan\s+Teknologi\s+Digital\s+di\s+Sektor\s+(\w+)",
                     "\n".join(pages[:3]), re.I)
    if ro_m:
        ro_sector = ro_m.group(1).lower()
        other_sectors = {"pertanian", "perikanan", "peternakan", "energi", "logistik", "pendidikan",
                         "kesehatan", "pariwisata", "maritim"}
        for other in other_sectors - {ro_sector}:
            count = len(re.findall(rf"\b{other}\b", text, re.I))
            if count > 0:
                # cek konteks — skip jika dalam daftar "6 sektor strategis"
                # simple heuristic: count > 2 = suspicious
                if count >= 2:
                    # ambil 3 sample lokasi
                    samples = []
                    for mm in re.finditer(rf"\b{other}\b", text, re.I):
                        start = max(0, mm.start() - 50)
                        end = min(len(text), mm.end() + 80)
                        samples.append(text[start:end].replace("\n", " "))
                    out["sector_keyword_leaks"].append({
                        "keyword": other,
                        "count": count,
                        "samples": samples[:3],
                    })
    return out


def parse_tenaga_ahli(pages: list[str]) -> dict:
    """Cek apakah TOR menyebut Tenaga Ahli."""
    text = "\n".join(pages)
    out = {"disebut": False, "jumlah": 0, "nama_posisi": []}
    m = re.search(r"Tabel\s+Tenaga\s+Ahli(.+?)(?=Kegiatan\s+ini|c\)\s*Monitoring|\Z)",
                  text, re.S | re.I)
    if m:
        seg = m.group(1)
        out["disebut"] = True
        positions = re.findall(r"Tenaga\s+Ahli\s+Bidang\s+([A-Z][a-zA-Z\s]+?)\s+\d", seg)
        out["nama_posisi"] = [_clean_ws(p) for p in positions]
        out["jumlah"] = len(positions)
    return out


def parse_baseline(pages: list[str]) -> dict:
    """Extract capaian/baseline tahun sebelumnya dari narasi TOR."""
    text = "\n".join(pages)
    out = {
        "narasi_mention_jumlah_kelompok": [],
        "tabel_baseline_rows": 0,
    }
    # cari pola "16 Kelompok Tani", "5 kelompok tani sebagai pilot"
    for m in re.finditer(r"(\d+)\s+[Kk]elompok\s+[Tt]ani", text):
        out["narasi_mention_jumlah_kelompok"].append(int(m.group(1)))
    # cari tabel baseline dengan numbering
    tab_seg = re.search(r"Kelompok\s+Tani\s+yang\s+telah\s+dilakukan\s+pemasangan(.+?)(?=Tahun\s+\d{4}\s+dilakukan|b\.\s*Deskripsi)",
                        text, re.S | re.I)
    if tab_seg:
        numbers = re.findall(r"^\s*(\d+)\s+KT\.?|\s+(\d+)\s+Gapoktan|^\s*(\d+)\s+KUB|^\s*(\d+)\s+Bumdes",
                             tab_seg.group(1), re.M)
        # count baris berdasarkan pola nomor + nama
        rows = re.findall(r"\n\s*(\d+)\s+(KT\.|Gapoktan|KUB|Bumdes)", tab_seg.group(1))
        out["tabel_baseline_rows"] = len(rows)
    return out


# ------------- main digest -------------

def digest_tor(pdf_path: str | Path) -> dict:
    """Return structured JSON representation of TOR."""
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(pdf_path)

    pages = _extract_pages(pdf_path)

    return {
        "metadata": {
            "source_file": str(pdf_path.name),
            "jenis_dokumen": "TOR",
            "total_pages": len(pages),
        },
        "identitas_ro": parse_identitas(pages),
        "penandaan_cluster": parse_penandaan(pages),
        "dasar_hukum": parse_dasar_hukum(pages),
        "penerima_manfaat": parse_penerima_manfaat(pages),
        "kpi": parse_kpi(pages),
        "lokasi": parse_lokasi(pages),
        "biaya": parse_biaya(pages),
        "cba": parse_cba(pages),
        "manajemen_risiko": parse_manajemen_risiko(pages),
        "asta_cita": parse_asta_cita(pages),
        "timeline_narasi": parse_timeline_narasi(pages),
        "tenaga_ahli": parse_tenaga_ahli(pages),
        "baseline": parse_baseline(pages),
        # raw_text disimpan untuk fallback Claude
        "raw_text_pages": pages,
    }


def _self_check_ast() -> None:
    """Preflight: pastikan script ini sendiri syntactically valid sebelum run.
    Mencegah eksekusi dengan file korup (mis. akibat OneDrive sync artifact)."""
    import ast
    try:
        ast.parse(open(__file__, "r", encoding="utf-8").read())
    except SyntaxError as e:
        print(f"Self-check AST gagal di {__file__}: {e}", file=sys.stderr)
        print("   File mungkin korup. Lihat backup atau git restore.", file=sys.stderr)
        sys.exit(2)


def main(argv=None):
    _self_check_ast()
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("pdf", help="Path ke file TOR (PDF)")
    parser.add_argument("-o", "--output", default=None, help="Path output JSON (default: <input>.tor.json)")
    parser.add_argument("--no-raw", action="store_true", help="Jangan sertakan raw_text_pages (hemat storage)")
    args = parser.parse_args(argv)

    out = digest_tor(args.pdf)
    if args.no_raw:
        out.pop("raw_text_pages", None)

    out_path = args.output or str(Path(args.pdf).with_suffix(".tor.json"))
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)

    print(f"OK — written: {out_path}")
    print(f"   RO: {out['identitas_ro'].get('ro')}")
    print(f"   Volume: {out['identitas_ro'].get('volume')}  Satuan: {out['identitas_ro'].get('satuan')}")
    print(f"   Biaya: {out['biaya'].get('total')}")
    print(f"   Lokasi target: {out['lokasi'].get('lokasi_target')}")
    print(f"   Dasar hukum: {len(out['dasar_hukum'])} butir — {sum(1 for d in out['dasar_hukum'] if d['memuat_pasal_ayat'])} menyebut pasal/ayat")
    return 0


if __name__ == "__main__":
    sys.exit(main())
