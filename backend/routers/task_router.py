from fastapi import APIRouter, Depends, HTTPException

from db import get_db
from repositories import task_repository
from schemas import MoveTask, TaskCreate, TaskOut, TaskUpdate
from services import task_service

router = APIRouter(prefix="/api")


def _task_out(row) -> TaskOut:
    return TaskOut(**dict(row))


@router.get("/boards/{board_id}/tasks", response_model=list[TaskOut])
def list_tasks(board_id: int, priority: str = None, conn=Depends(get_db)):
    if priority is not None:
        try:
            rows = task_service.get_tasks_by_priority(conn, board_id, priority)
        except task_service.TaskValidationError as e:
            raise HTTPException(status_code=400, detail=str(e))
        return [_task_out(r) for r in rows]
    rows = task_repository.get_tasks_by_board(conn, board_id)
    return [_task_out(r) for r in rows]


@router.post("/tasks", response_model=TaskOut, status_code=201)
def create_task(payload: TaskCreate, conn=Depends(get_db)):
    try:
        task_id = task_service.create_task(
            conn, payload.column_id, payload.title, payload.description, payload.priority
        )
    except task_service.TaskValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return _task_out(task_repository.get_task(conn, task_id))


@router.put("/tasks/{task_id}", response_model=TaskOut)
def update_task(task_id: int, payload: TaskUpdate, conn=Depends(get_db)):
    try:
        task_service.update_task(
            conn, task_id, payload.title, payload.description, payload.priority
        )
    except task_service.TaskValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return _task_out(task_repository.get_task(conn, task_id))


@router.put("/tasks/{task_id}/move", response_model=TaskOut)
def move_task(task_id: int, payload: MoveTask, conn=Depends(get_db)):
    try:
        task_service.move_task(conn, task_id, payload.column_id)
    except task_service.TaskValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return _task_out(task_repository.get_task(conn, task_id))


@router.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int, conn=Depends(get_db)):
    try:
        task_service.delete_task(conn, task_id)
    except task_service.TaskValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
