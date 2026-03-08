import aiosqlite
import os
import config

DB_NAME = "database.db"

async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                phone_number TEXT NOT NULL,
                session_string TEXT,
                UNIQUE(user_id, phone_number)
            )
        ''')
        await db.commit()

async def reset_db():
    # Remove all pyrogram sessions
    for filename in os.listdir(config.SESSION_DIR):
        file_path = os.path.join(config.SESSION_DIR, filename)
        if os.path.isfile(file_path):
            try:
                os.remove(file_path)
            except:
                pass
                
    # Recreate table
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('DROP TABLE IF EXISTS accounts')
        await db.commit()
    await init_db()

async def add_account(user_id: int, phone_number: str):
    async with aiosqlite.connect(DB_NAME) as db:
        try:
            await db.execute('INSERT INTO accounts (user_id, phone_number) VALUES (?, ?)', (user_id, phone_number))
            await db.commit()
            return True
        except aiosqlite.IntegrityError:
            return False

async def get_accounts(user_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT phone_number FROM accounts WHERE user_id = ?', (user_id,)) as cursor:
            rows = await cursor.fetchall()
            return [row[0] for row in rows]

async def get_account_session(phone_number: str):
    # phone is unique enough for the file session mapping, but we might want to check user_id too later
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT session_string FROM accounts WHERE phone_number = ?', (phone_number,)) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else None

async def update_account_session(user_id: int, phone_number: str, session_string: str):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('UPDATE accounts SET session_string = ? WHERE user_id = ? AND phone_number = ?', (session_string, user_id, phone_number))
        await db.commit()

async def delete_account(user_id: int, phone_number: str):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('DELETE FROM accounts WHERE user_id = ? AND phone_number = ?', (user_id, phone_number))
        await db.commit()
