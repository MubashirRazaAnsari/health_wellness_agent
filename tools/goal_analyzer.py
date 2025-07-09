from typing import Dict
from guardrails import GoalInput, validate_goal_string
from config.settings import Settings
import json

class GoalAnalyzerTool:
    name = "goal_analyzer"
    description = "Analyzes and structures user health and fitness goals"

    def __init__(self):
        self.client = Settings.get_openai_client()

    async def get_ai_response(self, goal_string: str) -> Dict:
        """Get AI analysis of the goal."""
        system_prompt = """You are a health and fitness goal specialist. Analyze the user's goal and extract structured 
        information. The response should be a JSON object with the following structure:
        {
            "goal_type": "weight_loss/muscle_gain/endurance/general_health",
            "target_value": number,
            "unit": "kg/lbs/miles/etc",
            "duration_weeks": number,
            "sub_goals": ["specific milestone 1", "specific milestone 2"],
            "recommendations": ["recommendation 1", "recommendation 2"],
            "risk_factors": ["risk 1", "risk 2"] or []
        }
        
        For goals without specific numbers, use reasonable defaults based on health guidelines."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Analyze this fitness goal: {goal_string}"}
        ]

        model_config = Settings.get_model_config()
        response = self.client.chat.completions.create(
            model=model_config["model"],
            messages=messages,
            temperature=0.7,
            max_tokens=1000
        )

        try:
            # Parse the AI response as JSON
            goal_data = json.loads(response.choices[0].message.content)
            return goal_data
        except json.JSONDecodeError:
            # Fallback to basic structure
            return {
                "goal_type": "general_health",
                "target_value": 0,
                "unit": "kg",
                "duration_weeks": 12,
                "sub_goals": ["Establish baseline", "Build healthy habits"],
                "recommendations": ["Start with basics", "Focus on consistency"],
                "risk_factors": []
            }

    async def run(self, goal_string: str) -> Dict:
        """
        Analyzes a natural language goal string and converts it to structured format.
        
        Args:
            goal_string: Natural language description of user's goal
            
        Returns:
            Structured goal information
        """
        # Get AI analysis of the goal
        goal_data = await self.get_ai_response(goal_string)

        # Create structured goal with additional insights
        goal = GoalInput(
            goal_type=goal_data["goal_type"],
            target_value=goal_data["target_value"],
            unit=goal_data["unit"],
            duration_weeks=goal_data["duration_weeks"],
            sub_goals=goal_data.get("sub_goals", []),
            recommendations=goal_data.get("recommendations", []),
            risk_factors=goal_data.get("risk_factors", [])
        )

        return goal.dict() 