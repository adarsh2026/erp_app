CREATE TABLE IF NOT EXISTS product_master (
    product_master_id     SERIAL PRIMARY KEY,
    master_product_name   VARCHAR(150) NOT NULL,
    product_category_id   INTEGER REFERENCES product_categories(product_category_id) ON DELETE SET NULL,
    uom_id                 INTEGER REFERENCES uoms(uom_id) ON DELETE SET NULL,
    created_at              TIMESTAMP    NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_product_master_category ON product_master (product_category_id);
CREATE INDEX IF NOT EXISTS idx_product_master_uom      ON product_master (uom_id);