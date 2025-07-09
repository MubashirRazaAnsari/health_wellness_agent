import asyncio
import functools
import traceback
from typing import Dict, Any, Optional, Callable, List
import logging
import datetime
import json
import os
from openai import OpenAI

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def async_error_handler(fallback_response: str = "I apologize, but I'm experiencing technical difficulties. Please try again."):
    """Decorator for handling async function errors gracefully."""
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                logger.error(f"Error in {func.__name__}: {str(e)}")
                logger.error(f"Traceback: {traceback.format_exc()}")
                
                # Return a structured response for agent methods
                if func.__name__.startswith('handle_'):
                    return {"message": fallback_response, "error": True}
                else:
                    return fallback_response
        return wrapper
    return decorator

def safe_tool_call(tool_method: Callable, *args, **kwargs) -> Optional[Any]:
    """Safely call a tool method and return None if it fails."""
    try:
        if asyncio.iscoroutinefunction(tool_method):
            return asyncio.run(tool_method(*args, **kwargs))
        else:
            return tool_method(*args, **kwargs)
    except Exception as e:
        logger.error(f"Tool call failed: {str(e)}")
        return None

class ToolManager:
    """Manages tool initialization and provides fallback functionality."""
    
    def __init__(self):
        self.tools = {}
        self.fallback_enabled = True
    
    def register_tool(self, name: str, tool_class: type, *args, **kwargs):
        """Register a tool with fallback handling."""
        try:
            self.tools[name] = tool_class(*args, **kwargs)
            logger.info(f"Tool '{name}' registered successfully")
        except Exception as e:
            logger.error(f"Failed to register tool '{name}': {str(e)}")
            self.tools[name] = None
    
    def get_tool(self, name: str):
        """Get a tool instance or None if not available."""
        return self.tools.get(name)
    
    def is_tool_available(self, name: str) -> bool:
        """Check if a tool is available and functional."""
        return self.tools.get(name) is not None
    
    async def call_tool(self, name: str, method: str, *args, **kwargs) -> Optional[Any]:
        """Safely call a tool method."""
        tool = self.get_tool(name)
        if tool is None:
            logger.warning(f"Tool '{name}' not available")
            return None
        
        try:
            method_func = getattr(tool, method)
            if asyncio.iscoroutinefunction(method_func):
                return await method_func(*args, **kwargs)
            else:
                return method_func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error calling {name}.{method}: {str(e)}")
            return None

class ResponseFormatter:
    """Formats responses for better user experience."""
    
    @staticmethod
    def format_meal_plan(meal_plan: Dict) -> str:
        """Format meal plan data for display."""
        if not meal_plan:
            return "I couldn't generate a meal plan right now. Please try again."
        
        formatted = "🍽️ **Your Personalized Meal Plan**\n\n"
        
        if "meals" in meal_plan:
            for meal_type, meal_info in meal_plan["meals"].items():
                formatted += f"**{meal_type.title()}:**\n"
                if isinstance(meal_info, dict):
                    for key, value in meal_info.items():
                        formatted += f"• {key}: {value}\n"
                else:
                    formatted += f"• {meal_info}\n"
                formatted += "\n"
        
        if "nutrition" in meal_plan:
            formatted += "📊 **Nutrition Information:**\n"
            nutrition = meal_plan["nutrition"]
            if isinstance(nutrition, dict):
                for key, value in nutrition.items():
                    formatted += f"• {key}: {value}\n"
            else:
                formatted += f"• {nutrition}\n"
        
        return formatted
    
    @staticmethod
    def format_workout_plan(workout_plan: Dict) -> str:
        """Format workout plan data for display."""
        if not workout_plan:
            return "I couldn't generate a workout plan right now. Please try again."
        
        formatted = "💪 **Your Personalized Workout Plan**\n\n"
        
        if "exercises" in workout_plan:
            formatted += "**Exercises:**\n"
            exercises = workout_plan["exercises"]
            if isinstance(exercises, list):
                for exercise in exercises:
                    if isinstance(exercise, dict):
                        name = exercise.get("name", "Unknown Exercise")
                        sets = exercise.get("sets", "N/A")
                        reps = exercise.get("reps", "N/A")
                        formatted += f"• **{name}**: {sets} sets × {reps} reps\n"
                    else:
                        formatted += f"• {exercise}\n"
            else:
                formatted += f"• {exercises}\n"
            formatted += "\n"
        
        if "duration" in workout_plan:
            formatted += f"⏱️ **Duration:** {workout_plan['duration']}\n"
        
        if "frequency" in workout_plan:
            formatted += f"📅 **Frequency:** {workout_plan['frequency']}\n"
        
        if "notes" in workout_plan:
            formatted += f"📝 **Notes:** {workout_plan['notes']}\n"
        
        return formatted
    
    @staticmethod
    def format_goal_analysis(goal_data: Dict) -> str:
        """Format goal analysis data for display."""
        if not goal_data:
            return "I couldn't analyze your goal right now. Please try again."
        
        formatted = "🎯 **Goal Analysis**\n\n"
        
        if "goal" in goal_data:
            formatted += f"**Your Goal:** {goal_data['goal']}\n\n"
        
        if "type" in goal_data:
            formatted += f"**Goal Type:** {goal_data['type']}\n\n"
        
        if "timeline" in goal_data:
            formatted += f"**Timeline:** {goal_data['timeline']}\n\n"
        
        if "steps" in goal_data:
            formatted += "**Action Steps:**\n"
            steps = goal_data["steps"]
            if isinstance(steps, list):
                for i, step in enumerate(steps, 1):
                    formatted += f"{i}. {step}\n"
            else:
                formatted += f"• {steps}\n"
        
        return formatted

class MessageClassifier:
    """Classifies user messages to determine appropriate handling."""
    
    @staticmethod
    def classify_message(message: str) -> str:
        """Classify a message into categories."""
        message_lower = message.lower()
        
        # Goal-related
        goal_keywords = ["goal", "target", "objective", "want to", "trying to", "aim to", "hope to"]
        if any(keyword in message_lower for keyword in goal_keywords):
            return "goal"
        
        # Nutrition-related
        nutrition_keywords = ["meal", "food", "diet", "nutrition", "eat", "recipe", "calories", "diabetic", "allergy"]
        if any(keyword in message_lower for keyword in nutrition_keywords):
            return "nutrition"
        
        # Fitness-related
        fitness_keywords = ["workout", "exercise", "fitness", "training", "gym", "cardio", "strength", "muscle"]
        if any(keyword in message_lower for keyword in fitness_keywords):
            return "fitness"
        
        # Progress-related
        progress_keywords = ["progress", "track", "check-in", "update", "how am i doing", "results"]
        if any(keyword in message_lower for keyword in progress_keywords):
            return "progress"
        
        # Injury/health-related
        injury_keywords = ["injury", "pain", "hurt", "sore", "strain", "sprain", "recovery", "medical"]
        if any(keyword in message_lower for keyword in injury_keywords):
            return "injury"
        
        # General health
        health_keywords = ["health", "wellness", "healthy", "tips", "advice", "help"]
        if any(keyword in message_lower for keyword in health_keywords):
            return "health"
        
        return "general"

class ConfigManager:
    """Manages configuration and settings with OpenRouter support."""
    
    DEFAULT_CONFIG = {
        "model": {
            "provider": "openrouter",
            "available_models": [
                "mistralai/mistral-7b-instruct:free",
                "meta-llama/llama-2-13b-chat:free",
                "openchat/openchat-7b:free",
                "phind/phind-codellama-34b:free"
            ],
            "default_model": "mistralai/mistral-7b-instruct:free",
            "temperature": 0.7,
            "max_tokens": 500
        },
        "openrouter": {
            "api_key": None,
            "api_base": "https://openrouter.ai/api/v1",
            "referer": "https://github.com/OpenRouterTeam/openrouter-python",
            "headers": {
                "HTTP-Referer": "https://github.com/OpenRouterTeam/openrouter-python",
                "X-Title": "Health Agent"
            }
        },
        "response_limits": {
            "max_retries": 3,
            "timeout": 30
        },
        "features": {
            "meal_planning": True,
            "workout_planning": True,
            "goal_setting": True,
            "progress_tracking": True
        }
    }
    
    def __init__(self, config_path: Optional[str] = None):
        self.config = self.DEFAULT_CONFIG.copy()
        self.config_path = config_path
        self.load_config()
        self._init_openrouter()
    
    def load_config(self):
        """Load configuration from file and environment."""
        try:
            # Load from file if exists
            if self.config_path and os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    file_config = json.load(f)
                    self.config.update(file_config)
            
            # Override with environment variables if present
            self._load_from_env()
            
        except Exception as e:
            logger.warning(f"Could not load config from {self.config_path}: {str(e)}")
    
    def _load_from_env(self):
        """Load configuration from environment variables."""
        # OpenRouter settings
        if os.getenv("OPENROUTER_API_KEY"):
            self.config["openrouter"]["api_key"] = os.getenv("OPENROUTER_API_KEY")
        
        if os.getenv("OPENROUTER_API_BASE"):
            self.config["openrouter"]["api_base"] = os.getenv("OPENROUTER_API_BASE")
        
        # Model settings
        if os.getenv("DEFAULT_MODEL"):
            self.config["model"]["default_model"] = os.getenv("DEFAULT_MODEL")
    
    def _init_openrouter(self):
        """Initialize OpenRouter client configuration."""
        try:
            api_key = self.config["openrouter"]["api_key"]
            if not api_key:
                api_key = os.getenv("OPENROUTER_API_KEY")
                if not api_key:
                    raise ValueError("OpenRouter API key not found in config or environment")
            
            self.openai_client = OpenAI(
                api_key=api_key,
                base_url=self.config["openrouter"]["api_base"],
                default_headers=self.config["openrouter"]["headers"]
            )
            
            logger.info("OpenRouter client initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize OpenRouter client: {str(e)}")
            self.openai_client = None
    
    def get_ai_client(self) -> Optional[OpenAI]:
        """Get the OpenRouter client."""
        return self.openai_client
    
    def get_current_model(self) -> str:
        """Get the current model name."""
        return self.config["model"]["default_model"]
    
    def get_available_models(self) -> List[str]:
        """Get list of available models."""
        return self.config["model"]["available_models"]
    
    def set_model(self, model_name: str) -> bool:
        """Set the current model if it's available."""
        if model_name in self.get_available_models():
            self.config["model"]["default_model"] = model_name
            return True
        return False
    
    def get(self, key: str, default=None):
        """Get configuration value."""
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value
    
    def set(self, key: str, value: Any):
        """Set configuration value."""
        keys = key.split('.')
        config_ref = self.config
        for k in keys[:-1]:
            if k not in config_ref:
                config_ref[k] = {}
            config_ref = config_ref[k]
        config_ref[keys[-1]] = value
        
        # Reinitialize OpenRouter client if relevant settings changed
        if keys[0] == "openrouter" or (keys[0] == "model" and keys[-1] == "default_model"):
            self._init_openrouter()

class ContextManager:
    """Manages user context and session state."""
    
    def __init__(self):
        self.context = {}
        self.session_history = []
    
    def update_context(self, key: str, value: Any):
        """Update context with new information."""
        self.context[key] = value
        logger.info(f"Context updated: {key}")
    
    def get_context(self, key: str, default=None):
        """Get context value."""
        return self.context.get(key, default)
    
    def add_to_history(self, message: str, response: str):
        """Add interaction to history."""
        self.session_history.append({
            "message": message,
            "response": response,
            "timestamp": datetime.datetime.now().isoformat()
        })
        
        # Keep only last 50 interactions
        if len(self.session_history) > 50:
            self.session_history = self.session_history[-50:]
    
    def get_recent_context(self, limit: int = 5) -> str:
        """Get recent conversation context."""
        if not self.session_history:
            return ""
        
        recent = self.session_history[-limit:]
        context_str = "Recent conversation:\n"
        for interaction in recent:
            context_str += f"User: {interaction['message'][:100]}...\n"
            context_str += f"Assistant: {interaction['response'][:100]}...\n\n"
        
        return context_str

# Utility functions
async def safe_async_call(func: Callable, *args, **kwargs) -> Optional[Any]:
    """Safely call an async function with error handling."""
    try:
        return await func(*args, **kwargs)
    except Exception as e:
        logger.error(f"Async call failed: {str(e)}")
        return None

def validate_user_input(message: str) -> bool:
    """Validate user input for safety and appropriateness."""
    if not message or len(message.strip()) == 0:
        return False
    
    if len(message) > 1000:  # Limit message length
        return False
    
    # Add more validation as needed
    return True

def sanitize_response(response: str) -> str:
    """Sanitize AI response for safety."""
    # Basic sanitization - expand as needed
    if not response:
        return "I apologize, but I couldn't generate a proper response. Please try again."
    
    # Remove potentially harmful content
    sensitive_patterns = ["http://", "https://", "www.", "@", "password", "login"]
    for pattern in sensitive_patterns:
        if pattern in response.lower():
            logger.warning(f"Potentially sensitive content detected: {pattern}")
    
    return response 

    