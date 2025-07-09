from typing import Dict
from guardrails import GoalInput, validate_goal_string

class GoalAnalyzerTool:
    name = "goal_analyzer"
    description = "Analyzes and structures user health and fitness goals"

    async def run(self, goal_string: str) -> Dict:
        """
        Analyzes a natural language goal string and converts it to structured format.
        
        Args:
            goal_string: Natural language description of user's goal
            
        Returns:
            Structured goal information
        """
        # Validate input format
        if not validate_goal_string(goal_string):
            raise ValueError("Invalid goal format. Example: 'lose 5kg in 2 months'")

        # Parse goal string
        parts = goal_string.lower().split()
        goal_type = "weight_loss" if parts[0] == "lose" else "muscle_gain"
        target_value = float(parts[1])
        unit = parts[2]
        duration = int(parts[4])
        duration_weeks = duration * 4 if "month" in parts[5] else duration

        # Create structured goal
        goal = GoalInput(
            goal_type=goal_type,
            target_value=target_value,
            unit=unit,
            duration_weeks=duration_weeks
        )

        return goal.dict() 