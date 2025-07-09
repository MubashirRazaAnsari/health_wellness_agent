from typing import Dict, List
from guardrails import DietaryInput, MealPlan

class MealPlannerTool:
    name = "meal_planner"
    description = "Generates personalized meal plans based on user preferences and goals"

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

        # Example meal plan generation (in real implementation, this would use more sophisticated logic)
        sample_meal_plan = {
            "meals": [
                {
                    "day": 1,
                    "breakfast": "Oatmeal with berries",
                    "lunch": "Quinoa salad with chickpeas",
                    "dinner": "Grilled salmon with vegetables",
                    "snacks": ["Apple", "Almonds"],
                    "calories": 2000
                }
                # ... more days would be added here
            ],
            "total_calories": 2000,
            "macros": {
                "protein": 25.0,
                "carbs": 50.0,
                "fats": 25.0
            },
            "shopping_list": [
                "Oatmeal",
                "Mixed berries",
                "Quinoa",
                "Chickpeas",
                "Salmon",
                "Mixed vegetables",
                "Apples",
                "Almonds"
            ]
        }

        # Validate output format
        meal_plan = MealPlan(**sample_meal_plan)
        return meal_plan.dict() 