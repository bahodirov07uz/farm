from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import text
import asyncio

async def migrate_branches():
    engine = create_async_engine("sqlite+aiosqlite:///med.db", echo=True)

    async with engine.begin() as conn:
        # 1. Jadvalni rename qilish
        await conn.execute(text("ALTER TABLE branches RENAME TO old_branches;"))

        # 2. Yangi jadvalni yaratish
        await conn.execute(text("""
        CREATE TABLE branches (
            id INTEGER PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            address VARCHAR(500),
            phone VARCHAR(50),
            pharmacy_id INTEGER NOT NULL REFERENCES pharmacies(id) ON DELETE CASCADE,
            longitude VARCHAR(255),
            latitude VARCHAR(255)
        )
        """))

        # 3. Ma'lumotlarni ko'chirish
        await conn.execute(text("""
        INSERT INTO branches (id, name, address, phone, pharmacy_id, longitude, latitude)
        SELECT id, name, address, phone, pharmacy_id, longitude, latitude
        FROM old_branches
        """))

        # 4. Eski jadvalni o'chirish
        await conn.execute(text("DROP TABLE old_branches;"))

asyncio.run(migrate_branches())
