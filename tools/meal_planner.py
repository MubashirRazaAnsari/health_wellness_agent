from typing import Dict
from guardrails import MealPlanOutput
from utils.openai_client import client
import json

async def meal_planner(goal: dict, diet_preferences: str = None) -> Dict:
    system_prompt = """You are a meal planning assistant. Generate a 7-day meal plan based on the user's goal and dietary preferences. Return a JSON object with meals, total_calories, macros, and shopping_list."""
    user_content = f"Goal: {goal}\nDietary preferences: {diet_preferences or 'None'}"
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_content}
    ]
    response = client.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        messages=messages,
        temperature=0.7,
        max_tokens=1500,
        response_format={"type": "json_object"}
    )
    try:
        meal_data = json.loads(response.choices[0].message.content)
        return MealPlanOutput(**meal_data).dict()
    except Exception:
        return {"error": "Could not parse or validate meal plan output."}

meal_planner.schema = {
    "name": "meal_planner",
    "description": "Suggests a 7-day meal plan honoring dietary preferences.",
    "parameters": {
        "type": "object",
        "properties": {
            "goal": {"type": "object", "description": "Structured user goal as a dict"},
            "diet_preferences": {"type": "string", "description": "User's dietary preferences", "nullable": True}
        },
        "required": ["goal"]
    }
} 