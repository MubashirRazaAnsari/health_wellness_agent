from typing import Dict, Optional
from context import UserSessionContext
from config.settings import Settings

class InjurySupportAgent:
    name = "injury_support"
    description = "Specialized agent for handling injury-related queries and providing safe exercise modifications"

    def __init__(self):
        self.client = Settings.get_openai_client()

    async def get_ai_response(self, context: str, query: str) -> str:
        """Get AI response with injury and rehabilitation expertise."""
        system_prompt = """You are a qualified physical therapy and rehabilitation expert with extensive knowledge of 
        exercise modifications, injury prevention, and safe recovery practices. Always prioritize safety and injury 
        prevention in your advice. Recommend consulting healthcare providers for specific medical conditions or severe 
        injuries. Focus on providing safe alternatives and recovery strategies."""
        
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
        Handles injury-related queries and provides exercise modifications.
        
        Args:
            context: User session context
            query: User's injury-related query
            
        Returns:
            Exercise modifications and safety recommendations
        """
        # Build context string
        context_str = f"User's health goal: {context.goal if context.goal else 'Not specified'}"
        if hasattr(context, 'injuries'):
            context_str += f"\nReported injuries: {', '.join(context.injuries)}"
        if hasattr(context, 'fitness_level'):
            context_str += f"\nFitness level: {context.fitness_level}"
            
        # Get AI response
        response_text = await self.get_ai_response(context_str, query)
        
        # Structure the response
        response = {
            "message": response_text,
            "type": "injury_support"
        }
        
        return response

    async def on_handoff(self, context: UserSessionContext) -> None:
        """Called when control is handed to this agent."""
        context.log_handoff(f"Control handed to {self.name} agent")
        # Initialize any agent-specific context here
        if not hasattr(context, 'injuries'):
            context.injuries = []
        if not hasattr(context, 'fitness_level'):
            context.fitness_level = "beginner" 