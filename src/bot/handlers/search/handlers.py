from aiogram import Router, types
from aiogram.filters import Command

from bot.dispatcher import dp

router = Router(name=__file__)


@dp.message(Command("search_channels"))
async def search_channels_handler(message: types.Message):
    await message.reply("Please enter your search query:")
