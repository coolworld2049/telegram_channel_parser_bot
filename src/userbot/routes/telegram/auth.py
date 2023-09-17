from fastapi import APIRouter
from starlette.requests import Request

import userbot
from userbot import client
from userbot.schemas.auth import SendCodeRequest, SendConfirmationCodeRequest

router = APIRouter(prefix="/telegram", tags=["telegram"])


@router.post(
    "/auth",
)
async def telegram_auth(request: Request, payload: SendCodeRequest):
    await client.connect()
    if not await client.is_user_authorized():
        await client.send_code_request(payload.phone)
    return {"message": "Confirmation code sent"}


@router.post(
    "/auth/sign_in",
)
async def telegram_auth(request: Request, payload: SendConfirmationCodeRequest):
    try:
        await client.sign_in(payload.phone, payload.confirm_code)
        userbot.client = client
        return {"message": "Success"}
    except:
        return {"message": "Failure"}
