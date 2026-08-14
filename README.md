# TaskFlow — Kanban Board

A minimal kanban board: FastAPI + Postgres on the backend, React (Vite) on the frontend.

## Run the whole stack with Docker (easiest)

Requires Docker + Docker Compose. Starts Postgres, the FastAPI backend, and the
Vite frontend together:

```bash
docker compose up -d --build
```

- Frontend: `http://localhost:5173`
- Backend: `http://localhost:8000` (docs at `/docs`)
- Postgres: `localhost:5435` (`taskflow` / `taskflow`, db `taskflow`)

The backend applies the schema and seeds sample data on first start
(`IF NOT EXISTS` tables, empty-board check). Data lives in the named volume
`taskflow-pgdata`, so it survives container restarts.

To run just the database (e.g. for local development outside Docker):

```bash
docker compose up -d db        # exposes Postgres on localhost:5435
```

## Setup (running the parts directly)

### 1. Create a Postgres database

The backend talks to Postgres via a `DATABASE_URL` connection string (e.g. the
Internal Database URL from a free Render Postgres instance). There's no
persistent disk on Render's free web service, so the database is hosted
externally. Locally, `docker compose up -d db` provides a Postgres on
`localhost:5435`.

### 2. Backend (port 8000)

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Set the connection string. Either export it, or copy `.env.example` to `.env`
(it's loaded automatically):

```bash
export DATABASE_URL=postgresql://USER:PASSWORD@HOST:PORT/DATABASE
# or: cp .env.example .env   then edit DATABASE_URL in .env
```

Load the schema and seed data once, before the first run:

```bash
psql "$DATABASE_URL" -f schema.sql
python seed.py
```

Then start the server:

```bash
uvicorn main:app --reload
```

- API runs at `http://localhost:8000`
- Interactive docs at `http://localhost:8000/docs` (free from FastAPI)
- The schema is also applied automatically on startup (tables are created with
  `IF NOT EXISTS`); `seed.py` only inserts data if the boards table is empty
  (1 board, 3 columns, 7 sample tasks).

### Frontend (port 5173)

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`.

Because the two run on different ports, the backend enables CORS for
`http://localhost:5173` via `CORSMiddleware` in `backend/main.py`.

## Deployment

### Backend on Render

1. Create a Render **Postgres** instance and note its Internal Database URL.
2. Create a Render **Web Service** from this repo (root folder is fine —
   `render.yaml` is included). Set these environment variables:
   - `DATABASE_URL` — the Postgres Internal Database URL
   - `CORS_ORIGINS` — comma-separated list of frontend origins, e.g.
     `https://taskflow.vercel.app`
3. Load schema + seed once against the Render DB:
   ```bash
   psql "$DATABASE_URL" -f schema.sql
   python seed.py
   ```
   (tables are also created on startup with `IF NOT EXISTS`, so step 3's first
   command is belt-and-suspenders.)
4. Deploy. The start command (`uvicorn main:app --host 0.0.0.0 --port $PORT`)
   uses Render's injected `$PORT`.

Connection pooling: `get_db()` in `backend/db.py` hands out connections from a
`ThreadedConnectionPool` (max size configurable via `DB_POOL_MAX`) and rolls
back + returns them on request end, so every HTTP request doesn't open a fresh
TCP connection.

### Frontend on Vercel

1. Import the repo in Vercel (it auto-detects Vite: build `npm run build`,
   output `dist`).
2. Set one environment variable:
   - `VITE_API_URL` — the deployed backend URL, e.g. `https://taskflow-backend.onrender.com`
3. Deploy. `vercel.json` rewrites all routes to `index.html`.

The frontend reads `VITE_API_URL` at build time (`src/api/client.js`), falling
back to `http://localhost:8000` locally — see `frontend/.env.example`.

## Tests

```bash
cd backend
.venv/bin/python -m pytest tests -v
```

Tests run against a real Postgres instance (via `DATABASE_URL`), using a
dedicated `test_taskflow` schema that is dropped and recreated for every test —
they never touch your real data.

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
    id         SERIAL PRIMARY KEY,
    name       TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE columns (
    id         SERIAL PRIMARY KEY,
    board_id   INTEGER NOT NULL,
    name       TEXT NOT NULL,
    position   INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    FOREIGN KEY (board_id) REFERENCES boards(id)
);

CREATE TABLE tasks (
    id          SERIAL PRIMARY KEY,
    column_id   INTEGER NOT NULL,
    title       TEXT NOT NULL,
    description TEXT,
    priority    TEXT NOT NULL DEFAULT 'Medium'
                CHECK (priority IN ('Low','Medium','High')),
    created_at  TIMESTAMP NOT NULL DEFAULT NOW(),
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
WHERE c.board_id = %s
GROUP BY c.id, c.name
ORDER BY c.position;
```

**2. Tasks by priority, newest first** (`repositories/task_repository.py`):

```sql
SELECT t.*
FROM tasks t
JOIN columns c ON c.id = t.column_id
WHERE c.board_id = %s AND t.priority = %s
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
- The backend originally used SQLite; it was swapped to Postgres so the app can
  be hosted on Render, whose free web service has no persistent disk. Only the
  connection layer and schema syntax changed — the repository/service/router
  architecture and the SQL logic are identical. Psycopg2 connections are
  wrapped with a sqlite3-style `.execute()` helper (`backend/db.py`) so call
  sites didn't change.

## What I'd add with more time

- Real drag-and-drop
- Search across tasks
- Auth + multiple boards/users
- Edit-in-place on cards instead of a modal

## Time spent

Roughly 4–5 hours including setup, verification, and this README.

## One thing I learned

Turning "status" into just `column_id` made moving a task a single
`UPDATE tasks SET column_id = %s` — removing a whole class of bugs where a
status string and a column disagree. Merging related concepts that can't
meaningfully diverge is usually simpler than modeling them separately.
