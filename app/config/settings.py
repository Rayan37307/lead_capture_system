from pydantic_settings import BaseSettings
from typing import List, Optional


class Settings(BaseSettings):
    # App settings
    PROJECT_NAME: str = "AI Lead Capture & Automation System"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = False

    # Database settings
    MONGODB_URL: str
    MONGODB_DB_NAME: str = "lead_capture_db"
    
    # Google Sheets settings
    GOOGLE_SHEETS_SYNC: bool = False
    GOOGLE_SHEETS_CREDENTIALS_FILE: Optional[str] = None
    GOOGLE_SHEETS_SPREADSHEET_ID: Optional[str] = None

    # AI settings
    AI_PROVIDER: str = "gemini"  # openai, openrouter, gemini
    OPENAI_API_KEY: Optional[str] = None
    OPENROUTER_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    AI_MODEL: str = "gemini-2.5-flash"

    # WhatsApp settings
    WHATSAPP_WEBHOOK_VERIFY_TOKEN: str
    WHATSAPP_ACCESS_TOKEN: str
    WHATSAPP_PHONE_NUMBER_ID: str
    TWILIO_ACCOUNT_SID: Optional[str] = None
    TWILIO_AUTH_TOKEN: Optional[str] = None
    TWILIO_PHONE_NUMBER: Optional[str] = None

    # Instagram settings
    INSTAGRAM_WEBHOOK_VERIFY_TOKEN: str
    INSTAGRAM_ACCESS_TOKEN: str

    # Facebook Messenger settings
    FB_PAGE_ACCESS_TOKEN: str
    FB_APP_SECRET: str
    FB_WEBHOOK_VERIFY_TOKEN: str

    # Notification settings
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    NOTIFICATION_EMAILS: List[str] = []
    ADMIN_WHATSAPP_NUMBER: Optional[str] = None

    # Security settings
    API_KEY: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Allowed origins for CORS
    ALLOWED_ORIGINS: List[str] = ["*"]

    class Config:
        env_file = ".env"


settings = Settings()