"""Routes Knowledge / Wiki.

- W1 (baca vault): vault_search / vault_get_page → panel "Cari Wiki". Read-only.
- W2 (promosi pattern): agregasi usulan pattern dari feedback agen lintas
  penugasan (`/pattern-monitor`) + promote jadi pattern wiki resmi (`/patterns`,
  PT/PM). Lihat app.wiki_promote.

V6 read-only — promosi menulis ke folder wiki proyek, bukan ke V6.
"""
from datetime import datetime, timedelta
from pathlib import Path

from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app import wiki_promote
from app.auth import get_current_user
from app.database import get_db
from app.models import Penugasan, Role, User
from app.routes.feedback import _collect_feedback
from app.tools.wiki_tools import vault_get_page, vault_search

router = APIRouter(prefix="/knowledge", tags=["knowledge"])


@router.get("/wiki/search")
async def wiki_search(
    q: str,
    limit: int = 12,
    _current: tuple[User, Role] = Depends(get_current_user),
) -> dict:
    """Cari catatan vault relevan dengan query `q`."""
    return vault_search(q, limit=max(1, min(limit, 50)))


@router.get("/wiki/page")
async def wiki_page(
    name: str,
    _current: tuple[User, Role] = Depends(get_current_user),
) -> dict:
    """Baca isi lengkap satu catatan vault by name (aman dari path traversal)."""
    return vault_get_page(name)


# =============================================================================
# W2 — promosi pattern
# =============================================================================

@router.get("/pattern-monitor")
async def pattern_monitor(
    days: int = Query(90, ge=1, le=365, description="Window hari ke belakang"),
    _current: tuple[User, Role] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Agregasi usulan pattern (`pattern_suggestions`) dari feedback agen lintas
    penugasan. Kandidat yg berulang = bahan promosi jadi pattern wiki resmi.

    Read-only & role-agnostik (sejalan dgn /feedback/aggregate).
    """
    rows = (
        await db.execute(select(Penugasan.folder_path, Penugasan.skill, Penugasan.obyek))
    ).all()
    folders: list[Path] = []
    folder_meta: dict[str, dict] = {}
    for folder_path, skill, obyek in rows:
        if not folder_path:
            continue
        p = Path(folder_path)
        folders.append(p)
        folder_meta[p.name] = {
            "skill": skill if isinstance(skill, str) else getattr(skill, "value", str(skill)),
            "obyek": obyek or "",
        }

    cutoff = datetime.utcnow() - timedelta(days=days)
    feedback_rows = _collect_feedback(folders, cutoff)
    result = wiki_promote.aggregate_pattern_suggestions(feedback_rows, folder_meta)
    result["days"] = days
    result["total_feedback"] = len(feedback_rows)
    return result


@router.post("/patterns")
async def create_pattern(
    body: dict = Body(...),
    current: tuple[User, Role] = Depends(get_current_user),
) -> dict:
    """Promote satu usulan jadi pattern wiki resmi (tulis file .md). PT/PM only."""
    role = current[1]
    if role not in (Role.PT, Role.PM):
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            f"Promosi pattern hanya untuk PT/PM (kurasi knowledge). Role Anda: {role.value}.",
        )

    res = wiki_promote.promote_pattern(
        skill=str(body.get("skill", "")).strip(),
        pattern_id=str(body.get("pattern_id") or body.get("id") or "").strip(),
        judul=str(body.get("judul", "")).strip(),
        kategori=str(body.get("kategori", "")).strip(),
        severity=str(body.get("severity", "MEDIUM")).strip(),
        kriteria_baku=str(body.get("kriteria_baku", "")).strip(),
        kondisi=str(body.get("kondisi", "")).strip(),
        akibat=str(body.get("akibat", "")).strip(),
        rekomendasi=str(body.get("rekomendasi", "")).strip(),
        bukti=str(body.get("bukti", "")).strip(),
        tags=body.get("tags") if isinstance(body.get("tags"), list) else None,
        sumber_penugasan=body.get("sumber_penugasan") if isinstance(body.get("sumber_penugasan"), list) else None,
    )
    if not res.get("ok"):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, res.get("error", "gagal promote pattern"))
    return res
