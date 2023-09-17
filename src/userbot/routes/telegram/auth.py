import json

from fastapi import APIRouter, HTTPException
from loguru import logger
from starlette import status
from starlette.requests import Request
from starlette.responses import JSONResponse

import userbot
from userbot import client
from userbot.schemas.auth import SendCodeRequest, SendConfirmationCodeRequest

router = APIRouter(prefix="/telegram", tags=["telegram"])


@router.post("/auth", response_model=dict)
async def telegram_auth(request: Request, payload: SendCodeRequest):
    """

    :param request:
    :param payload:
    :return: sent_code: SentCode
    """
    await client.connect()
    if await client.is_user_authorized():
        user = await client.get_me()
        return JSONResponse(json.loads(user.to_json(default=str)))
    sent_code = await client.send_code_request(payload.phone)
    return JSONResponse(json.loads(sent_code.to_json(default=str)))


@router.post("/auth/sign_in", response_model=dict)
async def telegram_sign_in(request: Request, payload: SendConfirmationCodeRequest):
    """

    :param request:
    :param payload:
    :return: user: User | SentCode
    """
    await client.connect()
    try:
        user = await client.sign_in(payload.phone, payload.code)
        userbot.client = client
        return JSONResponse(json.loads(user.to_json(default=str)))
    except Exception as e:
        logger.error(e)
        return HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR)
