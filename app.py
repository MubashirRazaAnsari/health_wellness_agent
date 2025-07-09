import streamlit as st
import asyncio
from agent import HealthWellnessAgent
from utils.streaming import Runner

# Initialize session state
if 'agent' not in st.session_state:
    st.session_state.agent = HealthWellnessAgent()
    st.session_state.initialized = False
    st.session_state.messages = []

async def process_message(message: str):
    """Process a message and update the chat history."""
    response = await st.session_state.agent.handle_message(message)
    st.session_state.messages.append({"role": "user", "content": message})
    st.session_state.messages.append({"role": "assistant", "content": response["message"]})
    if "plan" in response:
        st.session_state.messages.append({"role": "assistant", "content": str(response["plan"])})

def main():
    st.set_page_config(
        page_title="Health & Wellness Planner",
        page_icon="🏋️‍♂️",
        layout="wide"
    )

    st.title("🏋️‍♂️ Health & Wellness Planner 🥗")

    # Sidebar for user information and settings
    with st.sidebar:
        st.header("Profile Settings")
        if not st.session_state.initialized:
            with st.form("user_info"):
                name = st.text_input("Your Name")
                age = st.number_input("Age", min_value=18, max_value=100)
                height = st.number_input("Height (cm)", min_value=100, max_value=250)
                weight = st.number_input("Current Weight (kg)", min_value=30, max_value=200)
                
                fitness_level = st.selectbox(
                    "Fitness Level",
                    ["Beginner", "Intermediate", "Advanced"]
                )
                
                dietary_prefs = st.multiselect(
                    "Dietary Preferences",
                    ["Vegetarian", "Vegan", "Pescatarian", "Gluten-free", "Dairy-free", "No restrictions"]
                )

                if st.form_submit_button("Start Journey"):
                    # Initialize agent session
                    asyncio.run(st.session_state.agent.initialize_session(name, hash(name) % 10000))
                    st.session_state.initialized = True
                    st.experimental_rerun()

        if st.session_state.initialized:
            st.success("Profile Active ✅")
            if st.button("View Progress"):
                st.write("Progress tracking coming soon!")

    # Main chat interface
    if st.session_state.initialized:
        # Display chat history
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])

        # Quick action buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Get Meal Plan"):
                asyncio.run(process_message("I'd like a meal plan please"))
                st.experimental_rerun()
            if st.button("Track Progress"):
                asyncio.run(process_message("I want to track my progress"))
                st.experimental_rerun()
        with col2:
            if st.button("Get Workout Plan"):
                asyncio.run(process_message("Can you give me a workout plan?"))
                st.experimental_rerun()
            if st.button("Schedule Check-in"):
                asyncio.run(process_message("I'd like to schedule a check-in"))
                st.experimental_rerun()

        # Chat input
        if prompt := st.chat_input("What would you like to know?"):
            asyncio.run(process_message(prompt))
            st.experimental_rerun()

    else:
        st.info("👈 Please complete your profile in the sidebar to get started!")

    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center'>
            <p>Made with ❤️ for your health and wellness journey</p>
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main() 