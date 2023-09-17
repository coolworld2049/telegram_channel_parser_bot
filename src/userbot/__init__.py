from telethon import TelegramClient

from core.settings import get_settings

telethon_client = None
if all([get_settings().API_ID, get_settings().API_HASH]):
    telethon_client = TelegramClient(
        "my", get_settings().API_ID, get_settings().API_HASH, auto_reconnect=True
    )
