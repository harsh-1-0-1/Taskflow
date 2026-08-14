def get_task_counts_by_column(conn, board_id):
    """Query 1: number of tasks per column on a board."""
    return conn.execute(
        """
        SELECT c.id, c.name, COUNT(t.id) AS task_count
        FROM columns c
        LEFT JOIN tasks t ON t.column_id = c.id
        WHERE c.board_id = %s
        GROUP BY c.id, c.name
        ORDER BY c.position
        """,
        (board_id,),
    ).fetchall()
