import asyncio
import sys
from typing import Optional
import questionary
from agent import HealthWellnessAgent
from utils.streaming import Runner

class HealthAgentCLI:
    def __init__(self):
        self.agent = HealthWellnessAgent()
        self.user_name: Optional[str] = None
        self.user_id: Optional[int] = None

    async def setup_user(self):
        """Collect initial user information."""
        print("\n🏋️‍♂️ Welcome to Health & Wellness Planner! 🥗\n")
        
        self.user_name = await questionary.text(
            "What's your name?",
            validate=lambda text: len(text) >= 2 or "Name must be at least 2 characters"
        ).ask_async()

        # Generate a simple user ID (in production, this would come from a database)
        self.user_id = hash(self.user_name) % 10000

        # Initialize agent session
        await self.agent.initialize_session(self.user_name, self.user_id)

    async def collect_initial_info(self):
        """Collect initial health and fitness information."""
        # Collect goal
        goal = await questionary.text(
            "What's your health goal? (e.g., 'lose 5kg in 2 months')",
            validate=lambda text: "in" in text.lower() or "Please include duration (e.g., 'in 2 months')"
        ).ask_async()

        # Collect dietary preferences
        diet = await questionary.checkbox(
            "Select your dietary preferences:",
            choices=[
                "Vegetarian",
                "Vegan",
                "Pescatarian",
                "Gluten-free",
                "Dairy-free",
                "No specific restrictions"
            ]
        ).ask_async()

        # Collect fitness level
        fitness_level = await questionary.select(
            "What's your current fitness level?",
            choices=["Beginner", "Intermediate", "Advanced"]
        ).ask_async()

        # Process initial information
        await self.agent.handle_message(goal)
        return goal, diet, fitness_level

    async def main_loop(self):
        """Main interaction loop."""
        while True:
            # Show menu
            action = await questionary.select(
                "What would you like to do?",
                choices=[
                    "Get a meal plan",
                    "Get a workout plan",
                    "Track progress",
                    "Schedule check-in",
                    "Speak to nutrition expert",
                    "Report injury",
                    "Talk to human coach",
                    "Exit"
                ]
            ).ask_async()

            if action == "Exit":
                print("\nThank you for using Health & Wellness Planner! Stay healthy! 💪\n")
                break

            # Handle different actions
            if action == "Track progress":
                # Collect progress metrics
                weight = await questionary.text(
                    "Current weight (in kg):",
                    validate=lambda text: text.replace(".", "").isdigit() or "Please enter a valid number"
                ).ask_async()
                
                adherence = await questionary.select(
                    "How well did you follow your plan? (1-10)",
                    choices=[str(i) for i in range(1, 11)]
                ).ask_async()

            # Process the action as a message
            async for step in Runner.stream(self.agent, action, self.agent.context):
                if step["type"] == "message":
                    print(step["chunk"], end="", flush=True)
                elif step["type"] == "plan":
                    print(step["chunk"], end="", flush=True)
            print("\n")

            # Ask if user wants to continue
            if not await questionary.confirm("Would you like to do something else?").ask_async():
                print("\nThank you for using Health & Wellness Planner! Stay healthy! 💪\n")
                break

async def main():
    cli = HealthAgentCLI()
    await cli.setup_user()
    await cli.collect_initial_info()
    await cli.main_loop()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nExiting... Thank you for using Health & Wellness Planner! 👋\n")
        sys.exit(0) 