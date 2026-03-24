from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Database (Prisma)
    DATABASE_URL: str

    # Clerk Auth
    CLERK_SECRET_KEY: str
    CLERK_WEBHOOK_SECRET: str
    CLERK_ISSUER_URL: str  # Format: https://<your-clerk-domain>.clerk.accounts.dev

    # Cloudflare R2
    R2_ACCOUNT_ID: str
    R2_ACCESS_KEY_ID: str
    R2_SECRET_ACCESS_KEY: str
    R2_BUCKET_NAME: str

    # AI Model
    ANTHROPIC_API_KEY: str

    # Loads from a local .env file
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

# Instantiate once to be imported across the application
settings = Settings()