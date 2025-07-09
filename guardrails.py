from typing import Dict, List, Optional, Union
from pydantic import BaseModel, Field, validator
import re

class GoalInput(BaseModel):
    goal_type: str = Field(..., description="Type of goal (e.g., 'weight_loss', 'muscle_gain', 'endurance')")
    target_value: float = Field(..., description="Numeric target value")
    unit: str = Field(..., description="Unit of measurement")
    duration_weeks: int = Field(..., description="Duration in weeks")
    
    @validator('goal_type')
    def validate_goal_type(cls, v):
        valid_types = ['weight_loss', 'muscle_gain', 'endurance', 'flexibility', 'strength']
        if v.lower() not in valid_types:
            raise ValueError(f"Goal type must be one of {valid_types}")
        return v.lower()

    @validator('unit')
    def validate_unit(cls, v):
        valid_units = ['kg', 'lbs', 'km', 'miles', 'minutes']
        if v.lower() not in valid_units:
            raise ValueError(f"Unit must be one of {valid_units}")
        return v.lower()

class DietaryInput(BaseModel):
    preferences: List[str] = Field(..., description="List of dietary preferences")
    restrictions: List[str] = Field(default_factory=list, description="List of dietary restrictions")
    allergies: List[str] = Field(default_factory=list, description="List of food allergies")

    @validator('preferences')
    def validate_preferences(cls, v):
        valid_preferences = ['vegetarian', 'vegan', 'pescatarian', 'keto', 'paleo', 'mediterranean']
        for pref in v:
            if pref.lower() not in valid_preferences:
                raise ValueError(f"Invalid dietary preference: {pref}")
        return [p.lower() for p in v]

class WorkoutPlan(BaseModel):
    exercises: List[Dict[str, Union[str, int, float]]]
    duration_minutes: int
    difficulty: str
    equipment_needed: List[str]

    @validator('difficulty')
    def validate_difficulty(cls, v):
        valid_difficulties = ['beginner', 'intermediate', 'advanced']
        if v.lower() not in valid_difficulties:
            raise ValueError(f"Difficulty must be one of {valid_difficulties}")
        return v.lower()

class MealPlan(BaseModel):
    meals: List[Dict[str, Union[str, List[str], int]]]
    total_calories: int
    macros: Dict[str, float]
    shopping_list: List[str]

def validate_goal_string(goal_string: str) -> bool:
    """Validates if a goal string matches the expected format."""
    pattern = r'^(lose|gain)\s+\d+(\.\d+)?\s*(kg|lbs)\s+in\s+\d+\s+(weeks?|months?)$'
    return bool(re.match(pattern, goal_string.lower()))

def validate_injury_input(injury_description: str) -> bool:
    """Validates if an injury description contains necessary information."""
    required_info = ['location', 'pain level', 'duration']
    return all(info.lower() in injury_description.lower() for info in required_info) 