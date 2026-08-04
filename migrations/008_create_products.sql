CREATE TABLE IF NOT EXISTS products (
    product_id     SERIAL PRIMARY KEY,
    product_name   VARCHAR(150) NOT NULL,
    product_code   VARCHAR(30)  UNIQUE,
    created_at      TIMESTAMP    NOT NULL DEFAULT NOW()
);