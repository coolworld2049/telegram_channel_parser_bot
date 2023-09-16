from fastapi import APIRouter, HTTPException
from starlette import status
from starlette.requests import Request
from telethon import functions

import userbot
import userbot.main
from userbot import client
from userbot.schemas import ChatSearchRequest

router = APIRouter(prefix="/telegram", tags=["telegram"])


@router.post("/search", response_model=list[dict])
async def telegram_search(request: Request, payload: ChatSearchRequest):
    await client.connect()
    search_results = None
    for keyword in payload.keywords:
        search_results = await userbot.client(
            functions.contacts.SearchRequest(q=keyword, limit=payload.limit)
        )
    if not search_results:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    response = []
    for x in search_results.chats:
        data = x.__dict__
        data["default_banned_rights"] = None
        data["photo"] = None
        response.append(data)
    return response
