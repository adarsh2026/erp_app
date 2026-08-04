import os
import asyncpg

# Local (development) defaults — used only if DATABASE_URL is not set
DB_HOST = "localhost"
DB_PORT = 5432
DB_NAME = "erp_db"
DB_USER = "postgres"
DB_PASSWORD = "Admin123"

# On Render, this environment variable will be set to your PostgreSQL connection URL
DATABASE_URL = os.environ.get("DATABASE_URL")


async def create_pool():
    if DATABASE_URL:
        # Running on Render (or any host with DATABASE_URL set)
        pool = await asyncpg.create_pool(
            dsn=DATABASE_URL,
            min_size=2,
            max_size=10,
            ssl="require",
        )
    else:
        # Running locally
        pool = await asyncpg.create_pool(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            min_size=2,
            max_size=10,
        )
    return pool