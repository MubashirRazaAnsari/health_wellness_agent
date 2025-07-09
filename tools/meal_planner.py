from typing import Dict, List
from guardrails import DietaryInput, MealPlan
from config.settings import Settings
import json

class MealPlannerTool:
    name = "meal_planner"
    description = "Generates personalized meal plans based on user preferences and goals"

    def __init__(self):
        self.client = Settings.get_openai_client()

    async def get_ai_response(self, preferences: Dict, goal: Dict) -> Dict:
        """Get AI-generated meal plan."""
        system_prompt = """You are a professional nutritionist and meal planning expert. Create a detailed 7-day meal plan 
        that aligns with the user's dietary preferences and health goals. The meal plan should be realistic, varied, and 
        include all meals and snacks. Include estimated calories and a comprehensive shopping list.

        Format your response as a JSON object with the following structure:
        {
            "meals": [
                {
                    "day": 1,
                    "breakfast": "detailed breakfast description",
                    "lunch": "detailed lunch description",
                    "dinner": "detailed dinner description",
                    "snacks": ["snack1", "snack2"],
                    "calories": daily_calorie_count
                }
                // ... repeat for all 7 days
            ],
            "total_calories": weekly_total,
            "macros": {
                "protein": percentage,
                "carbs": percentage,
                "fats": percentage
            },
            "shopping_list": ["item1", "item2", ...]
        }"""

        user_prompt = f"""Create a meal plan with these requirements:
        Dietary Preferences: {preferences.get('preferences', [])}
        Restrictions: {preferences.get('restrictions', [])}
        Health Goal: {goal.get('goal_type', 'general health')}
        Target: {goal.get('target_value', '')} {goal.get('unit', '')}
        Duration: {goal.get('duration_weeks', 0)} weeks"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        model_config = Settings.get_model_config()
        response = self.client.chat.completions.create(
            model=model_config["model"],
            messages=messages,
            temperature=0.7,
            max_tokens=2000  # Increased for detailed meal plan
        )

        try:
            # Parse the AI response as JSON
            meal_plan_data = json.loads(response.choices[0].message.content)
            return meal_plan_data
        except json.JSONDecodeError:
            # Fallback to basic structure if JSON parsing fails
            return {
                "meals": [{"day": 1, "breakfast": response.choices[0].message.content[:500]}],
                "total_calories": 2000,
                "macros": {"protein": 30, "carbs": 40, "fats": 30},
                "shopping_list": ["Please see meal descriptions for ingredients"]
            }

    async def run(self, preferences: Dict, goal: Dict) -> Dict:
        """
        Generates a 7-day meal plan based on dietary preferences and goals.
        
        Args:
            preferences: User's dietary preferences and restrictions
            goal: Structured goal information
            
        Returns:
            7-day meal plan with shopping list
        """
        # Validate dietary preferences
        diet_input = DietaryInput(**preferences)
        
        # Get AI-generated meal plan
        meal_plan_data = await self.get_ai_response(preferences, goal)

        # Validate output format
        meal_plan = MealPlan(**meal_plan_data)
        return meal_plan.dict() 