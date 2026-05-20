"""Routes untuk akses file output penugasan dari frontend.

Endpoints:
- GET /penugasan/{id}/files            → list file di subfolder output
- GET /penugasan/{id}/files/download   → download file individual

Path validation strict: tidak boleh path traversal di luar folder penugasan.
Auth via Bearer token (sama dengan endpoint lain).
"""
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import quote

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user
from app.database import get_db
from app.models import Penugasan, Role, User

router = APIRouter(prefix="/penugasan", tags=["files"])


# Kategorisasi subfolder untuk grouping di UI
CATEGORIES = {
    "_KKP": "Kertas Kerja Pengawasan (KKP)",
    "_LHP": "Laporan Hasil Reviu (LHR)",
    "_QA-SAIPI": "QC SAIPI",
    "_FEEDBACK-AGEN": "Feedback Agen",
    "_INGESTED": "Hasil Ingestion",
    "_AUDIT-TRAIL": "Audit Trail",
    "_PKP": "Program Kerja",
    "_BUKTI-AI": "Bukti AI",
    "_SUBMIT": "Submit / INTEGRAL",
}

# Subfolder yang TIDAK ditampilkan (input docs sudah accessible lewat upload tab)
HIDDEN_SUBFOLDERS = {"00-input", "01-peraturan-internal", "02-kontrak", "03-perencanaan",
                     "04-pelaksanaan", "05-keuangan"}


# MIME type mapping untuk download
EXT_MIME = {
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".pdf": "application/pdf",
    ".json": "application/json",
    ".md": "text/markdown; charset=utf-8",
    ".txt": "text/plain; charset=utf-8",
    ".csv": "text/csv; charset=utf-8",
    ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ".html": "text/html; charset=utf-8",
    ".jsonl": "application/x-ndjson",
}


async def _get_penugasan_or_404(db: AsyncSession, penugasan_id: int) -> Penugasan:
    p = (
        await db.execute(select(Penugasan).where(Penugasan.id == penugasan_id))
    ).scalar_one_or_none()
    if not p:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Penugasan tidak ditemukan")
    return p


def _safe_resolve(base: Path, rel_path: str) -> Path:
    """Resolve rel_path terhadap base, tolak kalau keluar dari base (no traversal)."""
    target = (base / rel_path).resolve()
    base_resolved = base.resolve()
    try:
        target.relative_to(base_resolved)
    except ValueError:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Path tidak valid (traversal terdeteksi)")
    return target


@router.get("/{penugasan_id}/files")
async def list_files(
    penugasan_id: int,
    current: tuple[User, Role] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """List file output di subfolder kategoris.

    Return:
        {
            "penugasan_id": int,
            "folder_path": str,
            "categories": [
                {
                    "key": "_KKP",
                    "label": "Kertas Kerja Pengawasan (KKP)",
                    "files": [
                        {
                            "name": "KKP-Sarah-Aulia.docx",
                            "path": "_KKP/KKP-Sarah-Aulia.docx",
                            "size_bytes": 18452,
                            "mtime": "2026-05-19T10:30:00",
                            "ext": ".docx"
                        }, ...
                    ]
                }, ...
            ]
        }
    """
    p = await _get_penugasan_or_404(db, penugasan_id)
    folder = Path(p.folder_path)
    if not folder.exists():
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Folder penugasan tidak ada di disk: {folder}")

    categories: list[dict[str, Any]] = []
    for key, label in CATEGORIES.items():
        sub = folder / key
        if not sub.exists() or not sub.is_dir():
            continue
        files: list[dict[str, Any]] = []
        for f in sorted(sub.rglob("*")):
            if not f.is_file() or f.name.startswith("."):
                continue
            try:
                stat = f.stat()
            except OSError:
                continue
            files.append({
                "name": f.name,
                "path": str(f.relative_to(folder)),
                "size_bytes": stat.st_size,
                "mtime": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "ext": f.suffix.lower(),
            })
        if files:
            categories.append({"key": key, "label": label, "files": files})

    # Tambahkan file di root penugasan (mis. context.md) sebagai kategori "Konteks"
    root_files: list[dict[str, Any]] = []
    for f in sorted(folder.iterdir()):
        if (f.is_file() and not f.name.startswith(".")):
            try:
                stat = f.stat()
            except OSError:
                continue
            root_files.append({
                "name": f.name,
                "path": f.name,
                "size_bytes": stat.st_size,
                "mtime": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "ext": f.suffix.lower(),
            })
    if root_files:
        categories.insert(0, {"key": "_ROOT", "label": "Konteks Penugasan", "files": root_files})

    return {
        "penugasan_id": p.id,
        "folder_path": str(folder),
        "categories": categories,
    }


@router.get("/{penugasan_id}/files/download")
async def download_file(
    penugasan_id: int,
    path: str = Query(..., description="Path relatif terhadap folder penugasan, mis. _KKP/KKP-Sarah-Aulia.docx"),
    current: tuple[User, Role] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> FileResponse:
    """Download file individual dari folder penugasan.

    Validasi:
    - Path tidak boleh keluar dari folder penugasan (no traversal)
    - File harus ada dan readable
    """
    p = await _get_penugasan_or_404(db, penugasan_id)
    base = Path(p.folder_path)
    if not base.exists():
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Folder penugasan tidak ada di disk")

    target = _safe_resolve(base, path)
    if not target.exists() or not target.is_file():
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"File tidak ditemukan: {path}")

    mime = EXT_MIME.get(target.suffix.lower(), "application/octet-stream")
    # quote filename untuk handle karakter non-ASCII di nama file
    fname_quoted = quote(target.name)
    return FileResponse(
        path=str(target),
        media_type=mime,
        filename=target.name,
        headers={
            "Content-Disposition": f"attachment; filename*=UTF-8''{fname_quoted}",
        },
    )


@router.get("/{penugasan_id}/files/preview")
async def preview_file(
    penugasan_id: int,
    path: str = Query(..., description="Path relatif terhadap folder penugasan"),
    max_bytes: int = Query(50_000, le=200_000, description="Batas baca, default 50KB"),
    current: tuple[User, Role] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Preview file text-based (.md, .json, .txt, .jsonl) langsung di UI tanpa download.

    Untuk file binary (.docx, .pdf), client harus pakai endpoint /download.
    """
    p = await _get_penugasan_or_404(db, penugasan_id)
    base = Path(p.folder_path)
    target = _safe_resolve(base, path)
    if not target.exists() or not target.is_file():
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"File tidak ditemukan: {path}")

    ext = target.suffix.lower()
    if ext not in {".md", ".json", ".txt", ".jsonl", ".csv", ".log"}:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            f"Ext {ext} tidak bisa di-preview. Pakai /download untuk file binary.",
        )

    try:
        size = target.stat().st_size
        with target.open("r", encoding="utf-8", errors="replace") as f:
            content = f.read(max_bytes)
        truncated = size > max_bytes
    except OSError as e:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, f"Gagal baca file: {e}")

    return {
        "path": path,
        "size_bytes": size,
        "ext": ext,
        "truncated": truncated,
        "content": content,
    }
