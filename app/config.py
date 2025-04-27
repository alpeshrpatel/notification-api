import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    """Application settings configuration"""
    
    # App settings
    APP_NAME: str = os.getenv("APP_NAME", "Email Service API")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    
    # # AWS settings
    AWS_ACCESS_KEY_ID: str = os.getenv("AWS_ACCESS_KEY_ID", "")
    AWS_SECRET_ACCESS_KEY: str = os.getenv("AWS_SECRET_ACCESS_KEY", "")
    AWS_REGION: str = os.getenv("AWS_REGION", "us-east-1")
    
    # # API security
    # API_KEY: str = os.getenv("API_KEY", "your_secure_api_key")

    # Database settings
    DB_USERNAME: str = os.getenv("DB_USERNAME")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD")
    DB_SERVER: str = os.getenv("DB_SERVER")
    DB_NAME: str = os.getenv("DB_NAME")
    DB_PORT: str = os.getenv("DB_PORT")
    
    class Config:
        env_file = ".env"

# Create settings instance
settings = Settings()