import aiosqlite
import asyncio

DB_NAME = "test_async.db"

# --- Setup database (only run once) ---
async def setup_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                name TEXT,
                age INTEGER
            )
        """)
        await db.executemany("INSERT INTO users (name, age) VALUES (?, ?)", [
            ("Alice", 25),
            ("Bob", 42),
            ("Charlie", 38),
            ("David", 50)
        ])
        await db.commit()

# --- Async query functions ---
async def async_fetch_users():
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT * FROM users") as cursor:
            users = await cursor.fetchall()
            print("All Users:")
            for user in users:
                print(user)
            #return
async def async_fetch_older_users():
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT * FROM users WHERE age > 40") as cursor:
            older_users = await cursor.fetchall()
            print("\nUsers older than 40:")
            for user in older_users:
                print(user)
            #return
# --- Run both queries concurrently ---
async def fetch_concurrently():
    await asyncio.gather(
        async_fetch_users(),
        async_fetch_older_users()
    )

# --- Entry Point ---
if __name__ == "__main__":
    asyncio.run(setup_db())          # Optional: Comment out after first run
    asyncio.run(fetch_concurrently())
