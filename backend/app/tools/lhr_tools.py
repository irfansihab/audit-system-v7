"""Tools untuk Agen Ketua Tim: baca temuan, completeness check, render LHR, QC LHP sync.

Schema rekomendasi.json yang dipakai V6 render_lhp.py:

    {
        "T-001": "Rekomendasi tegas untuk perbaikan...",
        "T-002": "...",
        ...
    }

Note: Function `request_qc_lhp` lama (async-flag) DIGANTI dengan `run_qc_lhp`
sync — sama pola dengan `run_qc_kkp` di kkp_tools.py. Pola lama bermasalah:
agen tidak dapat hasil → improvisasi.
"""
import json
from datetime import datetime
from pathlib import Path

from claude_agent_sdk import tool

from app.tools.v6_bridge import run_v6_script, safe_read_json


@tool(
    "read_temuan_json",
    "Baca _KKP/temuan.json penugasan. Return JSON lengkap dengan envelope penugasan + array temuan.",
    {"penugasan_folder": str},
)
async def read_temuan_json(args: dict) -> dict:
    path = Path(args["penugasan_folder"]) / "_KKP" / "temuan.json"
    if not path.exists():
        return {
            "content": [{"type": "text", "text": "FAILED|temuan.json tidak ada"}],
            "is_error": True,
        }
    data = safe_read_json(path)
    return {"content": [{"type": "text", "text": json.dumps(data, ensure_ascii=False)}]}


@tool(
    "check_completeness",
    "Pastikan semua sasaran di sasaran-assignment.json sudah SELESAI_KKP.",
    {"penugasan_folder": str},
)
async def check_completeness(args: dict) -> dict:
    folder = Path(args["penugasan_folder"])
    assignment = safe_read_json(folder / "_PKP" / "sasaran-assignment.json")
    sasaran_list = assignment.get("sasaran", []) if isinstance(assignment, dict) else []
    belum = [s for s in sasaran_list if s.get("status") != "SELESAI_KKP"]
    if belum:
        text = "BELUM_LENGKAP|sasaran_belum=" + json.dumps(
            [{"id": s.get("sasaran_id"), "assigned_to": s.get("assigned_to")} for s in belum],
            ensure_ascii=False,
        )
        return {"content": [{"type": "text", "text": text}], "is_error": False}
    return {
        "content": [{"type": "text", "text": f"OK|total_sasaran={len(sasaran_list)}|all_selesai_kkp=true"}]
    }


@tool(
    "write_rekomendasi_json",
    "Tulis _LHP/rekomendasi.json — mapping id_temuan ke teks rekomendasi.",
    {"penugasan_folder": str, "rekomendasi": dict},
)
async def write_rekomendasi_json(args: dict) -> dict:
    path = Path(args["penugasan_folder"]) / "_LHP" / "rekomendasi.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(args["rekomendasi"], ensure_ascii=False, indent=2), encoding="utf-8")
    return {"content": [{"type": "text", "text": f"OK|n_rekomendasi={len(args['rekomendasi'])}"}]}


@tool(
    "render_lhr_rka",
    "Render LHR Reviu RKA-K/L via scripts/render_lhp.py V6. Butuh _LHP/rekomendasi.json sudah ada.",
    {
        "penugasan_folder": str,
        "judul": str,
        "auditi": str,
        "dasar_permintaan": str,
        "gambaran_umum": str,
        "tanggal_exit_meeting": str,
    },
)
async def render_lhr_rka(args: dict) -> dict:
    folder = Path(args["penugasan_folder"])
    rekomendasi = folder / "_LHP" / "rekomendasi.json"
    if not rekomendasi.exists():
        return {
            "content": [{"type": "text", "text": "FAILED|rekomendasi.json belum ada"}],
            "is_error": True,
        }
    code, out, err = await run_v6_script(
        "scripts/render_lhp.py",
        [
            "--penugasan", str(folder),
            "--rekomendasi-file", str(rekomendasi),
            "--judul", args["judul"],
            "--auditi", args["auditi"],
            "--dasar-permintaan", args["dasar_permintaan"],
            "--gambaran-umum", args["gambaran_umum"],
            "--tanggal-exit-meeting", args["tanggal_exit_meeting"],
        ],
        timeout=120,
    )
    if code != 0:
        return {
            "content": [{"type": "text", "text": f"FAILED|exit={code}|err={err[:400]}"}],
            "is_error": True,
        }
    return {"content": [{"type": "text", "text": f"OK|{out[:200]}"}]}


@tool(
    "render_lhr_pbj",
    "Render LHR Reviu Pengadaan via scripts/reviu-pengadaan/run_batch.py V6 mode KT. "
    "Script baca context.md dan _LHP/rekomendasi.json dari folder penugasan.",
    {"penugasan_folder": str},
)
async def render_lhr_pbj(args: dict) -> dict:
    """Note: V6 reviu-pengadaan/run_batch.py supports only --penugasan, --input-dir,
    --render, --role. Tidak ada --context (KT baca context.md langsung dari folder).
    --render WAJIB untuk trigger LHR generation (default OFF).
    """
    code, out, err = await run_v6_script(
        "scripts/reviu-pengadaan/run_batch.py",
        [
            "--penugasan", args["penugasan_folder"],
            "--role", "KT",
            "--render",
        ],
        timeout=180,
    )
    if code != 0:
        return {
            "content": [{"type": "text", "text": f"FAILED|exit={code}|err={err[:400]}"}],
            "is_error": True,
        }
    return {"content": [{"type": "text", "text": f"OK|{out[:200]}"}]}


@tool(
    "run_qc_lhp",
    "Jalankan QC SAIPI stage LHP secara SYNCHRONOUS. Memanggil scripts/qc_saipi.py "
    "V6 dengan --stage lhp lalu return status + breakdown severity + excerpt laporan. "
    "Pakai SETELAH render_lhr selesai untuk gate kepatuhan SAIPI tahap pelaporan.",
    {"penugasan_folder": str},
)
async def run_qc_lhp(args: dict) -> dict:
    """Sync version dari QC LHP — ganti pola async marker-flag yang lama
    (`request_qc_lhp` writer flag). Pola lama bermasalah: agen yang memanggilnya
    tidak dapat hasil → improvisasi sendiri.
    """
    folder = Path(args["penugasan_folder"])
    code, out, err = await run_v6_script(
        "scripts/qc_saipi.py",
        ["--penugasan", str(folder), "--stage", "lhp"],
        timeout=120,
    )

    checklist = safe_read_json(folder / "_QA-SAIPI" / "checklist-lhp.json")
    items = checklist.get("items", []) if isinstance(checklist, dict) else []
    total_kritis = sum(1 for i in items if i.get("severity") == "KRITIS" and i.get("status") == "GAP")
    total_peringatan = sum(1 for i in items if i.get("severity") == "PERINGATAN" and i.get("status") == "GAP")
    total_needs_review = sum(1 for i in items if i.get("severity") == "NEEDS_REVIEW")
    total_ok = sum(1 for i in items if i.get("status") == "OK")

    if total_kritis > 0:
        status_label = "BLOCKED_KRITIS"
    elif total_peringatan > 0 or total_needs_review > 0:
        status_label = "PASS_WITH_WARNINGS"
    else:
        status_label = "PASS"

    laporan_path = folder / "_QA-SAIPI" / "laporan-qa-lhp.md"
    laporan_excerpt = ""
    if laporan_path.exists():
        laporan_excerpt = laporan_path.read_text(encoding="utf-8")[:4000]

    return {
        "content": [
            {
                "type": "text",
                "text": (
                    f"stage=lhp|status={status_label}|exit_code={code}|"
                    f"kritis={total_kritis}|peringatan={total_peringatan}|"
                    f"needs_review={total_needs_review}|ok={total_ok}|"
                    f"laporan_path={laporan_path}\n\n"
                    f"=== LAPORAN QA (excerpt) ===\n{laporan_excerpt}"
                ),
            }
        ]
    }


LHR_TOOLS = [
    read_temuan_json,
    check_completeness,
    write_rekomendasi_json,
    render_lhr_rka,
    render_lhr_pbj,
    run_qc_lhp,
]
