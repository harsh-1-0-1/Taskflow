def get_tasks_by_column(conn, column_id):
    return conn.execute(
        "SELECT * FROM tasks WHERE column_id = ? ORDER BY created_at DESC, id DESC",
        (column_id,),
    ).fetchall()


def get_tasks_by_board(conn, board_id):
    return conn.execute(
        """
        SELECT t.*
        FROM tasks t
        JOIN columns c ON c.id = t.column_id
        WHERE c.board_id = ?
        ORDER BY c.position, t.created_at DESC, t.id DESC
        """,
        (board_id,),
    ).fetchall()


def get_tasks_by_priority(conn, board_id, priority):
    """Query 2: tasks with a given priority on a board, newest first."""
    return conn.execute(
        """
        SELECT t.*
        FROM tasks t
        JOIN columns c ON c.id = t.column_id
        WHERE c.board_id = ? AND t.priority = ?
        ORDER BY t.created_at DESC, t.id DESC
        """,
        (board_id, priority),
    ).fetchall()


def get_task(conn, task_id):
    return conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()


def insert_task(conn, column_id, title, description, priority):
    cur = conn.execute(
        "INSERT INTO tasks (column_id, title, description, priority) VALUES (?, ?, ?, ?)",
        (column_id, title, description, priority),
    )
    conn.commit()
    return cur.lastrowid


def update_task(conn, task_id, title, description, priority):
    conn.execute(
        "UPDATE tasks SET title = ?, description = ?, priority = ? WHERE id = ?",
        (title, description, priority, task_id),
    )
    conn.commit()


def move_task(conn, task_id, column_id):
    conn.execute(
        "UPDATE tasks SET column_id = ? WHERE id = ?",
        (column_id, task_id),
    )
    conn.commit()


def delete_task(conn, task_id):
    conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
