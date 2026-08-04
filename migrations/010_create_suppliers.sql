CREATE TABLE IF NOT EXISTS suppliers (
    supplier_id           SERIAL PRIMARY KEY,
    supplier_name         VARCHAR(150) NOT NULL,
    contact_person_name   VARCHAR(100),
    contact_phone         VARCHAR(15),
    created_at             TIMESTAMP    NOT NULL DEFAULT NOW()
);