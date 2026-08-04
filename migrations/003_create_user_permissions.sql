CREATE TABLE IF NOT EXISTS user_permissions (
    permission_id  SERIAL PRIMARY KEY,
    user_id        INTEGER      NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    module_name    VARCHAR(30)  NOT NULL,
    UNIQUE(user_id, module_name)
);

CREATE INDEX IF NOT EXISTS idx_user_permissions_user_id
    ON user_permissions (user_id);