import re
from typing import Dict, List, Any
from pydantic import BaseModel, ValidationError

# Input guardrail: validate goal string

def validate_goal_string(goal_string: str) -> bool:
    pattern = r'^(lose|gain)\s+\d+(\.\d+)?\s*(kg|lbs)\s+in\s+\d+\s+(weeks?|months?)$'
    return bool(re.match(pattern, goal_string.lower()))

# Output guardrails: Pydantic models
class GoalOutput(BaseModel):
    goal_type: str
    target_value: float
    unit: str
    duration_weeks: int
    sub_goals: List[str]
    recommendations: List[str]
    risk_factors: List[str]

class MealPlanOutput(BaseModel):
    meals: List[Dict[str, Any]]
    total_calories: int
    macros: Dict[str, float]
    shopping_list: List[str]

class WorkoutPlanOutput(BaseModel):
    exercises: List[Dict[str, Any]]
    duration_minutes: int
    difficulty: str
    equipment_needed: List[str] 