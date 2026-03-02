from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import Optional

class Settings(BaseSettings):
    # API Configuration
    PROJECT_NAME: str = "AI Chat Service"
    API_V1_STR: str = "/api/v1"
    
    # OpenAI Configuration
    # We use Field(..., env="...") to explicitly link to env vars
    OPENAI_API_KEY: Optional[str] = Field(None, env="OPENAI_API_KEY")
    AGENT_MODEL: str = "gpt-4o-mini"
    
    # Database Configuration
    DATABASE_URL: str = Field("postgresql+asyncpg://postgres:postgres@db:5432/chat_db", env="DATABASE_URL")
    
    # App Persona (Stored centrally for easy updates)
    AGENT_PERSONA: str = (
        "You are a helpful and concise AI assistant. "
        "Your goal is to provide clear and accurate information to the user."
    )

    # Pydantic-settings configuration
    model_config = SettingsConfigDict(
        env_file=".env", 
        case_sensitive=True,
        extra="ignore"
    )

settings = Settings()
