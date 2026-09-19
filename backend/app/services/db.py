"""
MongoDB Atlas case storage. If MONGODB_URI is unset, falls back to an in-memory
dict so the app runs for everyone; History just won't persist across restarts.
"""

import logging

from backend.app.config import settings
from backend.app.schemas import AnalysisResult, CaseSummary

log = logging.getLogger(__name__)

_memory: dict[str, dict] = {}
_collection = None


def _get_collection():
    global _collection
    if _collection is None and settings.mongodb_uri:
        from motor.motor_asyncio import AsyncIOMotorClient

        client = AsyncIOMotorClient(settings.mongodb_uri, serverSelectionTimeoutMS=3000)
        _collection = client[settings.mongodb_db]["cases"]
    return _collection


async def save_case(result: AnalysisResult, session_id: str) -> None:
    doc = result.model_dump(mode="json")
    doc["_id"] = result.case_id
    doc["session_id"] = session_id
    col = _get_collection()
    if col is None:
        _memory[result.case_id] = doc
        return
    try:
        await col.replace_one({"_id": result.case_id}, doc, upsert=True)
    except Exception as exc:  # noqa: BLE001
        log.warning("Mongo save failed (%s); keeping in memory", exc)
        _memory[result.case_id] = doc


async def list_cases(session_id: str, limit: int = 50) -> list[CaseSummary]:
    col = _get_collection()
    docs: list[dict]
    if col is None:
        docs = [d for d in _memory.values() if d.get("session_id") == session_id]
    else:
        try:
            cursor = (
                col.find({"session_id": session_id}, {"case_id": 1, "created_at": 1, "burden": 1})
                .sort("created_at", -1)
                .limit(limit)
            )
            docs = await cursor.to_list(length=limit)
        except Exception as exc:  # noqa: BLE001
            log.warning("Mongo list failed (%s); using memory", exc)
            docs = [d for d in _memory.values() if d.get("session_id") == session_id]
    docs.sort(key=lambda d: d["created_at"], reverse=True)
    return [
        CaseSummary(
            case_id=d["case_id"],
            created_at=d["created_at"],
            lesion_count=d["burden"]["lesion_count"],
            atypical_count=d["burden"]["atypical_count"],
        )
        for d in docs[:limit]
    ]


async def get_case(case_id: str) -> AnalysisResult | None:
    col = _get_collection()
    doc = None
    if col is not None:
        try:
            doc = await col.find_one({"_id": case_id})
        except Exception as exc:  # noqa: BLE001
            log.warning("Mongo get failed (%s); using memory", exc)
    if doc is None:
        doc = _memory.get(case_id)
    if doc is None:
        return None
    doc = {k: v for k, v in doc.items() if k != "_id"}
    return AnalysisResult.model_validate(doc)