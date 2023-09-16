from fastapi import APIRouter
from starlette.requests import Request

import userbot.main
from userbot.main import client
from userbot.schemas import AuthRequest, AuthCodeRequest

router = APIRouter(prefix="/telegram", tags=["telegram"])


@router.post(
    "/auth/phone_number",
)
async def telegram_auth(request: Request, payload: AuthRequest):
    await client.connect()
    if not await client.is_user_authorized():
        await client.send_code_request(payload.phone)
    return {"message": "Confirmation code sent"}


@router.post(
    "/auth/confirmation",
)
async def telegram_auth(request: Request, payload: AuthCodeRequest):
    await client.connect()
    try:
        await client.sign_in(payload.phone, payload.confirm_code)
        userbot.main.client = client
        return {"message": "Success"}
    except:
        return {"message": "Failure"}
