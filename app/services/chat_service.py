import uuid
import json
import asyncio
import time
from typing import AsyncGenerator, Dict, Any, List
from agents import Agent, Runner
from openai.types.responses import ResponseTextDeltaEvent

from app.core.config import settings
from app.models.chat import MessageRole

class AssistantContent:
    """Simple class to track content across generator execution."""
    def __init__(self):
        self.content = ""

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
        session_id: uuid.UUID,
        content_tracker: AssistantContent
    ) -> AsyncGenerator[str, None]:
        """
        Orchestrates the SSE stream including heartbeats and deltas.
        Updates content_tracker.content as it goes.
        """
        full_assistant_content: List[str] = []
        
        result = Runner.run_streamed(self.agent, input=message)
        event_iterator = result.stream_events().__aiter__()

        last_event_time = asyncio.get_event_loop().time()
        heartbeat_interval = 15.0

        is_done = False
        while not is_done:
            try:
                time_to_heartbeat = heartbeat_interval - (asyncio.get_event_loop().time() - last_event_time)
                
                try:
                    event = await asyncio.wait_for(event_iterator.__anext__(), timeout=max(0.1, time_to_heartbeat))
                    
                    if event.type == "raw_response_event" and hasattr(event.data, "delta"):
                        delta_text = event.data.delta
                        full_assistant_content.append(delta_text)
                        # Update the tracker shared with the caller
                        content_tracker.content = "".join(full_assistant_content)
                        
                        last_event_time = asyncio.get_event_loop().time()
                        yield self._format_sse("agent.message.delta", {"text": delta_text})
                
                except asyncio.TimeoutError:
                    last_event_time = asyncio.get_event_loop().time()
                    yield self._format_sse("heartbeat", {"timestamp": int(time.time())})
                
                except StopAsyncIteration:
                    is_done = True
                    yield self._format_sse("agent.message.done", {"session_id": str(session_id)})

            except Exception as e:
                is_done = True
                yield self._format_sse("agent.workflow.failed", {"error": str(e)})
                raise e

chat_service = ChatService()
