from telethon import TelegramClient

from core.settings import get_settings

client = TelegramClient(
    "my", get_settings().API_ID, get_settings().API_HASH, auto_reconnect=True
)
