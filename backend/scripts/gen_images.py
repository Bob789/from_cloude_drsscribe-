"""One-time script: generate hero images for all published articles that have none."""
import asyncio
import sys
sys.path.insert(0, '/app')

ARTICLES = [
    ('7011dea3-4398-4ec4-be85-85cd2b298faf', 'metabolic cardiac health balance over 40 lifestyle', 'general'),
    ('8e85b822-6f75-4fb7-be2b-2b6c04200802', 'blood glucose imbalance diabetes insulin management', 'nutrition'),
    ('34d96ba5-dd32-40d9-987d-25b163a670bd', 'cholesterol heart health LDL HDL blood lipids', 'cardiology'),
    ('f0d3ec8a-b065-402f-ae60-21e9ca1b5268', 'vitamin B12 deficiency neurological treatment', 'nutrition'),
    ('5b114e8d-11d9-44f5-9876-1c176b965b80', 'varicose veins legs swollen veins treatment', 'general'),
    ('6e9c7996-1773-470e-813d-d9bef85f7ec7', 'sleep disorders insomnia fatigue daily life', 'sleep'),
    ('178f0f58-9883-40bc-9b8f-6d68e2d4f514', 'sugar effects dental health teeth cavities', 'nutrition'),
    ('776f9073-d222-4f70-b282-8207ab3ceac1', 'chronic rhinitis nasal inflammation sinusitis treatment', 'general'),
    ('ac27ee2d-29c7-461a-a2d3-0bcec77b2474', 'blood pressure hypertension management cardiovascular', 'cardiology'),
    ('316bd155-3f7e-47eb-af79-4daaa6ecf264', 'IVF in vitro fertilization embryo fertility treatment', 'general'),
]

async def main():
    from app.database import get_db
    from app.models.article import Article
    from app.services.image_service import find_hero_image
    from sqlalchemy import select

    async for db in get_db():
        for article_id, topic, category in ARTICLES:
            print(f'[{ARTICLES.index((article_id, topic, category))+1}/{len(ARTICLES)}] {topic[:55]}')
            try:
                img = await find_hero_image(topic, category)
                if img:
                    article = (await db.execute(select(Article).where(Article.id == article_id))).scalars().first()
                    if article:
                        article.hero_image_url = img['url']
                        article.hero_image_alt = img.get('alt', topic)
                        await db.flush()
                        print(f'  OK: {img["url"][:80]}')
                    else:
                        print(f'  SKIP: article not found in DB')
                else:
                    print(f'  FAILED: no image returned')
            except Exception as e:
                print(f'  ERROR: {e}')
        await db.commit()
        print('\nAll done!')

asyncio.run(main())
