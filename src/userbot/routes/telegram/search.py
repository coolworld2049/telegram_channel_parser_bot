import asyncio
import json
from urllib.error import HTTPError

from fastapi import APIRouter, HTTPException
from googlesearch import search
from loguru import logger
from starlette import status
from starlette.requests import Request
from telethon import functions
from telethon.tl.types import Channel

import userbot
import userbot.main
from userbot import client
from userbot.schemas.search import (
    SearchQueryRequest,
    GoogleSearchRequest,
    TelethonSearchRequest,
)
from userbot.services.search_engine.main import generate_search_queries

router = APIRouter(prefix="/telegram", tags=["telegram"])


def get_search_queries(payload):
    new_search_queries = set()
    payload = SearchQueryRequest(**payload.model_dump())
    for query in generate_search_queries(**payload.model_dump()):
        md = query.model_dump(exclude_none=True).values()
        if len(md) > 0:
            q = " ".join(md).strip(" ")
            new_search_queries.add(q)
    new_search_queries = sorted(new_search_queries, key=lambda x: len(x))
    return new_search_queries


@router.post("/search_query", response_model=list[str])
async def telegram_search_query(request: Request, payload: SearchQueryRequest):
    if client.disconnected:
        await client.connect()
    new_search_queries = get_search_queries(payload)
    return new_search_queries


@router.post("/telethon_search", response_model=list[dict])
async def telethon_search_chat(request: Request, payload: TelethonSearchRequest):
    if client.disconnected:
        await client.connect()
    search_results = []
    for i, q in enumerate(get_search_queries(payload)):
        await asyncio.sleep(payload.delay)
        sr = await userbot.client(
            functions.contacts.SearchRequest(q, limit=payload.limit)
        )
        logger.debug(f"{i} - {q}. Telethon search result: {len(sr.chats)}")
        for src in sr.chats:
            src: Channel
            search_results.append(json.loads(src.to_json(default=str)))
    logger.debug(f"Quantity: {len(search_results)}")
    return search_results


@router.post("/google_search", response_model=list[dict])
async def google_search_chat(request: Request, payload: GoogleSearchRequest):
    if client.disconnected:
        await client.connect()
    search_results = []
    for i, q in enumerate(get_search_queries(payload)):
        google_dork = f"site:t.me/joinchat {q}"
        logger.debug(f"{i} - {google_dork} ...")
        await asyncio.sleep(payload.pause)
        try:
            for j, src in enumerate(
                search(
                    google_dork,
                    **GoogleSearchRequest(**payload.model_dump()).model_dump(),
                )
            ):
                search_results.append(src)
        except HTTPError as he:
            logger.error(he)
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=str(he.args)
            )
        logger.debug(f"{i} - {google_dork}")
    logger.debug(f"Quantity: {len(search_results)}")
    return search_results
