import asyncio
import bcrypt

from db import create_pool

SUPERADMIN_USERNAME = "superadmin"
SUPERADMIN_PASSWORD = "super123"
SUPERADMIN_FULL_NAME = "Super Administrator"

USERNAME = "admin"
PASSWORD = "admin123"
FULL_NAME = "Administrator"

TEST_USERNAME = "staff"
TEST_PASSWORD = "staff123"
TEST_FULL_NAME = "Staff User"


async def create_user(conn, username, password, full_name, role_name, created_by=None):
    existing = await conn.fetchrow("SELECT user_id FROM users WHERE username = $1", username)
    if existing:
        print(f"'{username}' Skipp")
        return existing["user_id"]

    role_row = await conn.fetchrow("SELECT role_id FROM roles WHERE role_name = $1", role_name)
    if not role_row:
        print(f"Role '{role_name}' not found in roles table — skipping {username}")
        return None

    password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    row = await conn.fetchrow(
        "INSERT INTO users (username, password_hash, full_name, role_id, created_by) "
        "VALUES ($1, $2, $3, $4, $5) RETURNING user_id",
        username, password_hash, full_name, role_row["role_id"], created_by,
    )
    print(f"User Created -> username: {username} | password: {password} | role: {role_name}")
    return row["user_id"]


async def seed():
    pool = await create_pool()

    async with pool.acquire() as conn:
        superadmin_id = await create_user(
            conn, SUPERADMIN_USERNAME, SUPERADMIN_PASSWORD, SUPERADMIN_FULL_NAME, "superadmin"
        )
        admin_id = await create_user(
            conn, USERNAME, PASSWORD, FULL_NAME, "admin", created_by=superadmin_id
        )
        await create_user(
            conn, TEST_USERNAME, TEST_PASSWORD, TEST_FULL_NAME, "user", created_by=admin_id
        )

    await pool.close()

if __name__ == "__main__":
    asyncio.run(seed())