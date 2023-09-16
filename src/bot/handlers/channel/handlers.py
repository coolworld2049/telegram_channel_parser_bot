from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from telethon import TelegramClient

from userbot._main import search_chats

router = Router(name=__file__)


@router.message(Command("search"))
async def start_message(message: Message, state: FSMContext):
    client: TelegramClient = message.bot.telethon_client  # noqa
    # res = await search_chats(client)
    await message.answer("\n".join(res))
