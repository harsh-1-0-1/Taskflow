def get_board_with_columns(conn, board_id):
    board = conn.execute("SELECT * FROM boards WHERE id = ?", (board_id,)).fetchone()
    if board is None:
        return None
    columns = conn.execute(
        """
        SELECT *
        FROM columns
        WHERE board_id = ?
        ORDER BY position
        """,
        (board_id,),
    ).fetchall()
    return {"board": board, "columns": columns}
