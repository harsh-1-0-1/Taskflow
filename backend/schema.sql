CREATE TABLE IF NOT EXISTS boards (
    id         SERIAL PRIMARY KEY,
    name       TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS columns (
    id         SERIAL PRIMARY KEY,
    board_id   INTEGER NOT NULL,
    name       TEXT NOT NULL,
    position   INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    FOREIGN KEY (board_id) REFERENCES boards(id)
);

CREATE TABLE IF NOT EXISTS tasks (
    id          SERIAL PRIMARY KEY,
    column_id   INTEGER NOT NULL,
    title       TEXT NOT NULL,
    description TEXT,
    priority    TEXT NOT NULL DEFAULT 'Medium'
                CHECK (priority IN ('Low','Medium','High')),
    created_at  TIMESTAMP NOT NULL DEFAULT NOW(),
    FOREIGN KEY (column_id) REFERENCES columns(id)
);
