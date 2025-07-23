from typing import Dict

async def progress_tracker(user_id: int, update: str) -> Dict:
    # In a real system, this would update progress in a DB or context
    return {"message": f"Progress updated for user {user_id}: {update}"}

progress_tracker.schema = {
    "name": "progress_tracker",
    "description": "Accepts updates, tracks user progress, modifies session context.",
    "parameters": {
        "type": "object",
        "properties": {
            "user_id": {"type": "integer", "description": "User's unique ID"},
            "update": {"type": "string", "description": "Progress update text"}
        },
        "required": ["user_id", "update"]
    }
} 