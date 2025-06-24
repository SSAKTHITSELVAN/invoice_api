class Settings:
    SECRET_KEY: str = "your-super-secret-jwt-key-change-in-production-123456789"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

settings = Settings()