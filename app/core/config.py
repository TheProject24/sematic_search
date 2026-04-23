from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Existing fields
    DATABASE_URL: str
    SUPABASE_URL: str
    SUPABASE_SERVICE_KEY: str
    GROQ_API_KEY: str
    LOCAL_SECRET_KEY: str
    BUCKET_NAME: str

    # ADD THESE MISSING FIELDS:
    DATABASE_URL_DEV: str | None = None  # Optional, so it doesn't break if missing
    SUPABASE_KEY: str                    # This matches your SUPABASE_KEY in .env
    SUPABASE_JWT_SECRET: str             # This matches your JWT secret in .env
    OPENAI_API_KEY: str | None = None    # Optional, fallback to GROQ_API_KEY if needed

    model_config = SettingsConfigDict(env_file=".env", extra="ignore") # 👈 THE MAGIC LINE

settings = Settings()