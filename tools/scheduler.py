from typing import Dict, List
from datetime import datetime, timedelta

class CheckinSchedulerTool:
    name = "checkin_scheduler"
    description = "Schedules recurring weekly progress checks"

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

        schedule = {
            "frequency": f"Every {frequency_days} days",
            "next_checkins": next_dates,
            "reminder_time": "09:00 AM",
            "check_items": [
                "Weight measurement",
                "Progress photos",
                "Workout completion rate",
                "Diet adherence",
                "Energy levels",
                "Any challenges faced"
            ],
            "notification_preferences": {
                "email": True,
                "push": True,
                "sms": False
            }
        }

        return schedule 