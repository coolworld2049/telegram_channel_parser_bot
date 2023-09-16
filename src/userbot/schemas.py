from pydantic import BaseModel


class ChatSearchRequest(BaseModel):
    keywords: list[str] = ["linux"]
    limit: int = 10


class ChatSearchResponse(BaseModel):
    username: str = None
    title: str = None


class AuthRequest(BaseModel):
    phone: str = None


class AuthCodeRequest(AuthRequest):
    confirm_code: str = None
