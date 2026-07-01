from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")
    
    ENV: str = "development"
    
    # Default database points to PostgreSQL for both local development and production.
    # SQLite is used strictly within the Pytest unit testing environment (see tests/conftest.py).
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/tickets"
    
    # Secret key required for API header authentication
    API_KEY: str

    # Comma-separated list of allowed CORS origins
    CORS_ORIGINS: str = "*"


    @property
    def sqlalchemy_database_url(self) -> str:
        # SQLAlchemy 2.0 requires postgresql:// instead of postgres://
        url = self.DATABASE_URL
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql://", 1)
        return url

settings = Settings()
