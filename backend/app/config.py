from pydantic_settings import BaseSettings
from pydantic import Field, model_validator
from functools import lru_cache


class Settings(BaseSettings):
    ENV_MODE: str = Field(default="dev", description="dev / staging / prod")
    APP_NAME: str = "MedScribe AI"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False

    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 8000

    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "medscribe"
    DB_USER: str = "medscribe"
    DB_PASSWORD: str = "changeme_db_password"
    DATABASE_URL: str = ""

    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = ""
    REDIS_URL: str = ""

    JWT_SECRET: str = "changeme_jwt_secret_at_least_32_chars"
    JWT_ACCESS_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_EXPIRE_DAYS: int = 7
    JWT_ALGORITHM: str = "HS256"   # HS256 or RS256
    JWT_PRIVATE_KEY: str = ""      # RSA private key PEM (required when JWT_ALGORITHM=RS256)
    JWT_PUBLIC_KEY: str = ""       # RSA public key PEM  (required when JWT_ALGORITHM=RS256)

    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = "http://localhost/api/auth/google/callback"
    GOOGLE_CALENDAR_REDIRECT_URI: str = "http://localhost:8000/api/appointments/calendar/callback"

    S3_ENDPOINT: str = "http://localhost:9000"
    S3_PUBLIC_ENDPOINT: str = "http://localhost:9000"
    S3_ACCESS_KEY: str = "minioadmin"
    S3_SECRET_KEY: str = "changeme_minio_password"
    S3_BUCKET: str = "medscribe-audio"
    S3_REGION: str = "us-east-1"

    WHISPER_API_URL: str = "https://api.openai.com/v1/audio/transcriptions"
    WHISPER_API_KEY: str = ""
    WHISPER_MODEL: str = "whisper-1"

    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4.1"

    MEILISEARCH_URL: str = "http://localhost:7700"
    MEILISEARCH_KEY: str = ""

    ENCRYPTION_KEY: str = "changeme_32_byte_hex_key_here_00"

    SENTRY_DSN: str = ""

    PARENT_WEBSITE_URL: str = "http://localhost:3001"

    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:80,http://localhost:3001"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}

    _WEAK_DEFAULTS: set = {
        "changeme_jwt_secret_at_least_32_chars",
        "changeme_32_byte_hex_key_here_00",
        "changeme_minio_password",
        "changeme_db_password",
    }

    @model_validator(mode="after")
    def validate_prod_secrets(self) -> "Settings":
        if self.ENV_MODE != "prod":
            return self
        checks = {
            "JWT_SECRET": self.JWT_SECRET,
            "ENCRYPTION_KEY": self.ENCRYPTION_KEY,
            "S3_SECRET_KEY": self.S3_SECRET_KEY,
            "DB_PASSWORD": self.DB_PASSWORD,
        }
        for name, value in checks.items():
            if value in self._WEAK_DEFAULTS:
                raise ValueError(
                    f"SECURITY ERROR: {name} is using a default/weak value in production. "
                    f"Set a strong secret in .env before starting."
                )
        return self

    @property
    def db_url(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def redis_url_computed(self) -> str:
        if self.REDIS_URL:
            return self.REDIS_URL
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/0"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/0"

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

    @property
    def is_dev(self) -> bool:
        return self.ENV_MODE == "dev"

    @property
    def is_prod(self) -> bool:
        return self.ENV_MODE == "prod"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
