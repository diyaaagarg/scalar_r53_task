from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_prefix="ROUTE53_", extra="ignore"
    )
    database_url: str = "sqlite:///./route53.db"
    session_secret: str = "development-secret-change-me"
    cors_origins: str = "http://localhost:3010"
    secure_cookies: bool = False
    cookie_samesite: str = "lax"
    session_days: int = 7

    @property
    def cors_origin_list(self) -> list[str]:
        return [
            origin.strip() for origin in self.cors_origins.split(",") if origin.strip()
        ]

    @property
    def cookie_samesite_value(self) -> str:
        """Return a Starlette-compatible SameSite value from environment config."""
        value = self.cookie_samesite.lower()
        if value not in {"lax", "strict", "none"}:
            return "lax"
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()
