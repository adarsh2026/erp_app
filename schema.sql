CREATE TABLE IF NOT EXISTS roles (
    role_id     SERIAL PRIMARY KEY,
    role_name   VARCHAR(30) UNIQUE NOT NULL
);

INSERT INTO roles (role_name)
VALUES ('admin'), ('user')
ON CONFLICT (role_name) DO NOTHING;

CREATE TABLE IF NOT EXISTS users (
    user_id       SERIAL PRIMARY KEY,
    username      VARCHAR(50)  UNIQUE NOT NULL,
    password_hash VARCHAR(100) NOT NULL,
    full_name     VARCHAR(100) NOT NULL,
    role_id       INTEGER      NOT NULL REFERENCES roles(role_id),
    is_active     BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at    TIMESTAMP    NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS user_permissions (
    permission_id  SERIAL PRIMARY KEY,
    user_id        INTEGER      NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    module_name    VARCHAR(30)  NOT NULL,
    UNIQUE(user_id, module_name)
);

CREATE INDEX IF NOT EXISTS idx_user_permissions_user_id
    ON user_permissions (user_id);

CREATE TABLE IF NOT EXISTS departments (
    department_id    SERIAL PRIMARY KEY,
    department_name  VARCHAR(100) UNIQUE NOT NULL,
    created_at        TIMESTAMP    NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS factories (
    factory_id        SERIAL PRIMARY KEY,
    factory_name      VARCHAR(100) UNIQUE NOT NULL,
    factory_location  VARCHAR(150),
    created_at         TIMESTAMP    NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS sessions (
    session_id     SERIAL PRIMARY KEY,
    session_name   VARCHAR(150) UNIQUE NOT NULL,
    start_date     DATE         NOT NULL,
    end_date       DATE         NOT NULL,
    created_at      TIMESTAMP    NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS stores (
    store_id        SERIAL PRIMARY KEY,
    store_name      VARCHAR(100) UNIQUE NOT NULL,
    store_location  VARCHAR(150),
    created_at       TIMESTAMP    NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS products (
    product_id     SERIAL PRIMARY KEY,
    product_name   VARCHAR(150) NOT NULL,
    product_code   VARCHAR(30)  UNIQUE,
    created_at      TIMESTAMP    NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS uoms (
    uom_id        SERIAL PRIMARY KEY,
    uom_name      VARCHAR(100) UNIQUE NOT NULL,
    uom_symbol    VARCHAR(10),
    created_at     TIMESTAMP    NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS suppliers (
    supplier_id           SERIAL PRIMARY KEY,
    supplier_name         VARCHAR(150) NOT NULL,
    contact_person_name   VARCHAR(100),
    contact_phone         VARCHAR(15),
    created_at             TIMESTAMP    NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS product_categories (
    product_category_id    SERIAL PRIMARY KEY,
    category_name           VARCHAR(100) UNIQUE NOT NULL,
    created_at               TIMESTAMP    NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS product_master (
    product_master_id     SERIAL PRIMARY KEY,
    master_product_name   VARCHAR(150) NOT NULL,
    product_category_id   INTEGER REFERENCES product_categories(product_category_id) ON DELETE SET NULL,
    uom_id                 INTEGER REFERENCES uoms(uom_id) ON DELETE SET NULL,
    created_at              TIMESTAMP    NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_product_master_category ON product_master (product_category_id);
CREATE INDEX IF NOT EXISTS idx_product_master_uom      ON product_master (uom_id);