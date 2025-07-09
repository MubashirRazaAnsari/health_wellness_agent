from typing import Dict
from guardrails import WorkoutPlan
from config.settings import Settings
import json

class WorkoutRecommenderTool:
    name = "workout_recommender"
    description = "Recommends personalized workout plans based on user goals and experience"

    def __init__(self):
        self.client = Settings.get_openai_client()

    async def get_ai_response(self, goal: Dict, experience_level: str) -> Dict:
        """Get AI-generated workout plan."""
        system_prompt = """You are a certified personal trainer and exercise specialist. Create a detailed, safe, and 
        effective workout plan that matches the user's goals and experience level. Include proper form cues, progression 
        strategies, and safety considerations.

        Format your response as a JSON object with the following structure:
        {
            "workout_type": "strength_training/circuit_training/etc",
            "exercises": [
                {
                    "name": "exercise name",
                    "sets": number,
                    "reps": number,
                    "rest_seconds": number,
                    "notes": "form cues and tips"
                }
                // ... more exercises
            ],
            "duration_minutes": total_workout_time,
            "difficulty": "beginner/intermediate/advanced",
            "equipment_needed": ["equipment1", "equipment2"],
            "warm_up": ["warm up activity1", "warm up activity2"],
            "cool_down": ["cool down activity1", "cool down activity2"],
            "progression": {
                "beginner": "progression tips",
                "intermediate": "progression tips",
                "advanced": "progression tips"
            }
        }"""

        user_prompt = f"""Create a workout plan with these requirements:
        Experience Level: {experience_level}
        Health Goal: {goal.get('goal_type', 'general fitness')}
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
            max_tokens=1500  # Increased for detailed workout plan
        )

        try:
            # Parse the AI response as JSON
            workout_data = json.loads(response.choices[0].message.content)
            return workout_data
        except json.JSONDecodeError:
            # Fallback to basic structure if JSON parsing fails
            return {
                "workout_type": "general_fitness",
                "exercises": [
                    {
                        "name": "Please see workout description below",
                        "sets": 3,
                        "reps": 10,
                        "rest_seconds": 60,
                        "notes": response.choices[0].message.content[:500]
                    }
                ],
                "duration_minutes": 45,
                "difficulty": experience_level,
                "equipment_needed": ["Basic equipment"],
                "warm_up": ["Light cardio", "Dynamic stretching"],
                "cool_down": ["Static stretching", "Light walking"],
                "progression": {"beginner": "Start with basics and focus on form"}
            }

    async def run(self, goal: Dict, experience_level: str = "beginner") -> Dict:
        """
        Generates a workout plan based on user's goals and experience level.
        
        Args:
            goal: Structured goal information
            experience_level: User's fitness experience level
            
        Returns:
            Structured workout plan
        """
        # Get AI-generated workout plan
        workout_data = await self.get_ai_response(goal, experience_level)

        # Validate output format
        workout_plan = WorkoutPlan(**workout_data)
        return workout_plan.dict() 