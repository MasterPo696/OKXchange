from typing import Optional
from pydantic_settings import BaseSettings

# Храним все данные и окружение .env

class Settings:
    OKX_API_URL = "https://www.okx.com/api/v5/public/instruments"
    WS_URL = "wss://ws.okx.com:8443/ws/v5/public"

    REDIS_URL: str = "redis://redis:6379"
    # CACHE_TTL: int = 3600  # 1 hour
    

settings = Settings()
