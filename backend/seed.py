from db import connect, init_db


def seed_if_empty():
    init_db()
    conn = connect()
    try:
        has_boards = conn.execute("SELECT COUNT(*) AS n FROM boards").fetchone()["n"]
        if has_boards:
            return False
        conn.execute("INSERT INTO boards (name) VALUES (%s)", ("My Team Board",))
        board_id = 1
        columns = [
            ("To Do", 0),
            ("In Progress", 1),
            ("Done", 2),
        ]
        for name, position in columns:
            conn.execute(
                "INSERT INTO columns (board_id, name, position) VALUES (%s, %s, %s)",
                (board_id, name, position),
            )
        todo = conn.execute(
            "SELECT id FROM columns WHERE board_id = %s AND position = 0", (board_id,)
        ).fetchone()["id"]
        progress = conn.execute(
            "SELECT id FROM columns WHERE board_id = %s AND position = 1", (board_id,)
        ).fetchone()["id"]
        done = conn.execute(
            "SELECT id FROM columns WHERE board_id = %s AND position = 2", (board_id,)
        ).fetchone()["id"]

        tasks = [
            (todo, "Set up project skeleton", "Initialize repo, schema and config.", "Medium"),
            (todo, "Wire up database layer", "Implement repositories and queries.", "High"),
            (todo, "Write README", "Document setup, schema and queries.", "Low"),
            (progress, "Build the board API", "Endpoints for board, columns and tasks.", "High"),
            (progress, "Frontend board rendering", "Render columns and task cards.", "Medium"),
            (done, "Choose tech stack", "FastAPI + React + SQLite.", "Low"),
            (done, "Write the build plan", "Taskflow implementation plan.", "High"),
        ]
        for column_id, title, description, priority in tasks:
            conn.execute(
                "INSERT INTO tasks (column_id, title, description, priority) VALUES (%s, %s, %s, %s)",
                (column_id, title, description, priority),
            )
        conn.commit()
        return True
    finally:
        conn.close()


if __name__ == "__main__":
    created = seed_if_empty()
    print("Seeded database." if created else "Database already seeded.")
