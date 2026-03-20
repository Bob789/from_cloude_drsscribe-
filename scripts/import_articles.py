import csv, json, io
import psycopg2
import os

# Read file and find real CSV header line
with open('/tmp/articles_export.csv', 'r', encoding='utf-8-sig') as f:
    content = f.read()

lines = content.split('\n')
start_idx = next(i for i, l in enumerate(lines) if l.strip().startswith('id,'))
csv_content = '\n'.join(lines[start_idx:])

reader = csv.DictReader(io.StringIO(csv_content))
rows = list(reader)
print(f'Found {len(rows)} articles to import')

db_url = os.environ.get('DATABASE_URL', '').replace('postgresql+asyncpg://', '')
# db_url = user:pass@host:port/dbname
import re
m = re.match(r'([^:]+):([^@]+)@([^:]+):(\d+)/(.+)', db_url)
conn = psycopg2.connect(
    host=m.group(3), port=int(m.group(4)),
    dbname=m.group(5), user=m.group(1), password=m.group(2)
)
cur = conn.cursor()

imported = 0
for row in rows:
    try:
        tags = row['tags'] if row['tags'] else '[]'
        published_at = row['created_at'] if row['status'] == 'published' else None
        cur.execute("""
            INSERT INTO articles (id, title, slug, status, category, summary,
                content_markdown, tags, author_name, read_time_minutes, views, likes,
                created_at, updated_at, published_at)
            VALUES (%s, %s, %s, %s::articlestatus, %s, %s, %s, %s::jsonb, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING
        """, (
            row['id'], row['title'], row['slug'], row['status'], row['category'],
            row['summary'], row['content_markdown'], tags, row['author_name'],
            int(row['read_time_minutes']), int(row['views']), int(row['likes']),
            row['created_at'], row['created_at'], published_at
        ))
        imported += 1
        print(f"  OK: {row['slug']}")
    except Exception as e:
        print(f"  ERR [{row.get('slug', '?')}]: {e}")
        conn.rollback()
        conn = psycopg2.connect(
            host=m.group(3), port=int(m.group(4)),
            dbname=m.group(5), user=m.group(1), password=m.group(2)
        )
        cur = conn.cursor()

conn.commit()
cur.close()
conn.close()
print(f'Done. Imported {imported}/{len(rows)} articles.')
