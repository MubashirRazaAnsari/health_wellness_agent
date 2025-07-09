import os
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from openai import OpenAI

print("Debug: Starting settings initialization...")



# Try to load from .env file if it exists
env_path = Path(__file__).parent.parent / '.env'
print(f"Debug: Looking for .env file at: {env_path}")
if env_path.exists():
    print("Debug: Found .env file, loading...")
    load_dotenv(env_path)
else:
    print("Debug: No .env file found")

class Settings:
    """Application settings and configuration management."""
    
    _openai_client: Optional[OpenAI] = None

    @staticmethod
    def get_required_env(key: str) -> str:
        """Get a required environment variable or raise an error."""
        print(f"Debug: Attempting to get required env var: {key}")
        value = os.getenv(key)
        print(f"Debug: Value for {key}: {'<not set>' if value is None else value[:10] + '...' if len(value) > 10 else value}")
        if value is None or value.strip() == "":
            raise ValueError(f"Missing required environment variable: {key}")
        return value

    @staticmethod
    def get_optional_env(key: str, default: str = "") -> str:
        """Get an optional environment variable with a default value."""
        print(f"Debug: Getting optional env var: {key}")
        return os.getenv(key, default)

    @classmethod
    def get_openai_config(cls) -> Dict[str, str]:
        """Get OpenAI/Openrouter API configuration."""
        print("Debug: Getting OpenAI config...")
        return {
            "api_key": cls.get_required_env("OPENROUTER_API_KEY"),
            "base_url": "https://openrouter.ai/api/v1",
            "app_name": cls.get_optional_env("APP_NAME", "HealthAgent"),
            "site_url": cls.get_optional_env("SITE_URL", "http://localhost:8501"),
            "model": cls.get_optional_env("AI_MODEL", "mistralai/mistral-7b-instruct:free"),
            "temperature": float(cls.get_optional_env("AI_TEMPERATURE", "0.7")),
            "max_tokens": int(cls.get_optional_env("AI_MAX_TOKENS", "500"))
        }

    @classmethod
    def get_openai_client(cls) -> OpenAI:
        """Get configured OpenAI client instance."""
        print("Debug: Getting OpenAI client...")
        if cls._openai_client is None:
            config = cls.get_openai_config()
            cls._openai_client = OpenAI(
                api_key=config["api_key"],
                base_url=config["base_url"],
                default_headers={
                    "HTTP-Referer": config["site_url"],
                    "X-Title": config["app_name"]
                }
            )
        return cls._openai_client

    @classmethod
    def get_model_config(cls) -> Dict[str, Any]:
        """Get AI model configuration."""
        config = cls.get_openai_config()
        return {
            "model": config["model"],
            "temperature": config["temperature"],
            "max_tokens": config["max_tokens"]
        }

    @classmethod
    def get_email_config(cls) -> Dict[str, str]:
        """Get email service configuration."""
        return {
            "service": cls.get_optional_env("EMAIL_SERVICE", "smtp.gmail.com"),
            "port": cls.get_optional_env("EMAIL_PORT", "587"),
            "user": cls.get_optional_env("EMAIL_USER"),
            "password": cls.get_optional_env("EMAIL_PASSWORD"),
        }

    @classmethod
    def get_notification_config(cls) -> Dict[str, str]:
        """Get notification service configuration."""
        return {
            "push_key": cls.get_optional_env("PUSH_NOTIFICATION_KEY"),
            "sms_key": cls.get_optional_env("SMS_API_KEY"),
        }

    @classmethod
    def get_security_config(cls) -> Dict[str, str]:
        """Get security configuration."""
        return {
            "jwt_secret": cls.get_required_env("JWT_SECRET"),
            "encryption_key": cls.get_required_env("ENCRYPTION_KEY"),
        }

    @classmethod
    def get_all_config(cls) -> Dict[str, Any]:
        """Get all configuration settings."""
        return {
            "openai": cls.get_openai_config(),
            "email": cls.get_email_config(),
            "notifications": cls.get_notification_config(),
            "security": cls.get_security_config(),
        }

# Create a settings instance
print("Debug: Creating settings instance...")
settings = Settings() 