from typing import Dict, List, Optional
from context import UserSessionContext
from tools.goal_analyzer import GoalAnalyzerTool
from tools.meal_planner import MealPlannerTool
from tools.workout_recommender import WorkoutRecommenderTool
from agents.nutrition_expert_agent import NutritionExpertAgent
from agents.injury_support_agent import InjurySupportAgent

class HealthWellnessAgent:
    def __init__(self):
        # Initialize tools
        self.goal_analyzer = GoalAnalyzerTool()
        self.meal_planner = MealPlannerTool()
        self.workout_recommender = WorkoutRecommenderTool()

        # Initialize specialized agents
        self.nutrition_expert = NutritionExpertAgent()
        self.injury_support = InjurySupportAgent()

        # Initialize state
        self.context = None

    async def initialize_session(self, user_name: str, user_id: int) -> None:
        """Initialize a new user session."""
        self.context = UserSessionContext(
            name=user_name,
            uid=user_id
        )

    async def handle_message(self, message: str) -> Dict:
        """
        Main message handler for the agent.
        
        Args:
            message: User's input message
            
        Returns:
            Agent's response
        """
        # Check if we need to hand off to a specialized agent
        if "diabetic" in message.lower() or "allergy" in message.lower():
            return await self.nutrition_expert.handle_request(self.context, message)
        elif "injury" in message.lower() or "pain" in message.lower():
            return await self.injury_support.handle_request(self.context, message)

        # Process regular health and wellness queries
        if "goal" in message.lower():
            goal_data = await self.goal_analyzer.run(message)
            self.context.update_goal(goal_data)
            return {"message": "I've recorded your goal. Would you like me to create a meal and workout plan?"}

        elif "meal plan" in message.lower():
            if not self.context.goal:
                return {"message": "Please tell me your health goal first."}
            meal_plan = await self.meal_planner.run(
                preferences={"preferences": ["balanced"], "restrictions": []},
                goal=self.context.goal
            )
            self.context.update_meal_plan(meal_plan["meals"])
            return {"message": "Here's your personalized meal plan:", "plan": meal_plan}

        elif "workout" in message.lower():
            if not self.context.goal:
                return {"message": "Please tell me your health goal first."}
            workout_plan = await self.workout_recommender.run(
                goal=self.context.goal
            )
            self.context.update_workout_plan(workout_plan)
            return {"message": "Here's your personalized workout plan:", "plan": workout_plan}

        return {"message": "I'm here to help with your health and wellness journey. What would you like to know?"} 