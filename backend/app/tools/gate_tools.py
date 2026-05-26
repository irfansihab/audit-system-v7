"""Tools gate — eksekusi evaluasi BERTAHAP (gate-based, human-in-the-loop).

Skill evaluasi tertentu (SPIP/SAKIP/RB) dijalankan gate demi gate. Tiap gate:
agen kerjakan SATU gate lalu BERHENTI; auditor memutuskan LANJUT / KOREKSI /
ULANG. Progress disimpan di `penilaian-progress.json` di folder penugasan supaya
bisa di-resume bila sesi terputus.

State machine per gate:
  PENDING → (dikerjakan) → DONE        [LANJUT]   → current pindah ke gate berikut
                         → NEEDS_REVISION [KOREKSI] → current tetap (auditor minta perbaikan)
                         → PENDING        [ULANG]   → current tetap (kerjakan ulang dari awal)
"""
import json
from datetime import datetime
from pathlib import Path

from claude_agent_sdk import tool

from app import gate_registry as greg

PROGRESS_FILE = "penilaian-progress.json"
_DECISIONS = {"LANJUT", "KOREKSI", "ULANG"}


def _progress_path(folder: Path) -> Path:
    return folder / PROGRESS_FILE


def read_progress(folder: Path) -> dict | None:
    p = _progress_path(folder)
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def _write_progress(folder: Path, data: dict) -> None:
    data["updated_at"] = datetime.utcnow().isoformat() + "Z"
    _progress_path(folder).write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def init_progress(folder: Path, skill: str) -> dict:
    """Buat penilaian-progress.json dari daftar gate skill. Idempotent — bila
    sudah ada, kembalikan yang ada (jangan reset progres auditor)."""
    existing = read_progress(folder)
    if existing:
        return existing
    gates = greg.list_gates(skill)
    state = {
        "skill": str(skill).strip().lower(),
        "total_gates": len(gates),
        "current_gate": gates[0]["id"] if gates else None,
        "gates": [
            {"id": g["id"], "judul": g["judul"], "status": "PENDING", "catatan": ""}
            for g in gates
        ],
    }
    folder.mkdir(parents=True, exist_ok=True)
    _write_progress(folder, state)
    return state


def record_result(folder: Path, gate_id: str, decision: str, catatan: str = "") -> dict:
    """Terapkan keputusan auditor atas satu gate. Return state terbaru atau
    {'error': ...}."""
    state = read_progress(folder)
    if not state:
        return {"error": "progress belum diinisialisasi (init_gate_progress dulu)"}
    decision = str(decision).strip().upper()
    if decision not in _DECISIONS:
        return {"error": f"decision tidak valid: {decision} (LANJUT/KOREKSI/ULANG)"}
    gid = str(gate_id).strip()
    gates = state.get("gates", [])
    idx = next((i for i, g in enumerate(gates) if g["id"].upper() == gid.upper()), None)
    if idx is None:
        return {"error": f"gate_id tidak ditemukan: {gid}"}

    if decision == "LANJUT":
        gates[idx]["status"] = "DONE"
        gates[idx]["catatan"] = catatan
        # current pindah ke gate PENDING/NEEDS_REVISION berikutnya
        nxt = next((g["id"] for g in gates[idx + 1:] if g["status"] != "DONE"), None)
        state["current_gate"] = nxt  # None = semua gate selesai
    elif decision == "KOREKSI":
        gates[idx]["status"] = "NEEDS_REVISION"
        gates[idx]["catatan"] = catatan
        state["current_gate"] = gates[idx]["id"]
    else:  # ULANG
        gates[idx]["status"] = "PENDING"
        gates[idx]["catatan"] = catatan
        state["current_gate"] = gates[idx]["id"]

    _write_progress(folder, state)
    return state


# =============================================================================
# MCP tools (dipakai agen Anggota Tim saat MODE:GATE)
# =============================================================================


@tool(
    "read_gate_progress",
    "Baca status eksekusi bertahap (penilaian-progress.json): skill, total_gates, "
    "current_gate, dan status tiap gate (PENDING/IN_PROGRESS/DONE/NEEDS_REVISION). "
    "Pakai di awal MODE:GATE untuk tahu gate mana yang harus dikerjakan.",
    {"penugasan_folder": str},
)
async def read_gate_progress(args: dict) -> dict:
    folder = Path(args["penugasan_folder"])
    state = read_progress(folder)
    if state is None:
        return {"content": [{"type": "text", "text": "BELUM_INIT|panggil init_gate_progress(penugasan_folder, skill)"}]}
    return {"content": [{"type": "text", "text": json.dumps(state, ensure_ascii=False)}]}


@tool(
    "init_gate_progress",
    "Inisialisasi penilaian-progress.json dari daftar gate skill evaluasi bertahap "
    "(SPIP/SAKIP/RB). Idempotent — tidak mereset bila sudah ada. Panggil sekali di gate 0.",
    {"penugasan_folder": str, "skill": str},
)
async def init_gate_progress(args: dict) -> dict:
    folder = Path(args["penugasan_folder"])
    skill = str(args.get("skill", "")).strip()
    if not greg.skill_has_gates(skill):
        return {
            "content": [{
                "type": "text",
                "text": f"BUKAN_BERTAHAP|skill='{skill}' tidak punya alur bertahap. Skill bertahap: {', '.join(greg.gated_skills())}",
            }],
            "is_error": True,
        }
    state = init_progress(folder, skill)
    return {"content": [{"type": "text", "text": json.dumps(state, ensure_ascii=False)}]}


@tool(
    "read_gate_instructions",
    "Baca instruksi LENGKAP satu gate (teks markdown dari file *-bertahap.md). "
    "Pakai SETELAH read_gate_progress untuk tahu apa yang dikerjakan di gate ini. "
    "`gate_id` mis. '0','1','4A'.",
    {"skill": str, "gate_id": str},
)
async def read_gate_instructions(args: dict) -> dict:
    skill = str(args.get("skill", "")).strip()
    gate_id = str(args.get("gate_id", "")).strip()
    section = greg.gate_section(skill, gate_id)
    if section is None:
        return {
            "content": [{
                "type": "text",
                "text": f"NOT_FOUND|gate '{gate_id}' untuk skill '{skill}'. Gate tersedia: {', '.join(greg.gate_ids(skill)) or '(skill bukan bertahap)'}",
            }],
            "is_error": True,
        }
    return {"content": [{"type": "text", "text": section[:9000]}]}


@tool(
    "record_gate_result",
    "Catat hasil & keputusan SATU gate ke penilaian-progress.json. `decision`: "
    "'LANJUT' (gate selesai → maju ke gate berikut), 'KOREKSI' (perlu revisi → tetap), "
    "'ULANG' (kerjakan ulang → tetap). `catatan` ringkas hasil/temuan gate. "
    "Panggil di AKHIR pengerjaan gate, lalu BERHENTI & minta konfirmasi auditor.",
    {"penugasan_folder": str, "gate_id": str, "decision": str, "catatan": str},
)
async def record_gate_result(args: dict) -> dict:
    folder = Path(args["penugasan_folder"])
    res = record_result(
        folder,
        str(args.get("gate_id", "")),
        str(args.get("decision", "")),
        str(args.get("catatan", "")),
    )
    if "error" in res:
        return {"content": [{"type": "text", "text": f"FAILED|{res['error']}"}], "is_error": True}
    nxt = res.get("current_gate")
    tail = f"current_gate={nxt}" if nxt else "SEMUA_GATE_SELESAI"
    return {"content": [{"type": "text", "text": f"OK|{tail}|" + json.dumps(res, ensure_ascii=False)}]}


GATE_TOOLS = [read_gate_progress, init_gate_progress, read_gate_instructions, record_gate_result]
