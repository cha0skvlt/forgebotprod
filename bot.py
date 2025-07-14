import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums.parse_mode import ParseMode
from dotenv import load_dotenv
import os

from modules import db
from modules.register import router as register_router
from modules.admin import router as admin_router
from modules.helpers import log_startup

load_dotenv()
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("bot")

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is not set")

bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

dp.include_routers(register_router, admin_router)


async def main():
    await db.connect()
    log_startup()
    await dp.start_polling(bot)
    await db.close()

if __name__ == "__main__":
    asyncio.run(main())
