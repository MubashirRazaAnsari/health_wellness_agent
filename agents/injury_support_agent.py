from typing import Dict
from context import UserSessionContext
from guardrails import validate_injury_input

class InjurySupportAgent:
    name = "injury_support"
    description = "Specialized agent for handling injury-related concerns and modifications"

    async def handle_request(self, context: UserSessionContext, injury_description: str) -> Dict:
        """
        Provides injury-specific workout modifications and recovery advice.
        
        Args:
            context: User session context
            injury_description: Description of the injury and concerns
            
        Returns:
            Modified workout plan and recovery recommendations
        """
        # Validate injury description
        if not validate_injury_input(injury_description):
            raise ValueError("Please provide injury location, pain level, and duration")

        # Example response (in real implementation, this would use more sophisticated logic)
        response = {
            "modified_exercises": [
                {
                    "original": "Squats",
                    "modification": "Wall sits",
                    "reason": "Reduces knee impact while maintaining strength"
                },
                {
                    "original": "Running",
                    "modification": "Swimming",
                    "reason": "Low-impact cardio alternative"
                }
            ],
            "recovery_tips": [
                "Apply ice for 15-20 minutes every 2-3 hours",
                "Gentle stretching exercises",
                "Consider physical therapy consultation"
            ],
            "warning_signs": [
                "Increased pain during exercise",
                "Swelling",
                "Limited range of motion"
            ]
        }
        
        return response

    async def on_handoff(self, context: UserSessionContext) -> None:
        """Called when control is handed to this agent."""
        context.log_handoff(f"Control handed to {self.name} agent") 