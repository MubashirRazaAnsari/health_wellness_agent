from typing import Dict
from context import UserSessionContext
from config.settings import Settings
import json

class EscalationAgent:
    name = "escalation"
    description = "Handles escalation to human coaches"

    def __init__(self):
        self.client = Settings.get_openai_client()

    async def get_ai_recommendation(self, context: UserSessionContext, query: str) -> Dict:
        """Get AI recommendation for coach matching."""
        system_prompt = """You are an expert in matching users with appropriate health and fitness coaches. Analyze the 
        user's context and query to recommend the best coaching approach. The response should be a JSON object with the 
        following structure:
        {
            "escalation_reason": "detailed reason for escalation",
            "priority_level": "low/medium/high",
            "coach_requirements": {
                "specialties": ["specialty1", "specialty2"],
                "experience_level": "entry/intermediate/senior",
                "certifications": ["cert1", "cert2"]
            },
            "session_recommendations": {
                "format": "video/audio/text",
                "duration": "minutes",
                "frequency": "sessions per week/month"
            },
            "preparation_checklist": ["item1", "item2"],
            "success_metrics": ["metric1", "metric2"]
        }"""

        # Build context string
        context_str = f"""
        User Goal: {context.goal if hasattr(context, 'goal') else 'Not specified'}
        Fitness Level: {context.fitness_level if hasattr(context, 'fitness_level') else 'Not specified'}
        Injuries: {', '.join(context.injuries) if hasattr(context, 'injuries') and context.injuries else 'None'}
        Dietary Preferences: {', '.join(context.dietary_preferences) if hasattr(context, 'dietary_preferences') and context.dietary_preferences else 'None'}
        Query: {query}
        """

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": context_str}
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
            recommendation_data = json.loads(response.choices[0].message.content)
            return recommendation_data
        except json.JSONDecodeError:
            # Fallback to basic structure
            return {
                "escalation_reason": "User requested human coach assistance",
                "priority_level": "medium",
                "coach_requirements": {
                    "specialties": ["General fitness", "Nutrition"],
                    "experience_level": "intermediate",
                    "certifications": ["Certified Personal Trainer"]
                },
                "session_recommendations": {
                    "format": "video",
                    "duration": "30",
                    "frequency": "1 per week"
                },
                "preparation_checklist": ["Recent progress data", "Specific questions"],
                "success_metrics": ["Goal achievement", "User satisfaction"]
            }

    async def handle_request(self, context: UserSessionContext, query: str) -> Dict:
        """
        Handles requests for human coach interaction.
        
        Args:
            context: User session context
            query: User's query for human coach
            
        Returns:
            Escalation status and next steps
        """
        # Get AI recommendation for coach matching
        recommendation = await self.get_ai_recommendation(context, query)
        
        response = {
            "status": "escalated",
            "message": "I'm connecting you with a human coach.",
            "escalation_details": {
                "reason": recommendation["escalation_reason"],
                "priority": recommendation["priority_level"]
            },
            "coach_matching": {
                "required_specialties": recommendation["coach_requirements"]["specialties"],
                "experience_level": recommendation["coach_requirements"]["experience_level"],
                "certifications": recommendation["coach_requirements"]["certifications"]
            },
            "session_plan": {
                "format": recommendation["session_recommendations"]["format"],
                "duration_minutes": int(recommendation["session_recommendations"]["duration"]),
                "frequency": recommendation["session_recommendations"]["frequency"]
            },
            "preparation": recommendation["preparation_checklist"],
            "success_metrics": recommendation["success_metrics"]
        }
        
        return response

    async def on_handoff(self, context: UserSessionContext) -> None:
        """Called when control is handed to this agent."""
        context.log_handoff(f"Control handed to {self.name} agent for human coach escalation") 