"""Feedback aggregate dashboard (Phase 2).

Scan semua file `_FEEDBACK-AGEN/feedback-*.json` cross-penugasan,
aggregate jadi insight: top workflow issues, top substansi issues,
top pattern suggestions, severity heatmap per agent.

Tujuan: PM/PT bisa lihat di satu tempat masalah recurring yang
agen laporkan dari banyak penugasan — bahan input mingguan untuk
hardening prompt + add pattern wiki + fix bug bridge.

Schema feedback file (lihat app/tools/feedback_tools.py):
    {
      schema_version, agent_name, timestamp, overall_confidence,
      summary, workflow_issues[], substansi_issues[], pattern_suggestions[],
      notes_freetext
    }

Endpoint:
    GET /feedback/aggregate?days=30   → ringkasan global
    GET /feedback/list?days=30        → daftar file feedback mentah (untuk drill-down)
"""
from __future__ import annotations

import json
import logging
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user
from app.database import get_db
from app.models import Penugasan, Role, User

log = logging.getLogger(__name__)
router = APIRouter(prefix="/feedback", tags=["feedback"])


# Max file yang diproses untuk satu request — anti-runaway saat folder besar.
MAX_FILES = 500


def _parse_ts(ts: str | None) -> datetime | None:
    """Parse ISO timestamp; tolerate trailing Z / mikrodetik."""
    if not ts:
        return None
    try:
        return datetime.fromisoformat(ts.replace("Z", ""))
    except (ValueError, TypeError):
        return None


def _safe_str(x: Any, max_len: int = 200) -> str:
    return str(x or "").strip()[:max_len]


def _collect_feedback(folders: list[Path], cutoff: datetime | None) -> list[dict]:
    """Walk semua folder penugasan, kumpulkan parsed JSON dari _FEEDBACK-AGEN/."""
    rows: list[dict] = []
    seen = 0
    for folder in folders:
        fb_dir = folder / "_FEEDBACK-AGEN"
        if not fb_dir.exists() or not fb_dir.is_dir():
            continue
        for fpath in sorted(fb_dir.glob("feedback-*.json")):
            if seen >= MAX_FILES:
                log.warning("Feedback aggregate: capped at %s files", MAX_FILES)
                return rows
            seen += 1
            try:
                data = json.loads(fpath.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError) as e:
                log.warning("Skip feedback file %s: %s", fpath, e)
                continue
            ts = _parse_ts(data.get("timestamp"))
            if cutoff and ts and ts < cutoff:
                continue
            data["_file_path"] = str(fpath)
            data["_penugasan_folder"] = str(folder.name)
            data["_mtime"] = datetime.fromtimestamp(fpath.stat().st_mtime).isoformat()
            rows.append(data)
    return rows


@router.get("/aggregate")
async def aggregate_feedback(
    days: int = Query(30, ge=1, le=365, description="Window hari ke belakang"),
    current: tuple[User, Role] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Ringkasan agregat feedback agen cross-penugasan.

    Return:
        {
          "days": 30,
          "total_feedback": int,
          "by_agent": {agent_name: count, ...},
          "by_confidence": {HIGH: x, MEDIUM: y, LOW: z},
          "top_workflow_issues": [{category, severity, count, examples: [...]}],
          "top_substansi_issues": [{category, severity, count, examples: [...]}],
          "top_pattern_suggestions": [{id_proposed, judul, count, rationales: [...]}],
          "severity_heatmap": {agent: {blocker, major, minor}},
          "recent_files": [{path, agent, confidence, ts, penugasan_folder}]
        }
    """
    # Akses ke semua penugasan — feedback aggregate role-agnostic untuk PM/PT/KT
    # supaya bisa surface masalah lintas tim. AT bisa lihat juga, tidak ada PII.
    penugasan_rows = (
        await db.execute(select(Penugasan.folder_path))
    ).scalars().all()
    folders = [Path(p) for p in penugasan_rows if p]

    cutoff = datetime.utcnow() - timedelta(days=days)
    feedback_rows = _collect_feedback(folders, cutoff)

    # by_agent + by_confidence
    by_agent: Counter = Counter()
    by_confidence: Counter = Counter()

    # workflow & substansi issues di-group by (category, severity)
    workflow_counter: Counter = Counter()
    workflow_examples: dict[tuple[str, str], list[str]] = defaultdict(list)
    substansi_counter: Counter = Counter()
    substansi_examples: dict[tuple[str, str], list[str]] = defaultdict(list)

    # severity heatmap per agent
    severity_heatmap: dict[str, Counter] = defaultdict(Counter)

    # pattern suggestions di-group by judul (normalize lower)
    pattern_counter: Counter = Counter()
    pattern_meta: dict[str, dict] = {}
    pattern_rationales: dict[str, list[str]] = defaultdict(list)

    for row in feedback_rows:
        agent = _safe_str(row.get("agent_name"), 40) or "unknown"
        conf = _safe_str(row.get("overall_confidence"), 10).upper() or "MEDIUM"
        by_agent[agent] += 1
        by_confidence[conf] += 1

        for w in row.get("workflow_issues", []) or []:
            cat = _safe_str(w.get("category"), 40)
            sev = _safe_str(w.get("severity"), 20)
            key = (cat, sev)
            workflow_counter[key] += 1
            severity_heatmap[agent][sev] += 1
            desc = _safe_str(w.get("description"), 240)
            if desc and len(workflow_examples[key]) < 3:
                workflow_examples[key].append(desc)

        for s in row.get("substansi_issues", []) or []:
            cat = _safe_str(s.get("category"), 40)
            sev = _safe_str(s.get("severity"), 20)
            key = (cat, sev)
            substansi_counter[key] += 1
            severity_heatmap[agent][sev] += 1
            desc = _safe_str(s.get("description"), 240)
            if desc and len(substansi_examples[key]) < 3:
                substansi_examples[key].append(desc)

        for p in row.get("pattern_suggestions", []) or []:
            judul = _safe_str(p.get("judul"), 200)
            if not judul:
                continue
            norm_key = judul.lower()
            pattern_counter[norm_key] += 1
            if norm_key not in pattern_meta:
                pattern_meta[norm_key] = {
                    "id_proposed": _safe_str(p.get("id_proposed"), 30),
                    "judul": judul,
                }
            rationale = _safe_str(p.get("rationale"), 240)
            if rationale and len(pattern_rationales[norm_key]) < 3:
                pattern_rationales[norm_key].append(rationale)

    top_workflow = [
        {
            "category": cat,
            "severity": sev,
            "count": cnt,
            "examples": workflow_examples[(cat, sev)],
        }
        for (cat, sev), cnt in workflow_counter.most_common(5)
    ]
    top_substansi = [
        {
            "category": cat,
            "severity": sev,
            "count": cnt,
            "examples": substansi_examples[(cat, sev)],
        }
        for (cat, sev), cnt in substansi_counter.most_common(5)
    ]
    top_patterns = [
        {
            **pattern_meta[key],
            "count": cnt,
            "rationales": pattern_rationales[key],
        }
        for key, cnt in pattern_counter.most_common(5)
    ]

    # recent files (top 20, urutan terbaru duluan)
    recent = sorted(
        feedback_rows,
        key=lambda r: r.get("_mtime", ""),
        reverse=True,
    )[:20]
    recent_files = [
        {
            "path": Path(r["_file_path"]).name,
            "full_path": r["_file_path"],
            "agent": _safe_str(r.get("agent_name"), 40),
            "confidence": _safe_str(r.get("overall_confidence"), 10).upper(),
            "summary": _safe_str(r.get("summary"), 200),
            "penugasan_folder": r.get("_penugasan_folder", ""),
            "timestamp": r.get("timestamp"),
            "workflow_count": len(r.get("workflow_issues", []) or []),
            "substansi_count": len(r.get("substansi_issues", []) or []),
            "pattern_count": len(r.get("pattern_suggestions", []) or []),
        }
        for r in recent
    ]

    return {
        "days": days,
        "total_feedback": len(feedback_rows),
        "by_agent": dict(by_agent),
        "by_confidence": dict(by_confidence),
        "top_workflow_issues": top_workflow,
        "top_substansi_issues": top_substansi,
        "top_pattern_suggestions": top_patterns,
        "severity_heatmap": {
            agent: dict(counts) for agent, counts in severity_heatmap.items()
        },
        "recent_files": recent_files,
    }


@router.get("/list")
async def list_feedback(
    days: int = Query(30, ge=1, le=365),
    current: tuple[User, Role] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Daftar file feedback mentah untuk drill-down.

    Tidak include isi penuh — frontend bisa ambil per file via preview endpoint
    yang sudah ada di routes/files.py.
    """
    penugasan_rows = (
        await db.execute(select(Penugasan.id, Penugasan.folder_path, Penugasan.obyek))
    ).all()
    folders_index = {Path(row[1]).name: (row[0], row[2]) for row in penugasan_rows if row[1]}
    folders = [Path(row[1]) for row in penugasan_rows if row[1]]

    cutoff = datetime.utcnow() - timedelta(days=days)
    feedback_rows = _collect_feedback(folders, cutoff)
    feedback_rows.sort(key=lambda r: r.get("_mtime", ""), reverse=True)

    items: list[dict[str, Any]] = []
    for r in feedback_rows:
        folder_name = r.get("_penugasan_folder", "")
        pid, obyek = folders_index.get(folder_name, (None, ""))
        items.append({
            "file": Path(r["_file_path"]).name,
            "agent": _safe_str(r.get("agent_name"), 40),
            "confidence": _safe_str(r.get("overall_confidence"), 10).upper(),
            "summary": _safe_str(r.get("summary"), 240),
            "workflow_count": len(r.get("workflow_issues", []) or []),
            "substansi_count": len(r.get("substansi_issues", []) or []),
            "pattern_count": len(r.get("pattern_suggestions", []) or []),
            "timestamp": r.get("timestamp"),
            "penugasan_id": pid,
            "penugasan_obyek": obyek,
            "penugasan_folder": folder_name,
        })

    return {
        "days": days,
        "total": len(items),
        "items": items,
    }
