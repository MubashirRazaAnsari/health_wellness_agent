import asyncio
from typing import Dict, Any
import os
from dotenv import load_dotenv

from agent import HealthWellnessAgent
from context import UserSessionContext
from hooks import RunHooks, AgentHooks
from utils.streaming import StreamHandler

# Load environment variables
load_dotenv()

async def main():
    """Initialize and run the Health & Wellness Planner Agent."""
    try:
        # Initialize the agent with hooks
        agent = HealthWellnessAgent(
            config_path="config/agent_config.json",
            run_hooks=RunHooks(),
            agent_hooks=AgentHooks("MainAgent")
        )

        # Initialize user context
        context = UserSessionContext(
            name="TestUser",
            uid=1234
        )

        # Initialize stream handler
        stream_handler = StreamHandler()

        print("🤖 Health & Wellness Planner Agent initialized!")
        print("Type 'quit' to exit")

        while True:
            user_input = input("\nYou: ")
            if user_input.lower() == 'quit':
                break

            # Process user input with streaming
            async for response_chunk in stream_handler.stream_response(
                agent=agent,
                user_input=user_input,
                context=context
            ):
                # Print response chunks in real-time
                print(f"Assistant: {response_chunk}", end="", flush=True)
            print()  # New line after response
    except Exception as e:
        print(f"Error running agent: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(main()) 