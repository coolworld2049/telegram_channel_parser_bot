from fastapi import APIRouter
from starlette.requests import Request

import userbot.main
from main import client
from schemas import AuthRequest, AuthCodeRequest

router = APIRouter(prefix="/telegram", tags=["telegram"])


@router.post(
    "/auth/send_code_request",
)
async def telegram_auth(request: Request, payload: AuthRequest):
    await client.connect()
    if not await client.is_user_authorized():
        await client.send_code_request(payload.phone)
    return {"message": "Confirmation code sent"}


@router.post(
    "/auth/sign_in",
)
async def telegram_auth(request: Request, payload: AuthCodeRequest):
    await client.connect()
    try:
        await client.sign_in(payload.phone, payload.confirm_code)
        userbot.main.client = client
        return {"message": "Success"}
    except:
        return {"message": "Failure"}
