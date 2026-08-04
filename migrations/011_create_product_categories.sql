CREATE TABLE IF NOT EXISTS product_categories (
    product_category_id    SERIAL PRIMARY KEY,
    category_name           VARCHAR(100) UNIQUE NOT NULL,
    created_at               TIMESTAMP    NOT NULL DEFAULT NOW()
);