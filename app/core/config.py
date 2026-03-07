from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import Optional

class Settings(BaseSettings):
    # API Configuration
    PROJECT_NAME: str = "AI Chat Service"
    API_V1_STR: str = "/api/v1"
    
    # OpenAI Configuration
    OPENAI_API_KEY: Optional[str] = Field(None, env="OPENAI_API_KEY")
    AGENT_MODEL: str = "gpt-4o-mini"
    EVAL_MODEL: str = "gpt-4o-mini" # Faster/Cheaper for evals
    
    # Database Configuration
    DATABASE_URL: str = Field("sqlite+aiosqlite:///./chat.db", env="DATABASE_URL")
    CHROMA_DB_PATH: str = Field("./.db/chroma", env="CHROMA_DB_PATH")
    DOCS_DIR: str = Field("./docs", env="DOCS_DIR")
    
    # App Persona (Stored centrally for easy updates)
    AGENT_PERSONA: str = (
        "Today is {current_date}. "
        "You are a technical assistant for the VCAPTECH assignment. "
        "You have access to the repository documentation via the search_docs tool and the internet via search_web. "
        "When asked about project requirements, tech stack, or event types, "
        "ALWAYS use the search_docs tool first. "
        "IMPORTANT: When you use tools (search_docs or search_web), you MUST provide citations in your response. "
        "Use the format [Source Name] to cite specific facts retrieved from tools."
    )

    # Pydantic-settings configuration
    model_config = SettingsConfigDict(
        env_file=".env", 
        case_sensitive=True,
        extra="ignore"
    )

settings = Settings()
