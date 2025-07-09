import asyncio
from agent import HealthWellnessAgent

async def main():
    # Initialize the agent
    agent = HealthWellnessAgent()
    await agent.initialize_session("TestUser", 1)

    # Example conversation flow
    messages = [
        "My goal is to lose 5kg in 2 months",
        "I'd like a meal plan please",
        "Can you give me a workout plan?",
        "I have knee pain when doing squats",
        "I'm diabetic and need diet advice"
    ]

    # Process each message
    for message in messages:
        print(f"\nUser: {message}")
        response = await agent.handle_message(message)
        print(f"Agent: {response['message']}")
        if "plan" in response:
            print("Plan details:", response["plan"])

if __name__ == "__main__":
    asyncio.run(main()) 