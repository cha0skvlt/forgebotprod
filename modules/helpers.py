from modules.db import get_cursor, commit
import os

OWNER_ID = int(os.getenv("OWNER_ID", "0"))

def is_admin(user_id: int) -> bool:
    with get_cursor() as cursor:
        cursor.execute("SELECT 1 FROM admins WHERE tg_id = %s", (user_id,))
        return cursor.fetchone() is not None

def is_owner(user_id: int) -> bool:
    return user_id == OWNER_ID
