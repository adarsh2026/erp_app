CREATE TABLE IF NOT EXISTS sessions (
    session_id     SERIAL PRIMARY KEY,
    session_name   VARCHAR(150) UNIQUE NOT NULL,
    start_date     DATE         NOT NULL,
    end_date       DATE         NOT NULL,
    created_at      TIMESTAMP    NOT NULL DEFAULT NOW()
);