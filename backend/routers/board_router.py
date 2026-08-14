from fastapi import APIRouter, Depends

from db import get_db
from repositories import board_repository, column_repository, task_repository
from schemas import TaskOut

router = APIRouter(prefix="/api")


@router.get("/boards/{board_id}")
def get_board(board_id: int, conn=Depends(get_db)):
    result = board_repository.get_board_with_columns(conn, board_id)
    if result is None:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Board not found")
    board = result["board"]
    columns = []
    for col in result["columns"]:
        columns.append(
            {
                "id": col["id"],
                "name": col["name"],
                "position": col["position"],
                "tasks": [
                    TaskOut(**dict(t)).model_dump()
                    for t in task_repository.get_tasks_by_column(conn, col["id"])
                ],
            }
        )
    return {"id": board["id"], "name": board["name"], "columns": columns}


@router.get("/boards/{board_id}/columns/counts")
def column_counts(board_id: int, conn=Depends(get_db)):
    rows = column_repository.get_task_counts_by_column(conn, board_id)
    return [{"id": r["id"], "name": r["name"], "task_count": r["task_count"]} for r in rows]
