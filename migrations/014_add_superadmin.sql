INSERT INTO roles (role_name)
VALUES ('superadmin')
ON CONFLICT (role_name) DO NOTHING;

ALTER TABLE users ADD COLUMN IF NOT EXISTS created_by INTEGER REFERENCES users(user_id) ON DELETE SET NULL;