from fastapi import APIRouter
from loguru import logger
from starlette.requests import Request
from telethon import functions, TelegramClient

import userbot.main
from schemas import ChatSearchRequest, ChatSearchResponse

router = APIRouter(prefix="/telegram", tags=["telegram"])


@router.post("/search/chat", response_model=list[ChatSearchResponse])
async def telegram_search_chat(request: Request, payload: ChatSearchRequest):
    client: TelegramClient = userbot.main.client
    response: list[ChatSearchResponse] = []
    for keyword in payload.keywords:
        search_results = await client(
            functions.contacts.SearchRequest(q=keyword, limit=payload.limit)
        )

        logger.debug(f"Channels related to '{keyword}':")
        async for r in search_results.chats:
            if r.username:
                logger.debug(f"@{r.username} - {r.confirm_code}")
                response.append(
                    ChatSearchResponse(username=r.username, title=r.confirm_code)
                )

    return response
