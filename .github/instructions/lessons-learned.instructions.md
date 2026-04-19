---
description: "Use when debugging errors, fixing bugs, troubleshooting deployment issues, or investigating unexpected behavior. Contains lessons learned from past issues."
---
# Lessons Learned & Common Fixes

## Database
- **"relation does not exist"**: Models not imported in `app/models/__init__.py` → Alembic can't see them → migration is empty. Fix: add import, regenerate migration.
- **Migration fails**: Always run with `PYTHONPATH=/app` inside Docker.

## Google Auth
- **Sign-In popup blocked**: Missing `Cross-Origin-Opener-Policy: same-origin-allow-popups` header in nginx.conf.
- **Redirect URI mismatch**: `GOOGLE_REDIRECT_URI` in `.env` must match actual frontend port (localhost:3000 for dev).
- **Token leaks in console**: GSI library prints tokens via `[GSI_LOGGER-TOKEN_CLIENT]`. Fixed by console interceptor in `web/index.html`.

## Images
- **Google profile image CORS error**: `Image.network` with `headers` parameter triggers XHR instead of `<img>` tag → CORS failure. Fix: remove `headers`, set `Referrer-Policy` in nginx instead.
- **Google profile image 429**: Google CDN rejects requests with referrer. Fix: `add_header Referrer-Policy "no-referrer"` in nginx.conf.

## Frontend Build
- **Changes to `index.html` not visible**: Requires full `docker-compose build frontend` — hot reload doesn't apply to static web files.
- **`*.lock` in gitignore**: This blocks `pubspec.lock` which should be committed. Use specific ignore patterns instead.

## Security
- Never add `headers` with tokens to `Image.network` — they appear in network tab
- GSI logger filter must cover all 5 console methods: log, warn, error, debug, info
- `docs/` and `private/` directories are gitignored — contain sensitive deployment info
- Patient data queries must always filter by `doctor_id` / `created_by`
- **NEVER use SQL ILIKE/LIKE on encrypted columns** — encrypted data is base64 ciphertext, text matching will never work. Always decrypt in memory first, then filter in Python.
- **Every query returning encrypted fields to API must decrypt before response** — use `decrypt_patient_pii()`, `decrypt_summary_fields()`, `decrypt_transcription_fields()`
- **Every query involving Visit/Patient/Summary MUST filter by doctor_id** — check all new endpoints and service functions
- **Tags have no doctor_id column** — isolation requires JOIN: Tag → Summary → Visit → filter `Visit.doctor_id`
- Full troubleshooting log with detection methods: `docs/troubleshooting.md`

## nginx
- **`proxy_pass` עם משתנה ($var) + URI suffix חותך את שאר הנתיב**: כאשר `proxy_pass` מכיל משתנה (`set $upstream ...`) וגם URI suffix (כגון `/drscribe-audio/`), nginx **לא** מחליף את ה-location prefix — הוא שולח רק את ה-suffix לבד, ללא שאר הנתיב. MinIO מקבל `/drscribe-audio/` בלבד ומחזיר `AccessDenied` (list bucket).
  - **שגיאה**: `proxy_pass $minio_upstream/drscribe-audio/;` → MinIO מקבל `/drscribe-audio/` בלי שם הקובץ
  - **תיקון**: להפריד בין rewrite לבין proxy_pass:
    ```nginx
    set $minio_upstream http://minio:9000;   # חייב לפני rewrite
    rewrite ^/media/(.*)$ /drscribe-audio/$1 break;
    proxy_pass $minio_upstream;              # בלי URI suffix
    ```
  - **סדר חשוב**: `set` חייב לבוא לפני `rewrite ... break`, אחרת המשתנה לא מוגדר.

## MinIO
- **MinIO InvalidAccessKeyId**: Credentials mismatch between `.env` and `docker-compose.yml`.
- **403 על קבצי מדיה (article-images)**: MinIO bucket פרטי כברירת מחדל — anonymous read חסום. תיקון: `mc anonymous set download local/<bucket>/article-images`
- **Policies סותרים ב-MinIO**: `article-images/*` (none) + `article-images*` (readonly) — הספציפי יותר מנצח וחוסם. תמיד בדוק `mc anonymous list` לפני דיבוג nginx. ניקוי: `mc anonymous set none .../article-images/` ואז `mc anonymous set download .../article-images`
- **`minio-init` service**: הוסף לdocker-compose.prod.yml כ-service נפרד עם `image: minio/mc` שרץ פעם אחת אחרי MinIO ומגדיר policies אוטומטית. מחייב healthcheck על service ה-minio.

## General
- **500 on endpoints**: First check if the DB table exists (`\dt` in psql), then check model imports in `__init__.py`.
- **SQLAlchemy async MissingGreenlet**: גישה לattribute של מודל אחרי `db.commit()` גורמת לשגיאה כי session נסגר. תמיד לשמור snapshot של הנתונים (`result = build_response(obj)`) לפני ה-commit.
