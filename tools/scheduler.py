from typing import Dict, List
from datetime import datetime, timedelta
from config.settings import Settings
import json

class CheckinSchedulerTool:
    name = "checkin_scheduler"
    description = "Schedules recurring weekly progress checks"

    def __init__(self):
        self.client = Settings.get_openai_client()

    async def get_ai_schedule(self, frequency_days: int) -> Dict:
        """Get AI-optimized schedule and check-in items."""
        system_prompt = """You are a health and fitness scheduling expert. Create an optimized check-in schedule and 
        comprehensive list of check items based on the given frequency. The response should be a JSON object with the 
        following structure:
        {
            "check_items": {
                "measurements": ["measurement 1", "measurement 2"],
                "progress_tracking": ["tracking item 1", "tracking item 2"],
                "feedback": ["feedback item 1", "feedback item 2"]
            },
            "reminder_schedule": {
                "primary_time": "HH:MM",
                "backup_time": "HH:MM",
                "timezone_handling": "timezone strategy"
            },
            "notification_strategy": {
                "channels": ["channel1", "channel2"],
                "message_templates": ["template1", "template2"]
            },
            "accountability": ["accountability measure 1", "measure 2"]
        }"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Create an optimized check-in schedule for every {frequency_days} days"}
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
            schedule_data = json.loads(response.choices[0].message.content)
            return schedule_data
        except json.JSONDecodeError:
            # Fallback to basic structure
            return {
                "check_items": {
                    "measurements": ["Weight", "Body measurements"],
                    "progress_tracking": ["Workout completion", "Diet adherence"],
                    "feedback": ["Energy levels", "Challenges faced"]
                },
                "reminder_schedule": {
                    "primary_time": "09:00",
                    "backup_time": "18:00",
                    "timezone_handling": "Use local device time"
                },
                "notification_strategy": {
                    "channels": ["email", "push", "in_app"],
                    "message_templates": ["Time for your check-in!", "Don't forget to track your progress"]
                },
                "accountability": ["Share with accountability partner", "Weekly progress summary"]
            }

    async def run(self, frequency_days: int = 7) -> Dict:
        """
        Schedules recurring check-ins for progress tracking.
        
        Args:
            frequency_days: Number of days between check-ins
            
        Returns:
            Schedule information and next check-in dates
        """
        now = datetime.now()
        next_dates = [
            (now + timedelta(days=i * frequency_days)).strftime("%Y-%m-%d")
            for i in range(1, 5)  # Schedule next 4 check-ins
        ]

        # Get AI-optimized schedule
        schedule_data = await self.get_ai_schedule(frequency_days)

        schedule = {
            "frequency": f"Every {frequency_days} days",
            "next_checkins": next_dates,
            "reminder_time": schedule_data["reminder_schedule"]["primary_time"],
            "backup_time": schedule_data["reminder_schedule"]["backup_time"],
            "check_items": [
                *schedule_data["check_items"]["measurements"],
                *schedule_data["check_items"]["progress_tracking"],
                *schedule_data["check_items"]["feedback"]
            ],
            "notification_preferences": {
                "channels": schedule_data["notification_strategy"]["channels"],
                "templates": schedule_data["notification_strategy"]["message_templates"]
            },
            "accountability_measures": schedule_data["accountability"]
        }

        return schedule 