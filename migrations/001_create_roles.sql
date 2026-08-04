CREATE TABLE IF NOT EXISTS roles (
    role_id     SERIAL PRIMARY KEY,
    role_name   VARCHAR(30) UNIQUE NOT NULL
);

INSERT INTO roles (role_name)
VALUES ('admin'), ('user')
ON CONFLICT (role_name) DO NOTHING;
