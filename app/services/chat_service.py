import uuid
import json
import asyncio
from typing import AsyncGenerator
from agents import Agent, Runner

from app.core.config import settings
from app.models.chat import MessageRole

class ChatService:
    def __init__(self):
        """
        Initialize the OpenAI Agent with its persona and model.
        These are centralized in app/core/config.py for easy updates.
        """
        self.agent = Agent(
            name="Assistant",
            instructions=settings.AGENT_PERSONA,
            model=settings.AGENT_MODEL
        )

    # Note: Phase 1 only initializes. Phase 2 will implement stream_chat.
    def get_agent(self) -> Agent:
        return self.agent

# Global instance for use in dependency injection or direct calls
chat_service = ChatService()
