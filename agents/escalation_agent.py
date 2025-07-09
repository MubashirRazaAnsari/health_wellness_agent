from typing import Dict
from context import UserSessionContext

class EscalationAgent:
    name = "escalation"
    description = "Handles escalation to human coaches"

    async def handle_request(self, context: UserSessionContext, query: str) -> Dict:
        """
        Handles requests for human coach interaction.
        
        Args:
            context: User session context
            query: User's query for human coach
            
        Returns:
            Escalation status and next steps
        """
        # Example response (in real implementation, this would integrate with a coaching system)
        response = {
            "status": "escalated",
            "message": "I'm connecting you with a human coach.",
            "next_steps": [
                "A coach will review your profile and progress",
                "You'll receive an email within 24 hours to schedule a consultation",
                "The consultation will be 30 minutes via video call"
            ],
            "coach_specialties": [
                "Weight loss",
                "Strength training",
                "Nutrition planning"
            ],
            "preparation": [
                "Please have your recent progress data ready",
                "Prepare any specific questions",
                "Think about your main challenges"
            ]
        }
        
        return response

    async def on_handoff(self, context: UserSessionContext) -> None:
        """Called when control is handed to this agent."""
        context.log_handoff(f"Control handed to {self.name} agent for human coach escalation") 