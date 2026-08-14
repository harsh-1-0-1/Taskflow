import os

import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

load_dotenv()

SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "schema.sql")


class Connection(psycopg2.extensions.connection):
    """psycopg2 connection with a sqlite3-style .execute() convenience method.

    Keeps the repository/service/seed call sites unchanged (`conn.execute(sql,
    params)` returns a cursor), so swapping SQLite for Postgres stays a
    one-file change.
    """

    def execute(self, *args, **kwargs):
        cur = self.cursor()
        try:
            cur.execute(*args, **kwargs)
        except Exception:
            cur.close()
            raise
        return cur


def connect():
    return psycopg2.connect(
        os.environ["DATABASE_URL"],
        connection_factory=Connection,
        cursor_factory=psycopg2.extras.RealDictCursor,
    )


def init_db():
    conn = connect()
    try:
        with open(SCHEMA_PATH) as f:
            schema = f.read()
        conn.execute(schema)
        conn.commit()
    finally:
        conn.close()


def get_db():
    conn = connect()
    try:
        yield conn
    finally:
        conn.close()
