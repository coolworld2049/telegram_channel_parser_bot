from pydantic import BaseModel


class SendCodeRequest(BaseModel):
    phone: str


class SendConfirmationCodeRequest(BaseModel):
    phone: str
    code: str
