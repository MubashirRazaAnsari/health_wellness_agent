import os
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

class Settings:
    """Application settings and configuration management."""

    @staticmethod
    def get_required_env(key: str) -> str:
        """Get a required environment variable or raise an error."""
        value = os.getenv(key)
        if value is None:
            raise ValueError(f"Missing required environment variable: {key}")
        return value

    @staticmethod
    def get_optional_env(key: str, default: str = "") -> str:
        """Get an optional environment variable with a default value."""
        return os.getenv(key, default)

    @classmethod
    def get_openai_config(cls) -> Dict[str, str]:
        """Get OpenAI API configuration."""
        return {
            "api_key": cls.get_required_env("OPENAI_API_KEY"),
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
settings = Settings() 