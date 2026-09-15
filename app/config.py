import os

class Config:
    PORT = int(os.environ.get("PORT", 10000))
    TEMP_DIR = os.environ.get("TEMP_DIR", "/tmp/ytmp3")
    MAX_CONCURRENT_DOWNLOADS = int(os.environ.get("MAX_CONCURRENT_DOWNLOADS", 1))
    CLEANUP_AGE_SECONDS = int(os.environ.get("CLEANUP_AGE_SECONDS", 1800))  # 30 minutes
    CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "*").split(",")

config = Config()
