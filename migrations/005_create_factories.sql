CREATE TABLE IF NOT EXISTS factories (
    factory_id        SERIAL PRIMARY KEY,
    factory_name      VARCHAR(100) UNIQUE NOT NULL,
    factory_location  VARCHAR(150),
    created_at         TIMESTAMP    NOT NULL DEFAULT NOW()
);