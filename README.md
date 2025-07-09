# Health & Wellness Planner Agent

An AI-powered health and wellness planner that helps users achieve their fitness goals through personalized meal plans, workout recommendations, and expert advice.

## Features

- Natural language goal setting and analysis
- Personalized meal planning with dietary preferences
- Custom workout recommendations based on experience level
- Injury-aware exercise modifications
- Specialized nutrition advice for specific conditions
- Progress tracking and regular check-ins

## Project Structure

```
health_wellness_agent/
├── main.py                 # Application entry point
├── agent.py               # Main agent implementation
├── context.py             # User session context
├── guardrails.py          # Input/output validation
├── tools/                 # Agent tools
│   ├── goal_analyzer.py
│   ├── meal_planner.py
│   └── workout_recommender.py
├── agents/                # Specialized agents
│   ├── nutrition_expert_agent.py
│   └── injury_support_agent.py
└── requirements.txt       # Project dependencies
```

## Installation

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the example conversation flow:

```bash
python main.py
```

Example interaction:

```python
agent = HealthWellnessAgent()
await agent.initialize_session("UserName", 1)
response = await agent.handle_message("My goal is to lose 5kg in 2 months")
```

## Features in Detail

### Goal Analysis
- Parses natural language goal descriptions
- Validates goal format and metrics
- Structures goals for planning

### Meal Planning
- Generates 7-day meal plans
- Considers dietary preferences and restrictions
- Includes shopping lists and macronutrient breakdowns

### Workout Recommendations
- Creates personalized exercise plans
- Adapts to user experience level
- Provides form guidance and modifications

### Specialized Support
- Nutrition Expert Agent for dietary conditions
- Injury Support Agent for exercise modifications
- Seamless handoffs between specialized agents

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request


##.env 
OPENAI_API_KEY=your_actual_key_here
JWT_SECRET=your_actual_secret_here
ENCRYPTION_KEY=your_actual_key_here


## License

This project is licensed under the MIT License - see the LICENSE file for details. 