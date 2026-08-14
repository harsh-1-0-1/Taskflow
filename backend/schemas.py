from typing import Optional

from pydantic import BaseModel


class TaskCreate(BaseModel):
    column_id: int
    title: str
    description: Optional[str] = None
    priority: Optional[str] = "Medium"


class TaskUpdate(BaseModel):
    title: str
    description: Optional[str] = None
    priority: Optional[str] = "Medium"


class MoveTask(BaseModel):
    column_id: int


class TaskOut(BaseModel):
    id: int
    column_id: int
    title: str
    description: Optional[str] = None
    priority: str
    created_at: str
