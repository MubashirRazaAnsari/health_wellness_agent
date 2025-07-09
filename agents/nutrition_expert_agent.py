from typing import Dict, Optional
from context import UserSessionContext
from config.settings import Settings

class NutritionExpertAgent:
    name = "nutrition_expert"
    description = "Specialized agent for handling complex dietary needs and restrictions"

    def __init__(self):
        self.client = Settings.get_openai_client()

    async def get_ai_response(self, context: str, query: str) -> str:
        """Get AI response with nutrition expertise."""
        system_prompt = """You are a qualified nutrition expert with extensive knowledge of dietary requirements, 
        restrictions, and health conditions. Provide detailed, scientifically-backed advice while maintaining a supportive 
        and educational tone. Always prioritize safety and recommend consulting healthcare providers for medical conditions."""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Context: {context}\n\nQuery: {query}"}
        ]
        
        model_config = Settings.get_model_config()
        response = self.client.chat.completions.create(
            model=model_config["model"],
            messages=messages,
            temperature=model_config["temperature"],
            max_tokens=model_config["max_tokens"]
        )
        
        return response.choices[0].message.content

    async def handle_request(self, context: UserSessionContext, query: str) -> Dict:
        """
        Handles nutrition-specific queries and provides expert dietary advice.
        
        Args:
            context: User session context
            query: User's nutrition-related query
            
        Returns:
            Expert dietary advice and recommendations
        """
        # Build context string
        context_str = f"User's health goal: {context.goal if context.goal else 'Not specified'}"
        if hasattr(context, 'dietary_preferences'):
            context_str += f"\nDietary preferences: {', '.join(context.dietary_preferences)}"
        if hasattr(context, 'allergies'):
            context_str += f"\nAllergies: {', '.join(context.allergies)}"
            
        # Get AI response
        response_text = await self.get_ai_response(context_str, query)
        
        # Structure the response
        response = {
            "message": response_text,
            "type": "nutrition_advice"
        }
        
        return response

    async def on_handoff(self, context: UserSessionContext) -> None:
        """Called when control is handed to this agent."""
        context.log_handoff(f"Control handed to {self.name} agent")
        # Initialize any agent-specific context here
        if not hasattr(context, 'dietary_preferences'):
            context.dietary_preferences = []
        if not hasattr(context, 'allergies'):
            context.allergies = [] 