# Health & Wellness Planner Agent

## Overview
This project implements a fully functional AI-powered Health & Wellness Planner Agent using the official OpenAI SDK and best practices. The agent can:
- Collect user fitness and dietary goals through multi-turn natural language conversation
- Analyze goals and generate structured health plans (meal/workout)
- Use context and state to remember past conversations and progress
- Stream responses to users in real time
- Apply input/output guardrails for safety and structure
- Handle handoffs to specialized agents (e.g., Nutrition Expert, Injury Support)
- (Optionally) Use lifecycle hooks for logging and tracking

## Folder Structure
```
health_wellness_agent/
├── main.py
├── agent.py
├── context.py
├── guardrails.py
├── hooks.py
├── tools/
│   ├── goal_analyzer.py
│   ├── meal_planner.py
│   ├── workout_recommender.py
│   ├── scheduler.py
│   ├── tracker.py
├── agents/
│   ├── escalation_agent.py
│   ├── nutrition_expert_agent.py
│   └── injury_support_agent.py
├── utils/
│   └── streaming.py
└── README.md
```

## Usage
1. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```
2. Set your OpenAI API key in a `.env` file or as an environment variable:
   ```env
   OPENAI_API_KEY=sk-...
   ```
3. Run the agent:
   ```bash
   python main.py
   ```
4. Interact with the agent via the CLI.

## Features
- **Agent + Tool Creation:** Tools are async functions with schemas, registered for function-calling.
- **State Management:** Context is tracked in a Pydantic model and passed to all tools/agents.
- **Guardrails:** Input (regex) and output (Pydantic) validation for safety and structure.
- **Real-Time Streaming:** (Optional) Use OpenAI streaming API for real-time responses.
- **Handoff to Specialized Agents:** Nutrition, Injury, Escalation agents handle special cases.
- **Lifecycle Hooks:** (Optional) Add hooks in `hooks.py` for logging and tracking.

## Adding New Tools or Agents
- **Tools:**
  - Create an async function in `tools/` with a `.schema` attribute.
  - Register it in `agent.py`.
- **Agents:**
  - Create a class with an async `run()` method in `agents/`.
  - Register it in `agent.py` for handoff logic.

## Example User Journey
```
User: I want to lose 5kg in 2 months
-> GoalAnalyzerTool extracts structured goal
User: I’m vegetarian
-> MealPlannerTool provides meal plan
User: I have knee pain
-> Handoff to InjurySupportAgent
User: I’m also diabetic
-> Handoff to NutritionExpertAgent
User: I want to talk to a real trainer
-> EscalationAgent handoff is triggered
```

## Requirements
- Python 3.11 recommended
- OpenAI SDK
- Pydantic

---

For more details, see the code and comments in each file.

