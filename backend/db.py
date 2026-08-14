import os
import sqlite3

from fastapi import Depends

DB_PATH = os.path.join(os.path.dirname(__file__), "taskflow.db")
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "schema.sql")


def init_db():
    conn = sqlite3.connect(DB_PATH)
    try:
        with open(SCHEMA_PATH) as f:
            conn.executescript(f.read())
        conn.commit()
    finally:
        conn.close()


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()
