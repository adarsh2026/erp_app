CREATE TABLE IF NOT EXISTS departments (
    department_id    SERIAL PRIMARY KEY,
    department_name  VARCHAR(100) UNIQUE NOT NULL,
    created_at        TIMESTAMP    NOT NULL DEFAULT NOW()
);