from dotenv import load_dotenv
import os
import redis

load_dotenv()

class Config():
    SECRET_KEY = os.getenv("APP_SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    
    SESSION_TYPE = os.getenv('SESSION_TYPE') or 'filesystem'
    SESSION_USE_SIGNER = True
    SESSION_PERMANENT = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    # SESSION_COOKIE_SECURE = True

    if SESSION_TYPE == 'redis':
        REDIS_URL = os.getenv("REDIS_URL")
        if not REDIS_URL:
            raise RuntimeError("REDIS_URL is required when SESSION_TYPE=redis")
        SESSION_REDIS = redis.from_url(REDIS_URL)