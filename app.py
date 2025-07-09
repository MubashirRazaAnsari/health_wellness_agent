"""
Streamlit interface for the Health & Wellness Agent.
"""
import streamlit as st
import asyncio
from typing import Dict, Any, Optional
import os
from dotenv import load_dotenv

from agent import HealthWellnessAgent
from context import UserSessionContext
from hooks import RunHooks, AgentHooks

# Load environment variables
load_dotenv()

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "agent" not in st.session_state:
    st.session_state.agent = None

if "context" not in st.session_state:
    st.session_state.context = None

if "user_name" not in st.session_state:
    st.session_state.user_name = None

if "user_id" not in st.session_state:
    st.session_state.user_id = None

async def process_message(agent: HealthWellnessAgent, message: str, context: UserSessionContext) -> str:
    """Process a message and return the response."""
    try:
        full_response = ""
        message_placeholder = st.empty()
        
        # Get the response iterator
        response_iterator = await agent.get_streaming_response(message, context)
        if not response_iterator:
            return "I apologize, but I'm having trouble generating a response. Please try again."
        
        # Process chunks as they arrive
        async for chunk in response_iterator:
            if isinstance(chunk, dict):
                if "tool_call" in chunk:
                    # Format tool calls with better visual separation
                    full_response += f"\n\n🔧 **Using {chunk['tool_call']}...**\n\n"
                elif "tool_result" in chunk:
                    result = chunk["tool_result"]
                    if isinstance(result, dict):
                        # Format dictionary results with better structure
                        full_response += "\n\n📊 **Results:**\n"
                        for key, value in result.items():
                            if value:  # Only show non-empty values
                                # Format key as title case and make it bold
                                formatted_key = key.replace('_', ' ').title()
                                full_response += f"* **{formatted_key}:** {value}\n"
                        full_response += "\n"  # Add extra line break after results
                    elif isinstance(result, list):
                        # Format list results with proper numbering
                        full_response += "\n\n📊 **Results:**\n"
                        for i, item in enumerate(result, 1):
                            if isinstance(item, dict):
                                # Handle dictionary items in list
                                full_response += f"{i}. "
                                for k, v in item.items():
                                    formatted_key = k.replace('_', ' ').title()
                                    full_response += f"**{formatted_key}:** {v}, "
                                full_response = full_response.rstrip(", ") + "\n"
                            else:
                                full_response += f"{i}. {item}\n"
                        full_response += "\n"
                    else:
                        # Format string results with proper spacing
                        full_response += f"\n\n📊 **Results:**\n{result}\n\n"
            elif isinstance(chunk, str) and chunk.strip():
                # Handle regular text chunks
                text = chunk.strip()
                
                # Check if it's a numbered list item
                if text.startswith(("1.", "2.", "3.", "4.", "5.", "6.", "7.", "8.", "9.", "0.")):
                    full_response += f"\n{text}"
                # Check if it's a bullet point
                elif text.startswith("*"):
                    full_response += f"\n{text}"
                # Check if it's a header (markdown style)
                elif text.startswith("#"):
                    full_response += f"\n\n{text}\n"
                # Regular text - preserve spacing but avoid double spaces
                else:
                    if not full_response.endswith("\n") and not full_response.endswith(" "):
                        full_response += " "
                    full_response += text
            
            # Update the display in real-time
            if st.session_state.messages:
                # Clean up any multiple line breaks
                display_response = full_response.replace("\n\n\n", "\n\n").strip()
                st.session_state.messages[-1]["content"] = display_response
                message_placeholder.markdown(display_response)
        
        # Final cleanup of the response
        final_response = full_response.replace("\n\n\n", "\n\n").strip()
        return final_response
        
    except Exception as e:
        error_msg = f"Error processing message: {str(e)}"
        print(error_msg)  # Log the error
        return "❌ I apologize, but I encountered an error while processing your request. Please try again."

def main():
    st.set_page_config(
        page_title="Health & Wellness Agent",
        page_icon="🏥",
        layout="wide"
    )

    st.title("🏥 Health & Wellness Agent")

    # Sidebar for user information
    with st.sidebar:
        st.header("User Information")
        if not st.session_state.user_name:
            with st.form("user_info"):
                name = st.text_input("Your Name")
                submit = st.form_submit_button("Start Session")
                if submit and name:
                    st.session_state.user_name = name
                    st.session_state.user_id = hash(name)  # Simple user ID generation
                    # Initialize agent and context
                    st.session_state.agent = HealthWellnessAgent(
                        config_path="config/agent_config.json",
                        run_hooks=RunHooks(),
                        agent_hooks=AgentHooks("MainAgent")
                    )
                    st.session_state.context = UserSessionContext(
                        name=name,
                        uid=st.session_state.user_id
                    )
                    st.rerun()
        else:
            st.write(f"Welcome, {st.session_state.user_name}! 👋")
            if st.button("End Session"):
                for key in st.session_state.keys():
                    del st.session_state[key]
                st.rerun()

    # Main chat interface
    if st.session_state.user_name:
        # Display chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Chat input
        if prompt := st.chat_input("What's on your mind?"):
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            # Create a placeholder for the assistant's response
            with st.chat_message("assistant"):
                response = asyncio.run(process_message(
                    st.session_state.agent,
                    prompt,
                    st.session_state.context
                ))
                if response:
                    st.session_state.messages.append({"role": "assistant", "content": response})
    else:
        st.info("👈 Please enter your information in the sidebar to start.")

if __name__ == "__main__":
    main()