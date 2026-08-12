import os
import time
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

from safety import is_safe
from evaluation import evaluate_response
from logger import log_interaction

# ----------------------------------------------------
# Load API
# ----------------------------------------------------
load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

MODEL = "openai/gpt-4o-mini"

# ----------------------------------------------------
# Streamlit Page
# ----------------------------------------------------
st.set_page_config(
    page_title="Gemini Style AI",
    page_icon="🤖",
    layout="wide"
)

# ----------------------------------------------------
# CSS (Gemini Style)
# ----------------------------------------------------
st.markdown("""
<style>

html, body, [class*="css"]{
    background:#131314;
    color:white;
    font-family:Arial;
}

header{
    visibility:hidden;
}

footer{
    visibility:hidden;
}

#MainMenu{
    visibility:hidden;
}

section[data-testid="stSidebar"]{
    background:#1E1F20;
}

.chat-user{
    background:#303134;
    padding:14px;
    border-radius:18px;
    margin:10px;
}

.chat-ai{
    background:#1E1F20;
    padding:14px;
    border-radius:18px;
    margin:10px;
}

.title{
    font-size:34px;
    font-weight:bold;
    color:white;
    margin-bottom:20px;
}

.small{
    color:gray;
    font-size:13px;
}

</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------
# Title
# ----------------------------------------------------
st.markdown("<div class='title'>✨ Responsible AI </div>", unsafe_allow_html=True)

# ----------------------------------------------------
# Session State
# ----------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages=[]

# ----------------------------------------------------
# Sidebar
# ----------------------------------------------------
with st.sidebar:

    st.title("🤖 Responsible AIS")

    if st.button("➕ New Chat"):

        st.session_state.messages=[]

        st.rerun()

    st.divider()

    st.subheader("History")

    for m in st.session_state.messages:

        if m["role"]=="user":
            st.write("👤",m["content"][:30])

# ----------------------------------------------------
# OpenRouter Function
# ----------------------------------------------------
def ask_ai(prompt):

    response=client.chat.completions.create(

        model=MODEL,

        messages=[
            {
                "role":"system",
                "content":"You are a helpful, safe and responsible AI assistant."
            },

            {
                "role":"user",
                "content":prompt
            }
        ],

        temperature=0.7,

        max_tokens=400

    )

    return response.choices[0].message.content

# ----------------------------------------------------
# Display Messages
# ----------------------------------------------------
for msg in st.session_state.messages:

    if msg["role"]=="user":

        with st.chat_message("user"):

            st.markdown(msg["content"])

    else:

        with st.chat_message("assistant"):

            st.markdown(msg["content"])

# ----------------------------------------------------
# Chat Input
# ----------------------------------------------------
prompt=st.chat_input("Ask Gemini...")

if prompt:

    st.session_state.messages.append(
        {
            "role":"user",
            "content":prompt
        }
    )

    with st.chat_message("user"):

        st.markdown(prompt)

    # ---------------- Safety ----------------

    if not is_safe(prompt):

        reply=(
            "I'm sorry that you're going through something difficult.\n\n"
            "Please consider talking to someone you trust or a mental health professional."
        )

        quality="Unsafe Prompt"

        elapsed=0

    else:

        start=time.time()

        try:

            with st.chat_message("assistant"):

                placeholder=st.empty()

                typing=""

                for ch in "Thinking...":

                    typing+=ch

                    placeholder.markdown(typing+"▌")

                    time.sleep(0.05)

                reply=ask_ai(prompt)

                placeholder.markdown(reply)

        except Exception as e:

            reply=f"API Error:\n{e}"

        elapsed=time.time()-start

        quality=evaluate_response(reply)

    log_interaction(
        prompt,
        reply,
        quality,
        elapsed
    )

    st.session_state.messages.append(
        {
            "role":"assistant",
            "content":reply
        }
    )

    st.caption(f"Quality : {quality}   |   Response Time : {elapsed:.2f} sec")