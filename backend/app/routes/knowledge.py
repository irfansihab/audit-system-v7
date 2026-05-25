"""Routes Knowledge / Wiki — akses baca vault pengetahuan (W1).

Membungkus fungsi inti di app.tools.wiki_tools (vault_search / vault_get_page)
sebagai endpoint HTTP untuk panel "Cari Wiki" di frontend. Read-only.
"""
from fastapi import APIRouter, Depends

from app.auth import get_current_user
from app.models import Role, User
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
