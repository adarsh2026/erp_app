CREATE TABLE IF NOT EXISTS uoms (
    uom_id        SERIAL PRIMARY KEY,
    uom_name      VARCHAR(100) UNIQUE NOT NULL,
    uom_symbol    VARCHAR(10),
    created_at     TIMESTAMP    NOT NULL DEFAULT NOW()
);