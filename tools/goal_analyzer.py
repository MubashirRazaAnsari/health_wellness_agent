from typing import Dict
from guardrails import GoalOutput
from utils.openai_client import client
import json

async def analyze_goal(goal_string: str) -> Dict:
    system_prompt = """You are a health and fitness goal specialist. Analyze the user's goal and extract structured information. The response should be a JSON object with the following structure: {\n    \"goal_type\": \"weight_loss/muscle_gain/endurance/general_health\",\n    \"target_value\": number,\n    \"unit\": \"kg/lbs/miles/etc\",\n    \"duration_weeks\": number,\n    \"sub_goals\": [\"specific milestone 1\", \"specific milestone 2\"],\n    \"recommendations\": [\"recommendation 1\", \"recommendation 2\"],\n    \"risk_factors\": [\"risk 1\", \"risk 2\"] or []\n}\nFor goals without specific numbers, use reasonable defaults based on health guidelines."""
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Analyze this fitness goal: {goal_string}"}
    ]
    response = client.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        messages=messages,
        temperature=0.7,
        max_tokens=1000,
        response_format={"type": "json_object"}
    )
    try:
        goal_data = json.loads(response.choices[0].message.content)
        # Output guardrail: validate with Pydantic
        return GoalOutput(**goal_data).dict()
    except Exception:
        return {"error": "Could not parse or validate goal analysis output."}

analyze_goal.schema = {
    "name": "analyze_goal",
    "description": "Converts user goals into structured format.",
    "parameters": {
        "type": "object",
        "properties": {
            "goal_string": {"type": "string", "description": "User's fitness goal in natural language"}
        },
        "required": ["goal_string"]
    }
} 