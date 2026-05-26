#!/usr/bin/env python3
"""Harness ujicoba DIGESTION (pipeline V6 deterministik) untuk BANYAK dokumen.

Menjalankan digest yang sama dgn produksi (digest_tor/digest_rab per-file,
digest_pengadaan folder-level) atas sebuah korpus, secara PARALEL, lalu mengukur
KECEPATAN + KUALITAS hasil otomatis (tanpa baca tiap JSON manual).

Klasifikasi jenis dokumen:
  - dari nama SUBFOLDER bila cocok {tor,rab,kak,hps,rfi,kontrak}; else
  - dari prefiks nama file (classify_doc_by_filename).
ST/KP/PKP/OTHER dilewati (tak punya digest script).

Kualitas:
  - JSON valid + tidak kosong (deteksi PDF scan/gambar → "perlu OCR").
  - Cakupan field kunci per jenis (reuse _summarize_digest).
  - (opsional) --golden golden.json → skor akurasi terhadap nilai harapan.

Pakai (dari root repo, venv aktif):
  PYTHONPATH=backend backend/.venv/bin/python backend/scripts/digestion_harness.py \
      --corpus <folder> [--out <folder>] [--workers 4] [--golden golden.json]

Format golden.json:
  { "NAMA-FILE.pdf": { "label": "nilai harapan (substring, case-insensitive)", ... } }
"""
from __future__ import annotations

import argparse
import asyncio
import json
import shutil
import tempfile
import time
from pathlib import Path

from app.storage import classify_doc_by_filename, target_subfolder_for
from app.tools.kkp_tools import _summarize_digest
from app.tools.v6_bridge import run_v6_script, safe_read_json

_SUBFOLDER_JENIS = {"tor", "rab", "kak", "hps", "rfi", "kontrak"}
_PBJ = {"KAK", "HPS", "RFI", "KONTRAK"}
# Field kunci yang DIHARAPKAN ada per jenis (untuk %cakupan). Mengacu _summarize_digest.
_COVERAGE_KEYS = {
    "TOR": ["kementerian", "program_nama", "kegiatan_nama", "ro", "total_biaya", "dasar_hukum"],
    "RAB": ["kementerian", "ro", "jumlah_komponen", "total_pagu"],
    "PENGADAAN": ["obyek", "nilai_hps", "jangka_waktu"],
}


def classify(path: Path, corpus: Path) -> str:
    parent = path.parent.name.lower()
    if parent in _SUBFOLDER_JENIS:
        return parent.upper()
    return classify_doc_by_filename(path.name)


def coverage(jenis_summary: str, summ: dict) -> tuple[int, int, list[str]]:
    keys = _COVERAGE_KEYS.get(jenis_summary, [])
    present = [k for k in keys if summ.get(k) not in (None, "", [], 0)]
    missing = [k for k in keys if k not in present]
    return len(present), len(keys), missing


def golden_score(out_json: Path, expected: dict) -> tuple[int, int, list[str]]:
    try:
        blob = out_json.read_text(encoding="utf-8").lower()
    except OSError:
        blob = ""
    miss = []
    hit = 0
    for label, val in expected.items():
        if val and str(val).strip().lower() in blob:
            hit += 1
        else:
            miss.append(label)
    return hit, len(expected), miss


async def _digest(sem, script, args, out, timeout=180):
    async with sem:
        t0 = time.perf_counter()
        code, _stdout, err = await run_v6_script(script, args, timeout=timeout)
    return code, (time.perf_counter() - t0), err, out


async def main() -> int:
    ap = argparse.ArgumentParser(description="Harness ujicoba digestion V6")
    ap.add_argument("--corpus", required=True)
    ap.add_argument("--out", default=None, help="folder output (default: <corpus>/_digest-test)")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--golden", default=None)
    args = ap.parse_args()

    corpus = Path(args.corpus).resolve()
    if not corpus.is_dir():
        print(f"FATAL: korpus tidak ada: {corpus}"); return 1
    out_dir = Path(args.out).resolve() if args.out else corpus / "_digest-test"
    out_dir.mkdir(parents=True, exist_ok=True)
    golden = {}
    if args.golden and Path(args.golden).is_file():
        golden = json.loads(Path(args.golden).read_text(encoding="utf-8"))

    pdfs = [p for p in sorted(corpus.rglob("*.pdf")) if "_digest-test" not in p.parts]
    tor, rab, pbj, skipped = [], [], [], []
    for p in pdfs:
        j = classify(p, corpus)
        if j == "TOR": tor.append(p)
        elif j == "RAB": rab.append(p)
        elif j in _PBJ: pbj.append((p, j))
        else: skipped.append((p, j))

    sem = asyncio.Semaphore(max(1, args.workers))
    jobs = []   # (label, jenis_summary, files, coro)

    for i, p in enumerate(tor, 1):
        o = out_dir / f"tor-{i:02d}.json"
        jobs.append((p.name, "TOR", [p],
                     _digest(sem, "scripts/reviu-rka-kl/digest_tor.py", [str(p), "--no-raw", "-o", str(o)], o)))
    for i, p in enumerate(rab, 1):
        o = out_dir / f"rab-{i:02d}.json"
        jobs.append((p.name, "RAB", [p],
                     _digest(sem, "scripts/reviu-rka-kl/digest_rab.py", [str(p), "-o", str(o)], o)))

    # PBJ folder-level: stage ke folder bergaya penugasan (subfolder sesuai target),
    # lalu digest_pengadaan sekali. Satu hasil gabungan utk semua dok PBJ.
    pbj_stage = None
    if pbj:
        pbj_stage = Path(tempfile.mkdtemp(prefix="pbj-stage-"))
        for p, j in pbj:
            sub = pbj_stage / target_subfolder_for(j)
            sub.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, sub / p.name)
        o = out_dir / "pengadaan-digest.json"
        jobs.append(("(" + ", ".join(p.name for p, _ in pbj) + ")", "PENGADAAN", [p for p, _ in pbj],
                     _digest(sem, "scripts/audit-pengadaan/digest_pengadaan.py", [str(pbj_stage), "-o", str(o)], o)))

    print(f"Korpus: {corpus}  | PDF={len(pdfs)} (TOR={len(tor)} RAB={len(rab)} PBJ={len(pbj)} skip={len(skipped)})")
    print(f"Workers={args.workers}  | output={out_dir}\n--- menjalankan digest paralel ---")
    t0 = time.perf_counter()
    results = await asyncio.gather(*(c for *_, c in jobs))
    wall = time.perf_counter() - t0

    rows = []
    for (label, js, files, _), (code, dur, err, out) in zip(jobs, results):
        ok = code == 0 and out.exists()
        data = safe_read_json(out) if ok else {}
        nonempty = bool(data) and bool(json.dumps(data).strip()) and json.dumps(data) != "{}"
        summ = _summarize_digest(out.name, data) if nonempty else {}
        pres, tot, missing = coverage(js, summ)
        gh = gt = None; gmiss = []
        if ok:
            # golden cocokkan per file (untuk PBJ: cocokkan tiap file ke dok gabungan)
            for f in files:
                if f.name in golden:
                    h, t, m = golden_score(out, golden[f.name])
                    gh = (gh or 0) + h; gt = (gt or 0) + t; gmiss += [f"{f.name}:{x}" for x in m]
        rows.append({"label": label, "jenis": js, "ok": ok, "time_s": round(dur, 2),
                     "nonempty": nonempty, "coverage": f"{pres}/{tot}", "missing": missing,
                     "golden": (f"{gh}/{gt}" if gt else None), "golden_miss": gmiss,
                     "error": (err[:200] if not ok else "")})

    # ---- ringkasan konsol ----
    print(f"\n=== RINGKASAN (wall {wall:.2f}s, {len(jobs)} job) ===")
    by = {}
    for r in rows:
        by.setdefault(r["jenis"], []).append(r)
    print(f"{'jenis':11} {'n':>2} {'ok':>3} {'kosong':>6} {'avg s':>6} {'cakupan rata2':>14}")
    for js, rs in by.items():
        nok = sum(1 for r in rs if r["ok"])
        empt = sum(1 for r in rs if r["ok"] and not r["nonempty"])
        avg = sum(r["time_s"] for r in rs) / len(rs)
        cov_pct = []
        for r in rs:
            a, b = r["coverage"].split("/")
            if int(b): cov_pct.append(int(a) / int(b))
        cavg = f"{(sum(cov_pct)/len(cov_pct)*100):.0f}%" if cov_pct else "-"
        print(f"{js:11} {len(rs):>2} {nok:>3} {empt:>6} {avg:>6.2f} {cavg:>14}")

    attention = [r for r in rows if (not r["ok"]) or (not r["nonempty"]) or r["missing"] or r["golden_miss"]]
    if attention:
        print(f"\n=== PERLU PERHATIAN ({len(attention)}) ===")
        for r in attention:
            why = []
            if not r["ok"]: why.append(f"GAGAL: {r['error']}")
            elif not r["nonempty"]: why.append("KOSONG (kemungkinan scan/gambar → OCR)")
            if r["missing"]: why.append(f"field hilang: {','.join(r['missing'])}")
            if r["golden_miss"]: why.append(f"golden meleset: {','.join(r['golden_miss'])}")
            print(f"  [{r['jenis']}] {r['label'][:50]} — {' ; '.join(why)}")
    if skipped:
        print(f"\nDilewati (non-digestible): {[p.name for p, _ in skipped]}")

    # ---- report files ----
    (out_dir / "report.json").write_text(json.dumps(
        {"corpus": str(corpus), "wall_s": round(wall, 2), "rows": rows,
         "skipped": [p.name for p, _ in skipped]}, ensure_ascii=False, indent=2), encoding="utf-8")
    md = [f"# Laporan Ujicoba Digestion", f"Korpus: `{corpus}` · wall {wall:.2f}s · {len(jobs)} job\n",
          "| jenis | dok | ok | kosong | waktu(s) | cakupan | golden |", "|---|---|---|---|---|---|---|"]
    for r in rows:
        md.append(f"| {r['jenis']} | {r['label'][:40]} | {'✓' if r['ok'] else '✗'} | "
                  f"{'kosong' if r['ok'] and not r['nonempty'] else '-'} | {r['time_s']} | {r['coverage']} | {r['golden'] or '-'} |")
    (out_dir / "report.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"\nReport: {out_dir/'report.md'} + report.json")

    if pbj_stage:
        shutil.rmtree(pbj_stage, ignore_errors=True)
    n_fail = sum(1 for r in rows if not r["ok"])
    return 0 if n_fail == 0 else 2


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
