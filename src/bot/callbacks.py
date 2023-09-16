from typing import Optional

from aiogram.filters.callback_data import CallbackData


class MenuCallback(CallbackData, prefix="menu"):
    name: str
    action: Optional[str] = None
    message_id: Optional[int] = None
