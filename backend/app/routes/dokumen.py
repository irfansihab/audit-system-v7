"""Routes upload & ingestion dokumen.

Setelah upload, ingestion otomatis ter-trigger sebagai background task — auditor
tidak perlu klik tombol "Jalankan Ingestion" terpisah. Kalau file sudah ada di
cache (sha256 match), status langsung READY tanpa re-process.
"""
import asyncio
import logging
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user
from app.database import get_db
from app.models import DocumentCache, Dokumen, DokumenStatus, Penugasan, Role, User
from app.schemas import DokumenOut
from app.storage import (
    classify_doc_by_filename,
    save_upload,
    sha256_bytes,
    target_subfolder_for,
)

log = logging.getLogger(__name__)
router = APIRouter(prefix="/dokumen", tags=["dokumen"])


async def _ingest_background(penugasan_id: int) -> None:
    """Wrapper untuk panggil _run_ingestion dari background task.

    Import lazy supaya tidak ada cycle dengan routes.agen (yang juga import
    dari routes.dokumen indirectly via app namespace).
    """
    try:
        from app.routes.agen import _run_ingestion
        await _run_ingestion(penugasan_id)
    except Exception as e:
        log.exception("Background ingestion gagal untuk penugasan_id=%d: %s", penugasan_id, e)


@router.post("", response_model=DokumenOut, status_code=status.HTTP_201_CREATED)
async def upload_dokumen(
    background_tasks: BackgroundTasks,
    penugasan_id: int = Form(...),
    jenis: str | None = Form(None),
    file: UploadFile = File(...),
    current: tuple[User, Role] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> DokumenOut:
    p = (
        await db.execute(select(Penugasan).where(Penugasan.id == penugasan_id))
    ).scalar_one_or_none()
    if not p:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Penugasan tidak ditemukan")

    content = await file.read()
    if len(content) > 50 * 1024 * 1024:
        raise HTTPException(status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, "Max 50 MB per file")

    sha = sha256_bytes(content)
    jenis_final = jenis or classify_doc_by_filename(file.filename or "")
    sub = target_subfolder_for(jenis_final)
    target = Path(p.folder_path) / sub / (file.filename or "dokumen.bin")
    await save_upload(content, target)

    # Cek cache → kalau ada, langsung READY tanpa ingestion ulang
    cached = (
        await db.execute(select(DocumentCache).where(DocumentCache.sha256 == sha))
    ).scalar_one_or_none()

    # Tentukan status awal:
    # - Cache HIT       → READY (skip ingestion)
    # - ST/KP/PKP/OTHER → langsung READY (tidak butuh digest script)
    # - TOR/RAB/KAK/HPS/RFI/KONTRAK → INGESTING (auto-trigger background)
    if cached:
        initial_status = DokumenStatus.READY
    elif jenis_final in ("TOR", "RAB", "KAK", "HPS", "RFI", "KONTRAK"):
        initial_status = DokumenStatus.INGESTING
    else:
        # ST, KP, PKP, OTHER, None — tidak ada V6 digest script untuk ini,
        # tapi tetap tersedia untuk dibaca agen lain
        initial_status = DokumenStatus.READY

    d = Dokumen(
        penugasan_id=p.id,
        nama_file=file.filename or "dokumen.bin",
        file_path=str(target),
        jenis=jenis_final,
        sha256=sha,
        size_bytes=len(content),
        status=initial_status,
        ingested_json_path=cached.ingested_json_path if cached else None,
        ingested_at=datetime.utcnow() if (cached or initial_status == DokumenStatus.READY) else None,
    )
    db.add(d)
    await db.flush()
    await db.refresh(d)

    # Auto-trigger ingestion kalau status INGESTING (V6 digest script perlu jalan)
    if initial_status == DokumenStatus.INGESTING:
        # commit dulu supaya background task lihat doc yang baru
        await db.commit()
        background_tasks.add_task(_ingest_background, p.id)

    return DokumenOut.model_validate(d)


@router.get("", response_model=list[DokumenOut])
async def list_dokumen(
    penugasan_id: int,
    current: tuple[User, Role] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[DokumenOut]:
    rows = (
        await db.execute(
            select(Dokumen).where(Dokumen.penugasan_id == penugasan_id).order_by(Dokumen.id)
        )
    ).scalars().all()
    return [DokumenOut.model_validate(r) for r in rows]
