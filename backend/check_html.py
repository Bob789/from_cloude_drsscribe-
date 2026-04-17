import asyncio
from app.database import AsyncSessionLocal
from sqlalchemy import text

async def main():
    async with AsyncSessionLocal() as db:
        r = await db.execute(text("SELECT slug, LEFT(content_html, 1500) FROM articles WHERE status='published' ORDER BY slug"))
        for row in r.fetchall():
            print(f"\n=== {row[0]} ===")
            print(row[1] if row[1] else "NO HTML")

asyncio.run(main())
