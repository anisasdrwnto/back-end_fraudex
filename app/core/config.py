from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import URL


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Cara 1: satu alamat penuh (dipakai di Render/Neon)
    DATABASE_URL: str = ""

    # Cara 2: terpisah (dipakai di laptop lo)
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_USER: str = "postgres"
    DB_PASSWORD: str = ""
    DB_NAME: str = "fraudex"

    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_MINUTES: int = 30
    REFRESH_TOKEN_DAYS: int = 7

    ADMIN_NAME: str = ""
    ADMIN_EMAIL: str = ""
    ADMIN_PASSWORD: str = ""

    CORS_ORIGINS: str = "http://localhost:3000"
    LOGIN_RATE_LIMIT: str = "10/minute"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

    @property
    def database_url(self) -> str | URL:
        if self.DATABASE_URL:
            url = self.DATABASE_URL
            # Neon memberi "postgresql://...", SQLAlchemy butuh "+psycopg" (driver psycopg 3)
            for prefix in ("postgresql://", "postgres://"):
                if url.startswith(prefix):
                    url = "postgresql+psycopg://" + url[len(prefix):]
            return url
        return URL.create(
            "postgresql+psycopg",
            username=self.DB_USER,
            password=self.DB_PASSWORD,
            host=self.DB_HOST,
            port=self.DB_PORT,
            database=self.DB_NAME,
        )


settings = Settings()