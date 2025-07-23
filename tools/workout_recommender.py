from typing import Dict
from guardrails import WorkoutPlanOutput
from utils.openai_client import client
import json

async def workout_recommender(goal: dict, experience_level: str = "beginner") -> Dict:
    system_prompt = """You are a workout planning assistant. Generate a weekly workout plan based on the user's goal and experience level. Return a JSON object with exercises, duration_minutes, difficulty, and equipment_needed."""
    user_content = f"Goal: {goal}\nExperience level: {experience_level}"
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_content}
    ]
    response = client.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        messages=messages,
        temperature=0.7,
        max_tokens=1200,
        response_format={"type": "json_object"}
    )
    try:
        workout_data = json.loads(response.choices[0].message.content)
        return WorkoutPlanOutput(**workout_data).dict()
    except Exception:
        return {"error": "Could not parse or validate workout plan output."}

workout_recommender.schema = {
    "name": "workout_recommender",
    "description": "Suggests a workout plan based on parsed goals and experience.",
    "parameters": {
        "type": "object",
        "properties": {
            "goal": {"type": "object", "description": "Structured user goal as a dict"},
            "experience_level": {"type": "string", "description": "User's experience level", "default": "beginner"}
        },
        "required": ["goal"]
    }
} 