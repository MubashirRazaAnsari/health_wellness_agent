from typing import Dict, List, Optional, AsyncGenerator, Any, AsyncIterator
import asyncio
import traceback
from context import UserSessionContext
from config.settings import Settings

# Import utilities
from utils.agent_utils import (
    async_error_handler,
    ToolManager,
    ResponseFormatter,
    MessageClassifier,
    ConfigManager,
    ContextManager,
    safe_async_call,
    validate_user_input,
    sanitize_response
)
from utils.openai_client import client
from tools.goal_analyzer import analyze_goal
from tools.meal_planner import meal_planner
from tools.workout_recommender import workout_recommender
from tools.scheduler import checkin_scheduler
from tools.tracker import progress_tracker
from agents.nutrition_expert_agent import NutritionExpertAgent
from agents.injury_support_agent import InjurySupportAgent
from agents.escalation_agent import EscalationAgent
from guardrails import validate_goal_string, GoalOutput, MealPlanOutput, WorkoutPlanOutput

class AsyncResponseIterator:
    """Async iterator for streaming responses from OpenRouter API."""
    
    def __init__(self, client, messages, model, config):
        """Initialize the async iterator."""
        self.client = client
        self.messages = messages
        self.model = model
        self.config = config
        self.current_tool = None
        self._queue = asyncio.Queue()
        self._done = False
        self._started = False
        
    async def _process_chunks(self):
        """Process the completion chunks."""
        try:
            # Create completion with streaming
            response = self.client.chat.completions.create(
                model=self.model,
                messages=self.messages,
                temperature=self.config.get("temperature", 0.7),
                max_tokens=self.config.get("max_tokens", 500),
                stream=True
            )
            
            # Process each chunk without awaiting the stream directly
            for chunk in response:
                if not chunk or not chunk.choices:
                    continue
                    
                delta = chunk.choices[0].delta
                
                # Handle function calls
                if hasattr(delta, 'function_call') and delta.function_call:
                    if not self.current_tool:
                        self.current_tool = delta.function_call.name
                        await self._queue.put({"tool_call": self.current_tool})
                
                # Handle content
                if hasattr(delta, 'content') and delta.content:
                    await self._queue.put(delta.content)
            
            # Mark as done when all chunks are processed
            self._done = True
            
        except Exception as e:
            print(f"Stream processing error: {str(e)}")
            await self._queue.put(f"Error: {str(e)}")
            self._done = True
    
    def __aiter__(self):
        """Return self as async iterator."""
        return self
    
    async def __anext__(self):
        """Get next chunk from the stream."""
        try:
            # Start processing if not started
            if not self._started:
                self._started = True
                asyncio.create_task(self._process_chunks())
            
            # Get next chunk with timeout
            try:
                chunk = await asyncio.wait_for(self._queue.get(), timeout=0.1)
                return chunk
            except asyncio.TimeoutError:
                if self._done and self._queue.empty():
                    raise StopAsyncIteration
                return ""  # Return empty chunk and continue
                
        except Exception as e:
            print(f"Stream iteration error: {str(e)}")
            raise StopAsyncIteration

class ImprovedAsyncResponseIterator:
    """Async iterator for streaming responses from OpenRouter API with improved formatting."""
    
    def __init__(self, client, messages, model, config):
        """Initialize the async iterator."""
        self.client = client
        self.messages = messages
        self.model = model
        self.config = config
        self.current_tool = None
        self._queue = asyncio.Queue()
        self._done = False
        self._started = False
        
    async def _process_chunks(self):
        """Process the completion chunks."""
        try:
            # Create completion with streaming
            response = self.client.chat.completions.create(
                model=self.model,
                messages=self.messages,
                temperature=self.config.get("temperature", 0.7),
                max_tokens=self.config.get("max_tokens", 500),
                stream=True
            )
            
            # Process each chunk without awaiting the stream directly
            for chunk in response:
                if not chunk or not chunk.choices:
                    continue
                    
                delta = chunk.choices[0].delta
                
                # Handle function calls
                if hasattr(delta, 'function_call') and delta.function_call:
                    if not self.current_tool:
                        self.current_tool = delta.function_call.name
                        await self._queue.put({"tool_call": self.current_tool})
                
                # Handle content
                if hasattr(delta, 'content') and delta.content:
                    await self._queue.put(delta.content)
            
            # Mark as done when all chunks are processed
            self._done = True
            
        except Exception as e:
            print(f"Stream processing error: {str(e)}")
            await self._queue.put(f"Error: {str(e)}")
            self._done = True
    
    def __aiter__(self):
        """Return self as async iterator."""
        return self
    
    async def __anext__(self):
        """Get next chunk from the stream."""
        try:
            # Start processing if not started
            if not self._started:
                self._started = True
                asyncio.create_task(self._process_chunks())
            
            # Get next chunk with timeout
            try:
                chunk = await asyncio.wait_for(self._queue.get(), timeout=0.1)
                return chunk
            except asyncio.TimeoutError:
                if self._done and self._queue.empty():
                    raise StopAsyncIteration
                return ""  # Return empty chunk and continue
                
        except Exception as e:
            print(f"Stream iteration error: {str(e)}")
            raise StopAsyncIteration

class HealthWellnessAgent:
    """Enhanced Health & Wellness Agent with improved error handling and tool integration."""
    
    def __init__(self, config_path: Optional[str] = None, run_hooks=None, agent_hooks=None):
        """Initialize the agent with configuration and tools."""
        self.config = ConfigManager(config_path)
        self.tool_manager = ToolManager()
        self.response_formatter = ResponseFormatter()
        self.message_classifier = MessageClassifier()
        self.context_manager = ContextManager()
        
        # Initialize hooks
        self.run_hooks = run_hooks
        self.agent_hooks = agent_hooks
        
        # Initialize OpenAI client
        self.context = None
        
        # Initialize tools and components
        self._initialize_components()
    
    def _initialize_components(self):
        """Initialize all components with proper error handling."""
        try:
            # Initialize OpenRouter client through config manager
            # self.client = self.config.get_ai_client() # This line is removed
            if not client: # Check if client is initialized
                raise ValueError("Failed to initialize OpenAI client")
            
            # Register tools
            self._register_tools()
            
            print(f"✅ Agent initialized successfully with model: {self.config.get_current_model()}")
            
        except Exception as e:
            print(f"⚠️ Agent initialization warning: {str(e)}")
            print("Agent will continue with limited functionality")
    
    def _register_tools(self):
        """Register function-calling tools with the OpenAI client."""
        self.tools = [analyze_goal]

    @async_error_handler("Failed to initialize session. Please try again.")
    async def initialize_session(self, user_name: str, user_id: int) -> None:
        """Initialize a new user session."""
        try:
            self.context = UserSessionContext(name=user_name, uid=user_id)
            self.context_manager.update_context("user_name", user_name)
            self.context_manager.update_context("user_id", user_id)
            print(f"✅ Session initialized for user: {user_name}")
            
        except Exception as e:
            print(f"Error initializing session: {str(e)}")
            # Create minimal fallback context
            self.context = type('Context', (), {
                'name': user_name,
                'uid': user_id,
                'goal': None,
                'update_goal': lambda x: None,
                'update_meal_plan': lambda x: None,
                'update_workout_plan': lambda x: None
            })()
    
    async def get_ai_response(self, message: str, system_prompt: str = None) -> str:
        """Get response from AI model, using function calling if a tool matches. Moderate output."""
        if not client:
            return "I'm currently unable to connect to the AI service. Please try again later."

        # Example: if the message looks like a goal analysis request, use the tool
        if validate_goal_string(message):
            tool = analyze_goal
            tool_args = {"goal_string": message}
            result = await tool(**tool_args)
            # Moderate tool output
            moderation = client.moderations.create(input=str(result))
            if moderation.results[0].flagged:
                return "⚠️ The response was flagged as unsafe. Please rephrase your request."
            return str(result)

        # Otherwise, do a normal chat completion
        messages = []
        formatting_instructions = """
        Format your responses with proper structure:
        - Use numbered lists for sequential steps (1., 2., etc.)
        - Use bullet points for non-sequential items
        - Add line breaks between paragraphs
        - Highlight important points with emphasis
        - Break down complex information into digestible sections
        """
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": message})
        model_config = self.config.get("model", {})
        response = client.chat.completions.create(
            model=self.config.get_current_model(),
            messages=messages,
            temperature=0.7,
            max_tokens=1000
        )
        content = response.choices[0].message.content
        # Moderate LLM output
        moderation = client.moderations.create(input=content)
        if moderation.results[0].flagged:
            return "⚠️ The response was flagged as unsafe. Please rephrase your request."
        return content
    
    @async_error_handler("Error in streaming response")
    async def get_streaming_response(
        self,
        message: str,
        context: UserSessionContext,
        system_prompt: str = None
    ) -> ImprovedAsyncResponseIterator:
        """
        Get streaming response from the AI model with improved formatting.
        
        Args:
            message: User's message
            context: User's session context
            system_prompt: Optional system prompt
            
        Returns:
            ImprovedAsyncResponseIterator for streaming responses
        """
        if not client: # Check if client is initialized
            raise ValueError("AI client not initialized")

        try:
            # Update context
            self.context = context
            
            # Call hooks if available
            if self.agent_hooks:
                await self.agent_hooks.on_start(context)
            if self.run_hooks:
                await self.run_hooks.on_agent_start(context)

            # Enhanced formatting instructions
            formatting_instructions = """
            You are a health and wellness expert. Format your responses clearly and professionally:

            FORMATTING RULES:
            1. Use numbered lists for step-by-step instructions (1., 2., 3.)
            2. Use bullet points (*) for related items or tips
            3. Separate different topics with blank lines
            4. Use **bold** for important terms or headings
            5. Keep paragraphs focused and readable
            6. Use proper spacing between sections

            STRUCTURE YOUR RESPONSE:
            - Start with a brief, direct answer
            - Follow with detailed explanation if needed
            - Use lists for actionable items
            - End with encouragement or next steps

            EXAMPLE FORMAT:
            Here's how to approach your fitness goal:

            1. Start with a proper assessment of your current fitness level.

            2. Create a progressive workout plan that includes:
               * Cardiovascular exercise (3-4 times per week)
               * Strength training (2-3 times per week)
               * Flexibility work (daily stretching)

            3. Monitor your progress and adjust as needed.

            **Important:** Always listen to your body and rest when needed.

            Remember, consistency is key to achieving your health goals!
            """

            # Prepare messages
            messages = []
            if system_prompt:
                messages.append({
                    "role": "system",
                    "content": f"{system_prompt}\n\n{formatting_instructions}"
                })
            else:
                messages.append({
                    "role": "system",
                    "content": formatting_instructions
                })
            
            # Add context information
            context_info = self._build_context_info()
            if context_info:
                message = f"{message}\n\nContext: {context_info}"
            
            messages.append({"role": "user", "content": message})
            
            # Get model configuration
            model_config = self.config.get("model", {})
            
            # Return improved async iterator
            return ImprovedAsyncResponseIterator(
                client=client,
                messages=messages,
                model=self.config.get_current_model(),
                config=model_config
            )
                
        except Exception as e:
            print(f"Error in get_streaming_response: {str(e)}")
            raise
    
    def _build_context_info(self) -> str:
        """Build context information string."""
        context_parts = []
        
        if self.context and hasattr(self.context, 'goal') and self.context.goal:
            context_parts.append(f"User's goal: {self.context.goal}")
        
        recent_context = self.context_manager.get_recent_context(3)
        if recent_context:
            context_parts.append(recent_context)
        
        return "\n".join(context_parts)
    
    @async_error_handler()
    async def handle_specialized_request(self, message: str, message_type: str) -> Optional[Dict]:
        """Handle requests that require specialized agents."""
        try:
            if message_type == "nutrition":
                # Check for specific nutrition needs
                if any(keyword in message.lower() for keyword in ["diabetic", "allergy", "gluten", "lactose"]):
                    nutrition_agent = self.tool_manager.get_tool("nutrition_expert")
                    if nutrition_agent:
                        return await safe_async_call(
                            nutrition_agent.handle_request,
                            self.context,
                            message
                        )
            
            elif message_type == "injury":
                injury_agent = self.tool_manager.get_tool("injury_support")
                if injury_agent:
                    return await safe_async_call(
                        injury_agent.handle_request,
                        self.context,
                        message
                    )
            
            return None
            
        except Exception as e:
            print(f"Error in specialized request handling: {str(e)}")
            return None
    
    @async_error_handler()
    async def handle_goal_setting(self, message: str) -> Dict:
        """Handle goal-related queries with enhanced processing."""
        try:
            # Use goal analyzer tool if available
            goal_analyzer = self.tool_manager.get_tool("goal_analyzer")
            goal_data = None
            
            if goal_analyzer:
                goal_data = await safe_async_call(goal_analyzer.run, message)
            
            # Fallback goal extraction
            if not goal_data:
                goal_data = {"goal": message, "type": "general", "timeline": "not specified"}
            
            # Update context
            if self.context and hasattr(self.context, 'update_goal'):
                self.context.update_goal(goal_data)
            
            self.context_manager.update_context("current_goal", goal_data)
            
            # Generate AI response
            system_prompt = """You are a supportive health and wellness expert. 
            Help the user analyze their health goal and provide constructive, motivating feedback. 
            Break down their goal into actionable steps and explain how you can help them achieve it.
            Be encouraging and specific in your recommendations."""
            
            ai_response = await self.get_ai_response(
                f"Help me set and analyze this health goal: {message}",
                system_prompt
            )
            
            # Format goal analysis if available
            goal_analysis = ""
            if goal_data and isinstance(goal_data, dict):
                goal_analysis = self.response_formatter.format_goal_analysis(goal_data)
            
            return {
                "message": ai_response,
                "goal_analysis": goal_analysis,
                "goal_set": True
            }
            
        except Exception as e:
            print(f"Error in goal setting: {str(e)}")
            return {"message": "I'd be happy to help you set a health goal! Could you tell me more about what you'd like to achieve?"}
    
    @async_error_handler()
    async def handle_meal_planning(self, message: str) -> Dict:
        """Handle meal planning requests with enhanced functionality."""
        try:
            # Check if user has a goal
            if not self._has_user_goal():
                return {
                    "message": "To create the best meal plan for you, I'd love to know more about your health goals! What are you hoping to achieve? (e.g., weight loss, muscle gain, better energy, etc.)",
                    "needs_goal": True
                }
            
            # Use meal planner tool
            meal_planner = self.tool_manager.get_tool("meal_planner")
            meal_plan = None
            
            if meal_planner:
                user_goal = self.context_manager.get_context("current_goal", self.context.goal if self.context else None)
                meal_plan = await safe_async_call(
                    meal_planner.run,
                    preferences={"preferences": ["balanced"], "restrictions": []},
                    goal=user_goal
                )
                
                # Update context
                if meal_plan and self.context and hasattr(self.context, 'update_meal_plan'):
                    self.context.update_meal_plan(meal_plan.get("meals", []))
            
            # Generate AI explanation
            system_prompt = """You are a certified nutritionist and meal planning expert. 
            Create personalized meal recommendations based on the user's goals and preferences. 
            Provide practical, healthy meal suggestions with clear explanations of nutritional benefits.
            Include portion sizes and preparation tips when relevant."""
            
            if meal_plan:
                formatted_plan = self.response_formatter.format_meal_plan(meal_plan)
                ai_response = await self.get_ai_response(
                    f"Explain this meal plan and how it supports the user's goals: {meal_plan}",
                    system_prompt
                )
                
                return {
                    "message": ai_response,
                    "plan": formatted_plan,
                    "raw_plan": meal_plan
                }
            else:
                # Fallback meal planning
                ai_response = await self.get_ai_response(
                    f"Create a meal plan for someone with these goals: {self._get_user_goal_summary()}",
                    system_prompt
                )
                
                return {"message": ai_response}
            
        except Exception as e:
            print(f"Error in meal planning: {str(e)}")
            return {"message": "I'd be happy to help you create a meal plan! Let me know about your dietary preferences and any restrictions you have."}
    
    @async_error_handler()
    async def handle_workout_planning(self, message: str) -> Dict:
        """Handle workout planning requests with enhanced functionality."""
        try:
            # Check if user has a goal
            if not self._has_user_goal():
                return {
                    "message": "To create the most effective workout plan for you, I'd like to understand your fitness goals better! What would you like to achieve? (e.g., build muscle, lose weight, improve endurance, etc.)",
                    "needs_goal": True
                }
            
            # Use workout recommender tool
            workout_recommender = self.tool_manager.get_tool("workout_recommender")
            workout_plan = None
            
            if workout_recommender:
                user_goal = self.context_manager.get_context("current_goal", self.context.goal if self.context else None)
                workout_plan = await safe_async_call(
                    workout_recommender.run,
                    goal=user_goal
                )
                
                # Update context
                if workout_plan and self.context and hasattr(self.context, 'update_workout_plan'):
                    self.context.update_workout_plan(workout_plan)
            
            # Generate AI explanation
            system_prompt = """You are a certified fitness trainer and exercise specialist. 
            Create personalized workout recommendations based on the user's goals and fitness level. 
            Provide clear exercise instructions, proper form tips, and safety guidelines.
            Explain how each exercise contributes to their specific goals."""
            
            if workout_plan:
                formatted_plan = self.response_formatter.format_workout_plan(workout_plan)
                ai_response = await self.get_ai_response(
                    f"Explain this workout plan and how it helps achieve the user's goals: {workout_plan}",
                    system_prompt
                )
                
                return {
                    "message": ai_response,
                    "plan": formatted_plan,
                    "raw_plan": workout_plan
                }
            else:
                # Fallback workout planning
                ai_response = await self.get_ai_response(
                    f"Create a workout plan for someone with these goals: {self._get_user_goal_summary()}",
                    system_prompt
                )
                
                return {"message": ai_response}
            
        except Exception as e:
            print(f"Error in workout planning: {str(e)}")
            return {"message": "I'd be happy to help you create a workout plan! Let me know about your fitness level and any equipment you have access to."}
    
    @async_error_handler()
    async def handle_progress_tracking(self, message: str) -> Dict:
        """Handle progress tracking and check-ins."""
        try:
            system_prompt = """You are a supportive health coach focused on progress tracking. 
            Help the user reflect on their journey, celebrate achievements, and identify areas for improvement.
            Ask relevant questions about their recent activities, how they're feeling, and any challenges they're facing.
            Provide encouragement and practical advice for staying on track."""
            
            ai_response = await self.get_ai_response(message, system_prompt)
            
            return {
                "message": ai_response,
                "tracking_enabled": True
            }
            
        except Exception as e:
            print(f"Error in progress tracking: {str(e)}")
            return {"message": "I'd love to help you track your progress! Tell me about your recent activities and how you're feeling about your health journey."}
    
    def _has_user_goal(self) -> bool:
        """Check if user has set a goal."""
        if self.context and hasattr(self.context, 'goal') and self.context.goal:
            return True
        return self.context_manager.get_context("current_goal") is not None
    
    def _get_user_goal_summary(self) -> str:
        """Get a summary of the user's goal."""
        if self.context and hasattr(self.context, 'goal') and self.context.goal:
            return str(self.context.goal)
        
        goal_data = self.context_manager.get_context("current_goal")
        if goal_data and isinstance(goal_data, dict):
            return goal_data.get("goal", "general health improvement")
        
        return "general health and wellness"
    
    @async_error_handler()
    async def handle_message(self, message: str) -> Dict:
        """
        Enhanced main message handler with improved routing and error handling.
        """
        try:
            # Validate input
            if not validate_user_input(message):
                return {"message": "I didn't receive a valid message. Please try again with a clear question or request."}
            
            message = message.strip()
            
            # Classify message type
            message_type = self.message_classifier.classify_message(message)
            
            # Handle specialized requests first
            specialized_response = await self.handle_specialized_request(message, message_type)
            if specialized_response:
                return specialized_response
            
            # Route to appropriate handler
            if message_type == "goal":
                response = await self.handle_goal_setting(message)
            elif message_type == "nutrition":
                response = await self.handle_meal_planning(message)
            elif message_type == "fitness":
                response = await self.handle_workout_planning(message)
            elif message_type == "progress":
                response = await self.handle_progress_tracking(message)
            else:
                # Handle general health and wellness queries
                system_prompt = """You are a knowledgeable health and wellness expert. 
                Provide helpful, accurate, and motivating responses to health-related questions. 
                Keep responses friendly but professional, and always prioritize user's health and safety.
                If medical advice is needed, recommend consulting healthcare professionals."""
                
                ai_response = await self.get_ai_response(message, system_prompt)
                response = {"message": ai_response}
            
            # Store interaction in context
            self.context_manager.add_to_history(message, response.get("message", ""))
            
            return response
            
        except Exception as e:
            print(f"Error in handle_message: {str(e)}")
            print(f"Traceback: {traceback.format_exc()}")
            return {
                "message": "I apologize, but I'm experiencing some technical difficulties. Please try again or rephrase your question.",
                "error": True
            }

    async def run(self, message: str, context: UserSessionContext):
        # Input guardrail: goal analysis
        if validate_goal_string(message):
            result = await analyze_goal(goal_string=message)
            if "error" not in result:
                context.goal = result
            return result
        # Handoff triggers
        if "diabetic" in message or "allergy" in message or "nutrition" in message:
            return await self.specialized_agents["nutrition"].run(context, message)
        if "injury" in message or "pain" in message:
            return await self.specialized_agents["injury"].run(context, message)
        if "trainer" in message or "human" in message or "coach" in message:
            return await self.specialized_agents["escalation"].run(context, message)
        # Meal planner
        if "meal" in message or "diet" in message:
            if context.goal:
                return await meal_planner(goal=context.goal, diet_preferences=context.diet_preferences)
            else:
                return {"error": "Please specify your health goal first."}
        # Workout recommender
        if "workout" in message or "exercise" in message:
            if context.goal:
                return await workout_recommender(goal=context.goal)
            else:
                return {"error": "Please specify your health goal first."}
        # Check-in scheduler
        if "check-in" in message or "reminder" in message:
            return await checkin_scheduler(user_id=context.uid)
        # Progress tracker
        if "progress" in message or "update" in message:
            return await progress_tracker(user_id=context.uid, update=message)
        # Default: fallback to OpenAI chat
        messages = [
            {"role": "system", "content": "You are a helpful health and wellness assistant."},
            {"role": "user", "content": message}
        ]
        response = client.chat.completions.create(
            model="gpt-3.5-turbo-1106",
            messages=messages,
            temperature=0.7,
            max_tokens=500
        )
        return response.choices[0].message.content