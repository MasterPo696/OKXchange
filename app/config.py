from pydantic_settings import BaseSettings


# Загружаем переменные окружения из .env файла
class Settings(BaseSettings):
    # Memcache 
    MEMCACHE_HOST: str
    MEMCACHE_PORT: int

    # URLs
    OKX_API_URL: str = "https://www.okx.com/api/v5/public/instruments"
    WS_URL: str = "wss://ws.okx.com:8443/ws/v5/public"

    class Config:
        env_file = ".env"  # Указываем, что настройки загружаются из файла .env

settings = Settings()
