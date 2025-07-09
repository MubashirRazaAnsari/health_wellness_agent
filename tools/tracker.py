from typing import Dict, List, Optional
from datetime import datetime
from config.settings import Settings
import json

class ProgressTrackerTool:
    name = "progress_tracker"
    description = "Tracks user progress and updates session context"

    def __init__(self):
        self.client = Settings.get_openai_client()

    async def get_ai_analysis(self, progress_entry: Dict) -> Dict:
        """Get AI analysis of progress data."""
        system_prompt = """You are a health and fitness progress analyst. Analyze the user's progress data and provide 
        insights and recommendations. The response should be a JSON object with the following structure:
        {
            "summary": {
                "on_track": boolean,
                "highlights": ["achievement 1", "achievement 2"],
                "areas_for_improvement": ["area 1", "area 2"]
            },
            "analysis": {
                "weight_trend": "analysis of weight changes",
                "workout_consistency": "analysis of workout completion",
                "diet_adherence": "analysis of diet adherence",
                "energy_patterns": "analysis of energy levels"
            },
            "recommendations": {
                "workout": ["specific workout adjustment 1", "adjustment 2"],
                "diet": ["specific diet adjustment 1", "adjustment 2"],
                "lifestyle": ["specific lifestyle adjustment 1", "adjustment 2"]
            },
            "next_milestones": ["milestone 1", "milestone 2"]
        }"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Analyze this progress data: {json.dumps(progress_entry)}"}
        ]

        model_config = Settings.get_model_config()
        response = self.client.chat.completions.create(
            model=model_config["model"],
            messages=messages,
            temperature=0.7,
            max_tokens=1500
        )

        try:
            # Parse the AI response as JSON
            analysis_data = json.loads(response.choices[0].message.content)
            return analysis_data
        except json.JSONDecodeError:
            # Fallback to basic structure
            return {
                "summary": {
                    "on_track": True,
                    "highlights": ["Tracking progress consistently"],
                    "areas_for_improvement": ["Need more data for detailed analysis"]
                },
                "analysis": {
                    "weight_trend": "Insufficient data for trend analysis",
                    "workout_consistency": "Regular workout participation noted",
                    "diet_adherence": "Maintaining consistent diet habits",
                    "energy_patterns": "Energy levels are stable"
                },
                "recommendations": {
                    "workout": ["Continue current routine", "Monitor progress"],
                    "diet": ["Maintain current habits", "Track portions"],
                    "lifestyle": ["Ensure adequate rest", "Stay hydrated"]
                },
                "next_milestones": ["Complete next week's check-in", "Review progress in detail"]
            }

    async def run(
        self,
        current_weight: Optional[float] = None,
        completed_workouts: Optional[List[str]] = None,
        diet_adherence: Optional[int] = None,
        energy_level: Optional[int] = None,
        notes: Optional[str] = None
    ) -> Dict:
        """
        Records and analyzes user progress.
        
        Args:
            current_weight: Current weight measurement
            completed_workouts: List of completed workout sessions
            diet_adherence: Diet adherence score (1-10)
            energy_level: Energy level score (1-10)
            notes: Additional progress notes
            
        Returns:
            Progress analysis and recommendations
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        progress_entry = {
            "timestamp": timestamp,
            "metrics": {
                "weight": current_weight,
                "completed_workouts": completed_workouts or [],
                "diet_adherence": diet_adherence,
                "energy_level": energy_level
            },
            "notes": notes
        }

        # Get AI analysis of progress
        analysis = await self.get_ai_analysis(progress_entry)

        return {
            "progress_entry": progress_entry,
            "analysis": analysis
        } 