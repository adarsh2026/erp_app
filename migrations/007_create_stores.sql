CREATE TABLE IF NOT EXISTS stores (
    store_id        SERIAL PRIMARY KEY,
    store_name      VARCHAR(100) UNIQUE NOT NULL,
    store_location  VARCHAR(150),
    created_at       TIMESTAMP    NOT NULL DEFAULT NOW()
);