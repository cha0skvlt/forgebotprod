from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from modules import db
from modules.helpers import get_env
import logging

router = Router()
log = logging.getLogger("admin")

def _owner_only(func):
    async def wrapper(message: Message, *args, **kwargs):
        owner_id = int(get_env("OWNER_ID", required=True))
        if message.from_user and message.from_user.id == owner_id:
            return await func(message, *args, **kwargs)
        await message.answer("🚫 Access denied.")
    return wrapper

def _admin_only(func):
    async def wrapper(message: Message, *args, **kwargs):
        uid = message.from_user.id if message.from_user else 0
        owner_id = int(get_env("OWNER_ID", required=True))
        if uid == owner_id:
            return await func(message, *args, **kwargs)
        row = await db.fetchrow("SELECT 1 FROM admins WHERE user_id=$1", uid)
        if row:
            return await func(message, *args, **kwargs)
        await message.answer("🚫 Access denied.")
    return wrapper

@router.message(Command("reg"))
@_admin_only
async def manual_reg(message: Message) -> None:
    parts = message.text.split(maxsplit=1)
    if len(parts) != 2:
        await message.answer("❗ Usage: /reg ФИО, телефон, ДР")
        return
    try:
        full_name, phone, birthdate = [x.strip() for x in parts[1].split(",")]
    except ValueError:
        await message.answer("❗ Format: ФИО, телефон, дата_рождения")
        return
    guest_id = await db.fetchrow(
        "INSERT INTO guests(full_name, phone, birthdate) VALUES($1, $2, $3) RETURNING id",
        full_name, phone, birthdate
    )
    await db.execute("INSERT INTO visits(guest_id) VALUES($1)", guest_id["id"])
    await message.answer("✅ Гость зарегистрирован")

@router.message(Command("report"))
@_admin_only
async def report(message: Message) -> None:
    guests = await db.fetchrow("SELECT COUNT(*) AS count FROM guests")
    visits = await db.fetchrow("SELECT COUNT(*) AS count FROM visits")
    await message.answer(f"👥 Гостей: {guests['count']}, визитов: {visits['count']}")

@router.message(Command("search_guest"))
@_admin_only
async def search_guest(message: Message) -> None:
    parts = message.text.split(maxsplit=1)
    if len(parts) != 2:
        await message.answer("❗ Usage: /search_guest Иванов or +7912...")
        return
    query = parts[1]
    rows = await db.fetch(
        "SELECT full_name, phone, birthdate FROM guests WHERE full_name ILIKE $1 OR phone ILIKE $1",
        f"%{query}%"
    )
    if not rows:
        await message.answer("❌ Не найдено.")
        return
    text = "\n".join([f"{r['full_name']} — {r['phone']} ({r['birthdate']})" for r in rows])
    await message.answer(text)

@router.message(Command("add_admin"))
@_owner_only
async def add_admin(message: Message) -> None:
    parts = message.text.split()
    if len(parts) != 2:
        await message.answer("Usage: /add_admin <user_id>")
        return
    try:
        uid = int(parts[1])
    except ValueError:
        await message.answer("Invalid user ID")
        return
    await db.execute(
        "INSERT INTO admins(user_id) VALUES($1) ON CONFLICT DO NOTHING", uid
    )
    log.info("Added admin %s", uid)
    await message.answer(f"Added admin {uid}")

@router.message(Command("rm_admin"))
@_owner_only
async def rm_admin(message: Message) -> None:
    parts = message.text.split()
    if len(parts) != 2:
        await message.answer("Usage: /rm_admin <user_id>")
        return
    try:
        uid = int(parts[1])
    except ValueError:
        await message.answer("Invalid user ID")
        return
    await db.execute("DELETE FROM admins WHERE user_id=$1", uid)
    log.info("Removed admin %s", uid)
    await message.answer(f"Removed admin {uid}")

@router.message(Command("list_admin"))
@_admin_only
async def list_admin(message: Message) -> None:
    rows = await db.fetch("SELECT user_id FROM admins")
    admins = [str(r["user_id"]) for r in rows]
    text = ", ".join(admins) if admins else "No admins."
    log.info("Listed admins: %s", text)
    await message.answer(text)
