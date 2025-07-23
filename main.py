import asyncio
from agent import HealthWellnessAgent
from context import UserSessionContext
import json

async def main():
    agent = HealthWellnessAgent()
    context = UserSessionContext(name="TestUser", uid=1234)
    print("🤖 Health & Wellness Planner Agent initialized!")
    print("Type 'quit' to exit")
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() == 'quit':
            break
        response = await agent.run(user_input, context)
        # Print as JSON if possible
        try:
            print("Assistant:", json.dumps(response, indent=2))
        except Exception:
            print("Assistant:", response)

if __name__ == "__main__":
    asyncio.run(main()) 