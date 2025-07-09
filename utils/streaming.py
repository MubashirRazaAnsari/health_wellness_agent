from typing import AsyncGenerator, Dict, Any
from context import UserSessionContext

class StreamingManager:
    """Manages real-time streaming of agent responses."""

    @staticmethod
    async def stream_response(response: Dict[str, Any]) -> AsyncGenerator[str, None]:
        """
        Streams a response dictionary word by word.
        
        Args:
            response: Response dictionary to stream
            
        Yields:
            Words from the response
        """
        if "message" in response:
            words = response["message"].split()
            for word in words:
                yield word + " "
                # In real implementation, add small delay here

    @staticmethod
    async def stream_plan(plan: Dict[str, Any]) -> AsyncGenerator[str, None]:
        """
        Streams a plan dictionary section by section.
        
        Args:
            plan: Plan dictionary to stream
            
        Yields:
            Sections of the plan
        """
        for key, value in plan.items():
            if isinstance(value, list):
                yield f"\n{key}:\n"
                for item in value:
                    yield f"- {item}\n"
            elif isinstance(value, dict):
                yield f"\n{key}:\n"
                for sub_key, sub_value in value.items():
                    yield f"  {sub_key}: {sub_value}\n"
            else:
                yield f"\n{key}: {value}\n"

class Runner:
    """Handles streaming of agent interactions."""

    @staticmethod
    async def stream(starting_agent: Any, input: str, context: UserSessionContext) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Streams the entire agent interaction process.
        
        Args:
            starting_agent: Initial agent to handle the request
            input: User input
            context: User session context
            
        Yields:
            Steps of the interaction process
        """
        # Start processing
        yield {"type": "start", "message": "Processing your request..."}

        # Get agent response
        response = await starting_agent.handle_message(input)

        # Stream the response
        async for chunk in StreamingManager.stream_response(response):
            yield {"type": "message", "chunk": chunk}

        # If there's a plan, stream it
        if "plan" in response:
            async for chunk in StreamingManager.stream_plan(response["plan"]):
                yield {"type": "plan", "chunk": chunk}

        # End processing
        yield {"type": "end", "message": "Response complete"} 