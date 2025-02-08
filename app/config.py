# Храним все данные и окружение .env
class Settings:
    
    OKX_API_URL = "https://www.okx.com/api/v5/public/instruments"
    WS_URL = "wss://ws.okx.com:8443/ws/v5/public"

    MEMCACHE_HOST = 'localhost'  
    MEMCACHE_PORT = 11211 

settings = Settings()
