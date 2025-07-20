import streamlit as st
from agent import get_wellness_response

st.set_page_config(page_title="College Mental Wellness Assistant", page_icon="🧠")

st.title("🧠 College Mental Wellness Assistant")
st.write("I'm here to support your mental wellness. How can I help you today?")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

def submit():
    user_input = st.session_state.user_input
    if user_input.strip():
        response = get_wellness_response(user_input)
        st.session_state.chat_history.append(("You", user_input))
        st.session_state.chat_history.append(("Assistant", response))
        st.session_state.user_input = ""  # This is safe inside on_change



for sender, message in st.session_state.chat_history:
    if sender == "You":
        st.markdown(f"**You:** {message}")
    else:
        st.markdown(f"**Assistant:** {message}")
st.text_input("You:", key="user_input", on_change=submit)