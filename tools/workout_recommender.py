from typing import Dict
from guardrails import WorkoutPlan

class WorkoutRecommenderTool:
    name = "workout_recommender"
    description = "Recommends personalized workout plans based on user goals and experience"

    async def run(self, goal: Dict, experience_level: str = "beginner") -> Dict:
        """
        Generates a workout plan based on user's goals and experience level.
        
        Args:
            goal: Structured goal information
            experience_level: User's fitness experience level
            
        Returns:
            Structured workout plan
        """
        # Example workout plan generation (in real implementation, this would use more sophisticated logic)
        sample_workout = {
            "exercises": [
                {
                    "name": "Squats",
                    "sets": 3,
                    "reps": 12,
                    "rest_seconds": 60,
                    "notes": "Focus on form and depth"
                },
                {
                    "name": "Push-ups",
                    "sets": 3,
                    "reps": 10,
                    "rest_seconds": 60,
                    "notes": "Modify on knees if needed"
                }
                # ... more exercises would be added here
            ],
            "duration_minutes": 45,
            "difficulty": experience_level,
            "equipment_needed": ["None", "Exercise mat"]
        }

        # Validate output format
        workout_plan = WorkoutPlan(**sample_workout)
        return workout_plan.dict() 