import asyncpg
DB_HOST = "localhost"
DB_PORT = 5432
DB_NAME = "erp_db"
DB_USER = "postgres"
DB_PASSWORD = "Admin123"
async def create_pool():
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

