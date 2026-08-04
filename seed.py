import asyncio
import bcrypt

from db import create_pool

USERNAME = "admin"
PASSWORD = "admin123"
FULL_NAME = "Administrator"

TEST_USERNAME = "staff"
TEST_PASSWORD = "staff123"
TEST_FULL_NAME = "Staff User"


async def create_user(conn, username, password, full_name, role_name):
    existing = await conn.fetchrow("SELECT user_id FROM users WHERE username = $1", username)
    if existing:
        print(f"'{username}' Skipp")
        return

    role_row = await conn.fetchrow("SELECT role_id FROM roles WHERE role_name = $1", role_name)
    if not role_row:
        print(f"Role '{role_name}' not found in roles table — skipping {username}")
        return

    password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    await conn.execute(
        "INSERT INTO users (username, password_hash, full_name, role_id) "
        "VALUES ($1, $2, $3, $4)",
        username, password_hash, full_name, role_row["role_id"],
    )
    print(f"User Created -> username: {username} | password: {password} | role: {role_name}")


async def seed():
    pool = await create_pool()

    async with pool.acquire() as conn:
        await create_user(conn, USERNAME, PASSWORD, FULL_NAME, "admin")
        await create_user(conn, TEST_USERNAME, TEST_PASSWORD, TEST_FULL_NAME, "user")

    await pool.close()

if __name__ == "__main__":
    asyncio.run(seed())