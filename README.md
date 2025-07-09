# Health & Wellness Planner Agent 🏥

An AI-powered health and wellness planning assistant that helps users achieve their fitness goals through personalized recommendations and real-time interaction.

## 🌟 Features

- 💬 Natural language conversation with real-time streaming responses
- 🎯 Goal analysis and structured health plan generation
- 🍽️ Personalized meal planning with dietary preferences
- 💪 Custom workout recommendations based on fitness level
- 📊 Progress tracking and scheduled check-ins
- 🔄 Context-aware responses that remember your preferences
- 🏥 Specialized agents for nutrition and injury support
- 📱 Beautiful Streamlit web interface

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- pip package manager
- OpenRouter API key (get one at [openrouter.ai](https://openrouter.ai))

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd health_agent
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp sample.env .env
```
Edit `.env` and add your OpenRouter API key:
```
OPENROUTER_API_KEY=your_api_key_here
```

### Running the Application

1. Start the Streamlit interface:
```bash
streamlit run app.py
```

2. Or use the CLI interface:
```bash
python main.py
```

## 🛠️ Project Structure

```
health_wellness_agent/
├── main.py              # CLI entry point
├── app.py              # Streamlit web interface
├── agent.py            # Core agent implementation
├── context.py          # Session context management
├── guardrails.py       # Input/output validation
├── hooks.py            # Lifecycle hooks
├── tools/              # Tool implementations
│   ├── goal_analyzer.py
│   ├── meal_planner.py
│   ├── workout_recommender.py
│   ├── scheduler.py
│   └── tracker.py
├── agents/             # Specialized agents
│   ├── nutrition_expert_agent.py
│   ├── injury_support_agent.py
│   └── escalation_agent.py
├── utils/              # Utility functions
│   ├── agent_utils.py
│   └── streaming.py
└── config/             # Configuration files
    ├── agent_config.json
    └── settings.py
```

## 💡 Usage Examples

1. Setting a health goal:
```
You: I want to lose 5kg in 2 months
Agent: [Analyzes goal and provides structured plan]
```

2. Getting a meal plan:
```
You: I need a vegetarian meal plan
Agent: [Creates personalized meal plan considering preferences]
```

3. Workout recommendations:
```
You: I want to start strength training
Agent: [Provides beginner-friendly workout plan]
```

4. Special considerations:
```
You: I have a knee injury
Agent: [Hands off to injury support specialist]
```

## 🔒 Safety & Privacy

- Input validation prevents harmful commands
- Output sanitization ensures safe responses
- No personal health data is stored permanently
- All interactions are ephemeral and session-based

## 📚 Documentation

For more detailed documentation on:
- Tool development
- Agent customization
- Guardrails configuration
- Lifecycle hooks
- Streaming implementation

Please refer to the [docs/](docs/) directory.

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guidelines](CONTRIBUTING.md) for details on how to submit pull requests.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This agent is for informational purposes only and should not replace professional medical advice. Always consult healthcare professionals for medical decisions.

