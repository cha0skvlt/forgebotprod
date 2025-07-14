from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart
from modules import db
import logging
import os

router = Router()
log = logging.getLogger("register")

@router.message(CommandStart())
async def register_user(message: Message) -> None:
    tg_id = message.from_user.id
    guest = await db.fetchrow("SELECT id FROM guests WHERE tg_id=$1", tg_id)
    if guest:
        guest_id = guest["id"]
        await db.execute("INSERT INTO visits(guest_id) VALUES($1)", guest_id)
        log.info("Visit logged for guest %s", guest_id)
    else:
        guest_id = await db.fetchrow(
            "INSERT INTO guests(tg_id) VALUES($1) RETURNING id", tg_id
        )
        await db.execute("INSERT INTO visits(guest_id) VALUES($1)", guest_id["id"])
        log.info("New guest %s registered", guest_id["id"])

    await message.answer("✅ Вы зарегистрированы, добро пожаловать!")

    channel = os.getenv("CHANNEL_USERNAME")
    if channel:
        try:
            await message.bot.send_message(
                chat_id=channel,
                text=f"📥 Новый гость: @{message.from_user.username or tg_id}"
            )
        except Exception as e:
            log.warning("Failed to notify channel: %s", e)
