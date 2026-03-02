import uuid
import json
import asyncio
import time
from typing import AsyncGenerator, Dict, Any
from agents import Agent, Runner
from openai.types.responses import ResponseTextDeltaEvent

from app.core.config import settings
from app.models.chat import MessageRole

class ChatService:
    def __init__(self):
        """Initialize the OpenAI Agent with its persona and model."""
        self.agent = Agent(
            name="Assistant",
            instructions=settings.AGENT_PERSONA,
            model=settings.AGENT_MODEL
        )

    def _format_sse(self, event: str, data: Dict[Any, Any]) -> str:
        """Helper to format SSE wire format: event: name\ndata: JSON\n\n"""
        return f"event: {event}\ndata: {json.dumps(data)}\n\n"

    async def stream_chat(
        self, 
        message: str,
        session_id: uuid.UUID
    ) -> AsyncGenerator[str, None]:
        """
        Orchestrates the SSE stream including:
        1. Agent deltas (agent.message.delta)
        2. Done event (agent.message.done)
        3. Error handling (agent.workflow.failed)
        4. Heartbeat every 15s
        
        Returns the full response content as the final yielding value or via side-effect.
        """
        full_assistant_content = []
        
        # We wrap the agent stream in a task so we can race it against a heartbeat timer
        result = Runner.run_streamed(self.agent, input=message)
        event_iterator = result.stream_events().__aiter__()

        # Track the last time we sent ANY event (chunk or heartbeat)
        last_event_time = asyncio.get_event_loop().time()
        heartbeat_interval = 15.0

        is_done = False
        while not is_done:
            try:
                # Calculate how long until the next heartbeat
                time_to_heartbeat = heartbeat_interval - (asyncio.get_event_loop().time() - last_event_time)
                
                # Race the next AI event against the heartbeat timeout
                try:
                    event = await asyncio.wait_for(event_iterator.__anext__(), timeout=max(0.1, time_to_heartbeat))
                    
                    # 1. Handle raw token deltas
                    if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
                        delta_text = event.data.delta
                        full_assistant_content.append(delta_text)
                        last_event_time = asyncio.get_event_loop().time()
                        yield self._format_sse("agent.message.delta", {"text": delta_text})
                
                except asyncio.TimeoutError:
                    # 2. Heartbeat triggered if no AI event within interval
                    last_event_time = asyncio.get_event_loop().time()
                    yield self._format_sse("heartbeat", {"timestamp": int(time.time())})
                
                except StopAsyncIteration:
                    # 3. AI Stream successfully finished
                    is_done = True
                    yield self._format_sse("agent.message.done", {"session_id": str(session_id)})
                    # Save the full content to a shared state or return it 
                    # (In Commit 11 we will handle the DB persistence wrap-around)
                    self._last_full_content = "".join(full_assistant_content)

            except Exception as e:
                # 4. Handle unexpected failures
                is_done = True
                yield self._format_sse("agent.workflow.failed", {"error": str(e)})
                raise e

    def get_last_full_content(self) -> str:
        """Retrieves the full content from the most recent stream."""
        return getattr(self, "_last_full_content", "")

chat_service = ChatService()
