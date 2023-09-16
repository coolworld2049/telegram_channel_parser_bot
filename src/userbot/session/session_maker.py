import asyncio
import os
import re

from dotenv import load_dotenv

load_dotenv()

try:
    import pyrogram
except ModuleNotFoundError:
    print(
        "You need to install pyrogram first!\nSee: https://github.com/AyraHikari/pyrogram-session-maker"
    )
    exit(1)

# Cleanup
try:
    os.remove("my.session")
except:  # noqa
    pass
try:
    os.remove("bot.session")
except:  # noqa
    pass


def clear():
    if os.name == "posix":
        a = os.system("clear")
    elif os.name == "nt":
        a = os.system("cls")
    else:
        pass


clear()
print(
    """
 _  _  _       _                        
| || || |     | |                       
| || || | ____| | ____ ___  ____   ____ 
| ||_|| |/ _  ) |/ ___) _ \|    \ / _  )
| |___| ( (/ /| ( (__| |_| | | | ( (/ / 
 \______|\____)_|\____)___/|_|_|_|\____)                                  
"""
)
print(
    "You need to register to get app_id and api_hash in here:\nhttps://my.telegram.org/apps"
)
input("Press any key to continue")


def initial_selection(api_id, app_hash):
    clear()
    while True:
        print("You want to make session for user bot or real bot?")
        print("1 = user bot")
        print("2 = real bot")
        create_bot = input("[1/2] ")
        if str(create_bot).isdigit() and int(create_bot) in (1, 2):
            create_bot = int(create_bot)
            break
        print("Invaild selection!\n")
    phone_number = os.getenv("PHONE_NUMBER") or input("Enter phone number: ")
    session_maker(create_bot, api_id, app_hash, phone_number)


def fill_api():
    clear()
    while True:
        api_id = os.getenv("API_ID") or input("Insert app_id: ")
        if str(api_id).isdigit():
            break
        print("Invaild app_id!\n")

    while True:
        api_hash = os.getenv("API_HASH") or input("Insert api_hash: ")
        if api_hash:
            break
        print("Invaild api_hash!\n")
    initial_selection(api_id, api_hash)


def session_maker(create_bot, api_id, app_hash, phone_number):
    clear()
    session = None
    session_txt = None
    if re.search("asyncio", pyrogram.__version__):
        if create_bot == 1:
            app = pyrogram.Client(
                "my", api_id=api_id, api_hash=app_hash, phone_number=phone_number
            )
            session = "my.session"
            session_txt = "my.txt"
        elif create_bot == 2:
            bot_token = os.getenv("BOT_TOKEN") or input("Insert bot token: ")
            app = pyrogram.Client(
                "bot",
                api_id=api_id,
                api_hash=app_hash,
                bot_token=bot_token,
                phone_number=phone_number,
            )
            session = "bot.session"
            session_txt = "bot.txt"

        async def start_app():
            await app.start()
            session = app.export_session_string()
            print(f"Done!\nYour session string is:\n\n{session}")
            print(
                f"\n\nSession string will saved as {session_txt}, Also you can copy {session} to session dir if need.\nNever share this to anyone!"
            )
            open(session_txt, "w").write(str(session))

        asyncio.get_event_loop().run_until_complete(start_app())
    else:
        if create_bot == 1:
            app = pyrogram.Client(
                "my", api_id=api_id, api_hash=app_hash, phone_number=phone_number
            )
            session = "my.session"
            session_txt = "my.txt"
        elif create_bot == 2:
            bot_token = input("Insert bot token: ")
            app = pyrogram.Client(
                "bot",
                api_id=api_id,
                api_hash=app_hash,
                bot_token=bot_token,
                phone_number=phone_number,
            )
            session = "bot.session"
            session_txt = "bot.txt"

        with app as generation:  # noqa
            session = generation.export_session_string()
            print(f"Done!\nYour session string is:\n\n{session}")
            print(
                f"\n\nSession string will saved as {session_txt}, Also you can copy {session} to session dir if need.\nNever share this to anyone!"
            )
            open(session_txt, "w").write(str(session))
    print("\n\nDo you want to create again with same API?")
    ask = input("[Y/N] ")
    if ask.lower() == "y":
        initial_selection(api_id, app_hash)


fill_api()
