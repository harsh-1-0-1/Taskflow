from repositories import task_repository

VALID_PRIORITIES = ("Low", "Medium", "High")


class TaskValidationError(ValueError):
    pass


def create_task(conn, column_id, title, description=None, priority="Medium"):
    if not title or not title.strip():
        raise TaskValidationError("Title is required and cannot be blank")
    if priority is None:
        priority = "Medium"
    if priority not in VALID_PRIORITIES:
        raise TaskValidationError(
            f"Priority must be one of {', '.join(VALID_PRIORITIES)}"
        )
    return task_repository.insert_task(
        conn, column_id, title.strip(), description, priority
    )


def update_task(conn, task_id, title, description=None, priority="Medium"):
    existing = task_repository.get_task(conn, task_id)
    if existing is None:
        raise TaskValidationError("Task not found")
    if not title or not title.strip():
        raise TaskValidationError("Title is required and cannot be blank")
    if priority not in VALID_PRIORITIES:
        raise TaskValidationError(
            f"Priority must be one of {', '.join(VALID_PRIORITIES)}"
        )
    task_repository.update_task(
        conn, task_id, title.strip(), description, priority
    )


def move_task(conn, task_id, column_id):
    task = task_repository.get_task(conn, task_id)
    if task is None:
        raise TaskValidationError("Task not found")
    task_repository.move_task(conn, task_id, column_id)


def delete_task(conn, task_id):
    task = task_repository.get_task(conn, task_id)
    if task is None:
        raise TaskValidationError("Task not found")
    task_repository.delete_task(conn, task_id)


def get_tasks_by_priority(conn, board_id, priority):
    if priority not in VALID_PRIORITIES:
        raise TaskValidationError(
            f"Priority must be one of {', '.join(VALID_PRIORITIES)}"
        )
    return task_repository.get_tasks_by_priority(conn, board_id, priority)
