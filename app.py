import os
import streamlit as st
from google import genai
from google.genai import types

# 1. Initialize the Gemini Client
# The SDK automatically picks up the GEMINI_API_KEY environment variable
if "GEMINI_API_KEY" not in os.environ:
    st.error("Please set your GEMINI_API_KEY environment variable.")
    st.stop()

client = genai.Client()

# 2. Configure the Streamlit UI
st.set_page_config(page_title="AI Interview Coach", page_icon="💼")
st.title("💼 AI General Interview Coach")
st.write("Welcome! I am your interactive interviewer. I will ask you standard behavioral and situational questions, evaluate your answers, and guide you to success.")

# 3. Define the System Instructions (The Chatbot's Persona)
SYSTEM_INSTRUCTION = (
    "You are an expert corporate job interviewer and career coach. Your goal is to conduct "
    "a general-purpose mock interview with the user. Ask one question at a time. "
    "When the user responds, briefly evaluate their answer (point out what was good, "
    "and give 1-2 constructive tips for improvement, mentioning the STAR method if relevant). "
    "Then, transition smoothly to the next general interview question. Keep your tone "
    "professional, encouraging, and constructive."
)

# 4. Initialize Session State for Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []
    
    # Let the AI kick off the conversation with a welcoming question
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents="Introduce yourself briefly as the interviewer and ask the first classic interview question.",
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION
            )
        )
        st.session_state.messages.append({"role": "assistant", "content": response.text})
    except Exception as e:
        st.error(f"Error connecting to Gemini API: {e}")

# 5. Display Past Chat Messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# 6. Handle User Input
if user_input := st.chat_input("Type your response here..."):
    # Display user message in chat message container
    with st.chat_message("user"):
        st.write(user_input)
    # Add user message to session history
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Prepare the full history for the API call to maintain context
    api_contents = []
    for msg in st.session_state.messages:
        # Map roles to what the Gemini API expects ('user' or 'model')
        api_role = 'model' if msg["role"] == 'assistant' else 'user'
        api_contents.append(
            types.Content(
                role=api_role,
                parts=[types.Part.from_text(text=msg["content"])]
            )
        )

    # Generate the AI's response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        with st.spinner("Analyzing your response..."):
            try:
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=api_contents,
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_INSTRUCTION
                    )
                )
                ai_response = response.text
                message_placeholder.write(ai_response)
                # Add assistant message to session history
                st.session_state.messages.append({"role": "assistant", "content": ai_response})
            except Exception as e:
                st.error(f"An error occurred: {e}")
