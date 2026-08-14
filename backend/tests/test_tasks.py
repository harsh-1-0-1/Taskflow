import pytest

from db import SCHEMA_PATH, connect
from repositories import task_repository
from services import task_service

TEST_SCHEMA = "test_taskflow"


@pytest.fixture
def conn():
    conn = connect()
    try:
        conn.execute(f"DROP SCHEMA IF EXISTS {TEST_SCHEMA} CASCADE")
        conn.execute(f"CREATE SCHEMA {TEST_SCHEMA}")
        conn.execute(f"SET search_path TO {TEST_SCHEMA}")
        with open(SCHEMA_PATH) as f:
            conn.execute(f.read())
        conn.commit()
        yield conn
    finally:
        conn.close()


@pytest.fixture
def seeded(conn):
    conn.execute("INSERT INTO boards (name) VALUES (%s)", ("Test Board",))
    for name, position in (("To Do", 0), ("Done", 1)):
        conn.execute(
            "INSERT INTO columns (board_id, name, position) VALUES (1, %s, %s)",
            (name, position),
        )
    conn.commit()
    return conn


def test_create_task_without_title_fails(seeded):
    with pytest.raises(ValueError):
        task_service.create_task(seeded, column_id=1, title="   ")
    with pytest.raises(ValueError):
        task_service.create_task(seeded, column_id=1, title="")


def test_move_task_updates_column(seeded):
    task_id = task_service.create_task(
        seeded, column_id=1, title="My task", priority="High"
    )
    task_service.move_task(seeded, task_id, column_id=2)
    moved = task_repository.get_task(seeded, task_id)
    assert moved["column_id"] == 2


def test_tasks_by_priority_query_returns_right_rows(seeded):
    seeded.execute(
        "INSERT INTO tasks (column_id, title, priority, created_at) "
        "VALUES (1, 'Old high', 'High', '2026-01-01 09:00:00')"
    )
    seeded.execute(
        "INSERT INTO tasks (column_id, title, priority, created_at) "
        "VALUES (1, 'New high', 'High', '2026-01-03 09:00:00')"
    )
    seeded.execute(
        "INSERT INTO tasks (column_id, title, priority, created_at) "
        "VALUES (1, 'Medium task', 'Medium', '2026-01-02 09:00:00')"
    )
    seeded.execute(
        "INSERT INTO tasks (column_id, title, priority, created_at) "
        "VALUES (2, 'Done high', 'High', '2026-01-01 10:00:00')"
    )
    seeded.commit()

    rows = task_service.get_tasks_by_priority(seeded, board_id=1, priority="High")
    titles = [r["title"] for r in rows]
    assert titles == ["New high", "Done high", "Old high"]
    assert "Medium task" not in titles
