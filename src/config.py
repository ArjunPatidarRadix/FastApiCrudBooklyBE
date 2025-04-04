from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str
    JWT_SECRET_KEY: str
    ALGORITHM: str
    REDIS_HOST: str = "redis://localhost"
    REDIS_PORT: int = 6379
    REDIS_URL: str
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_PORT: int
    MAIL_SERVER: str
    MAIL_FROM_NAME: str
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False
    USE_CREDENTIALS: bool = True
    VALIDATE_CERTS: bool = True
    DOMAIN: str

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


Config = Settings()
"""
To access the .env variables, you can use the Config object like this:
print(Config.DATABASE_URL)
"""

print("Config: %s" % Config.REDIS_URL)


# To start the celery server to send the emails in background worked
# celery -A src.celery_tasks.c_app worker --loglevel=INFO
# check src/celery_tasks.py for more information

broker_url = Config.REDIS_URL
result_backend = Config.REDIS_URL
broker_connection_retry_on_startup = True
