# TaskFlow — Kanban Board

A minimal kanban board: FastAPI + SQLite on the backend, React (Vite) on the frontend.

## Setup

### Backend (port 8000)

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

- API runs at `http://localhost:8000`
- Interactive docs at `http://localhost:8000/docs` (free from FastAPI)
- The database (`taskflow.db`) is created and seeded automatically on first
  startup (1 board, 3 columns, 7 sample tasks).

### Frontend (port 5173)

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`.

Because the two run on different ports, the backend enables CORS for
`http://localhost:5173` via `CORSMiddleware` in `backend/main.py`.

## Tests

```bash
cd backend
.venv/bin/python -m pytest tests -v
```

Tests use an in-memory SQLite database — they never touch `taskflow.db`.

## API

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/boards/1` | board + columns + tasks (initial load) |
| GET | `/api/boards/1/tasks?priority=High` | tasks filtered by priority, newest first |
| GET | `/api/boards/1/columns/counts` | task count per column |
| POST | `/api/tasks` | create a task |
| PUT | `/api/tasks/:id` | edit title/description/priority |
| PUT | `/api/tasks/:id/move` | move a task to another column |
| DELETE | `/api/tasks/:id` | delete a task |

## Database schema

See [`backend/schema.sql`](backend/schema.sql). Three tables:

```sql
CREATE TABLE boards (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    name       TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE columns (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    board_id   INTEGER NOT NULL,
    name       TEXT NOT NULL,
    position   INTEGER NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (board_id) REFERENCES boards(id)
);

CREATE TABLE tasks (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    column_id   INTEGER NOT NULL,
    title       TEXT NOT NULL,
    description TEXT,
    priority    TEXT NOT NULL DEFAULT 'Medium'
                CHECK (priority IN ('Low','Medium','High')),
    created_at  TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (column_id) REFERENCES columns(id)
);
```

## The two non-trivial queries

Defined as named functions in the repository layer:

**1. Task count per column** (`repositories/column_repository.py`):

```sql
SELECT c.id, c.name, COUNT(t.id) AS task_count
FROM columns c
LEFT JOIN tasks t ON t.column_id = c.id
WHERE c.board_id = ?
GROUP BY c.id, c.name
ORDER BY c.position;
```

**2. Tasks by priority, newest first** (`repositories/task_repository.py`):

```sql
SELECT t.*
FROM tasks t
JOIN columns c ON c.id = t.column_id
WHERE c.board_id = ? AND t.priority = ?
ORDER BY t.created_at DESC;
```

Priority filtering happens server-side in SQL — the frontend calls
`/api/boards/1/tasks?priority=High` rather than filtering fetched data.

## Architecture

Repository → Service → Router. Each layer has one job:

| Layer | Knows about | Must NOT do |
|---|---|---|
| **Repository** | Raw SQL only | Validation, HTTP |
| **Service** | Business rules (blank title, valid priority) | SQL, request/response |
| **Router** | HTTP in/out, calls the service | SQL, business logic |

Validation ("title can't be blank", "priority must be Low/Medium/High") lives
in the service layer so every caller is protected by the same rule.

## Assumptions

- Single board, single team (multi-user/team is out of scope per the spec).
  The app always shows board `id = 1`.
- A task's *status* is which column it's in (`column_id`) — there is no
  separate status field, so the two can never drift out of sync.
- `priority` is a `TEXT CHECK` constraint, not a `priorities` table —
  three fixed values that never change.
- Task moving uses a "Move to" dropdown (the spec says a working dropdown
  beats a broken drag-and-drop); drag-and-drop is a stretch goal.
- Blank-titled tasks are rejected server-side with HTTP 400.

## What I'd add with more time

- Real drag-and-drop
- Search across tasks
- Auth + multiple boards/users
- Edit-in-place on cards instead of a modal

## Time spent

Roughly 4–5 hours including setup, verification, and this README.

## One thing I learned

Turning "status" into just `column_id` made moving a task a single
`UPDATE tasks SET column_id = ?` — removing a whole class of bugs where a
status string and a column disagree. Merging related concepts that can't
meaningfully diverge is usually simpler than modeling them separately.
# Taskflow
