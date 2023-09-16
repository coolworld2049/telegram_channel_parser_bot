import asyncio

from fastapi import APIRouter, HTTPException
from starlette import status
from starlette.requests import Request
from telethon import functions

import userbot
import userbot.main
from userbot import client
from userbot.schemas.search import SearchQueryRequest
from userbot.services.search_engine.main import generate_search_queries

router = APIRouter(prefix="/telegram", tags=["telegram"])


@router.post("/search_query", response_model=list[str])
async def telegram_search_query(request: Request, payload: SearchQueryRequest):
    search_queries = generate_search_queries(
        **payload.model_dump(exclude={"limit", "delay"})
    )
    if not search_queries:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    new_search_queries = []
    for query in search_queries:
        await asyncio.sleep(payload.delay)
        q = " ".join(list(query.model_dump().values())).strip(" ")
        new_search_queries.append(q)
    return new_search_queries


@router.post("/search", response_model=list[dict])
async def telegram_search_chat(request: Request, payload: SearchQueryRequest):
    await client.connect()
    search_queries = generate_search_queries(
        **payload.model_dump(exclude={"limit", "delay"})
    )
    if not search_queries:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    search_results = []
    for query in search_queries:
        q = f"{query.country} {query.city} {query.category}"
        sr = await userbot.client(
            functions.contacts.SearchRequest(q, limit=payload.limit)
        )
        for src in sr.chats:
            data = src.__dict__
            data["default_banned_rights"] = None
            data["photo"] = None
            search_results.append(data)
    if not search_results:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return search_results
