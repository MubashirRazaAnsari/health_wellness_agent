from typing import Optional, List, Dict
from pydantic import BaseModel

class UserSessionContext(BaseModel):
    name: str
    uid: int
    goal: Optional[dict] = None
    diet_preferences: Optional[str] = None
    workout_plan: Optional[dict] = None
    meal_plan: Optional[List[str]] = None
    injury_notes: Optional[str] = None
    handoff_logs: List[str] = []
    progress_logs: List[Dict[str, str]] = []

    def update_goal(self, goal: dict):
        self.goal = goal

    def update_diet_preferences(self, preferences: str):
        self.diet_preferences = preferences

    def update_workout_plan(self, plan: dict):
        self.workout_plan = plan

    def update_meal_plan(self, plan: List[str]):
        self.meal_plan = plan

    def add_injury_note(self, note: str):
        self.injury_notes = note

    def log_handoff(self, message: str):
        self.handoff_logs.append(message)

    def log_progress(self, progress: Dict[str, str]):
        self.progress_logs.append(progress) 