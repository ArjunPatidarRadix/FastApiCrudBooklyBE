from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str
    JWT_SECRET_KEY: str
    ALGORITHM: str
    REDIS_HOST: str = "redis://localhost"
    REDIS_PORT: int = 6379

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


Config = Settings()
"""
To access the .env variables, you can use the Config object like this:
print(Config.DATABASE_URL)
"""
