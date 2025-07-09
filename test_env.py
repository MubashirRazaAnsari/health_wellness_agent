import os
import streamlit as st

st.write("Environment Variables Test")
st.write("OPENROUTER_API_KEY:", os.getenv("OPENROUTER_API_KEY", "Not set"))
st.write("JWT_SECRET:", os.getenv("JWT_SECRET", "Not set"))
st.write("APP_NAME:", os.getenv("APP_NAME", "Not set")) 