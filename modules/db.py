import psycopg2
import os
from contextlib import contextmanager

conn = None

def init():
    global conn
    conn = psycopg2.connect(os.getenv("DATABASE_URL"))

@contextmanager
def get_cursor():
    cursor = conn.cursor()
    try:
        yield cursor
    finally:
        cursor.close()

def commit():
    conn.commit()
