import asyncio
import json

from fastapi import APIRouter, HTTPException
from loguru import logger
from starlette import status
from starlette.requests import Request
from telethon import functions
from telethon.tl.types import Chat

import userbot
import userbot.main
from userbot import client
from userbot.schemas.search import SearchQueryRequest
from userbot.services.search_engine.main import generate_search_queries

router = APIRouter(prefix="/telegram", tags=["telegram"])


@router.post("/search_query", response_model=list[str])
async def telegram_search_query(request: Request, payload: SearchQueryRequest):
    if client.disconnected:
        await client.connect()
    new_search_queries = []
    for query in generate_search_queries(
        **payload.model_dump(exclude={"limit", "delay"})
    ):
        await asyncio.sleep(payload.delay)
        q = " ".join(list(query.model_dump().values())).strip(" ")
        new_search_queries.append(q)
    return new_search_queries


@router.post("/search", response_model=list[dict])
async def telegram_search_chat(request: Request, payload: SearchQueryRequest):
    if client.disconnected:
        await client.connect()
    search_results = []
    for i, query in enumerate(
        generate_search_queries(**payload.model_dump(exclude={"limit", "delay"}))
    ):
        await asyncio.sleep(payload.delay)
        q = " ".join(list(query.model_dump().values())).strip(" ")
        if q == "":
            continue
        sr = await userbot.client(
            functions.contacts.SearchRequest(q, limit=payload.limit)
        )
        logger.debug(f"{i} - {q}. Chat count: {len(sr.chats)}")
        for src in sr.chats:
            src: Chat
            search_results.append(json.loads(src.to_json(default=str)))
    if not search_results:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return search_results
