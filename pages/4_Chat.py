import streamlit as st
import sys
import os
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.auth import ensure_authenticated, get_current_user, render_auth_status
from utils.groq_helper import chat_with_dietician
from utils.storage import append_to_user_bucket_list, load_user_bucket, update_user_bucket
from utils.ui import apply_base_theme

st.set_page_config(page_title="Chat with AI Dietician", page_icon="💬", layout="centered")
apply_base_theme()
ensure_authenticated()
render_auth_status()

active_user = get_current_user()

st.title("💬 Chat with AI Dietician")
st.caption("Ask anything about diet, nutrition, and healthy eating!")

st.divider()

# --- Profile context ---
profile = st.session_state.get('profile', None)

if profile:
    st.success(f"✅ Chatting as **{profile['name']}** — responses are personalized for you!")
else:
    st.info("💡 Fill your profile first for personalized advice! Chatting in general mode.")

st.divider()

# --- Initialize chat history ---
if st.session_state.get("chat_loaded_for") != active_user:
    st.session_state.pop("chat_history", None)

if "chat_history" not in st.session_state:
    saved_history = load_user_bucket(active_user).get("chat_history", [])
    if saved_history:
        st.session_state.chat_history = saved_history
    else:
        st.session_state.chat_history = [
            {
                "role": "assistant",
                "content": "Namaste! 🙏 Main aapka AI Dietician hoon! Kya aap apni diet ke baare mein kuch poochna chahte hain? Main Indian food, nutrition, weight loss, ya kisi bhi health goal mein help kar sakta hoon! 😊"
            }
        ]
    st.session_state["chat_loaded_for"] = active_user

# --- Quick Question Buttons ---
st.markdown("**⚡ Quick Questions:**")
quick_questions = [
    "What should I eat for weight loss?",
    "Best Indian protein sources?",
    "Healthy Indian breakfast ideas?",
    "How many calories in my daily meals?"
]

cols = st.columns(2)
for i, question in enumerate(quick_questions):
    with cols[i % 2]:
        if st.button(question, use_container_width=True, key=f"quick_{i}"):
            st.session_state.pending_message = question

st.divider()

# --- Display Chat History ---
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- Handle pending quick question ---
if "pending_message" in st.session_state:
    user_input = st.session_state.pending_message
    del st.session_state.pending_message

    # Add user message
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Get AI response
    with st.chat_message("assistant"):
        with st.spinner("🤔 Thinking..."):
            response = chat_with_dietician(
                user_input,
                st.session_state.chat_history[:-1],
                profile
            )
        st.markdown(response)

    st.session_state.chat_history.append({"role": "assistant", "content": response})
    update_user_bucket(active_user, {"chat_history": st.session_state.chat_history})
    st.rerun()

# --- Sidebar: chat actions ---
with st.sidebar:
    st.markdown("### 💬 Chat Actions")
    chat_export = "\n\n".join(
        [f"{msg['role'].title()}: {msg['content']}" for msg in st.session_state.chat_history]
    )
    st.download_button(
        "📥 Export Chat",
        data=chat_export,
        file_name="aaharai_chat_history.txt",
        mime="text/plain",
        use_container_width=True,
    )
    if st.button("💾 Save Snapshot", use_container_width=True):
        append_to_user_bucket_list(
            active_user,
            "chat_snapshots",
            {
                "saved_at": datetime.now().strftime("%d %b %Y, %H:%M"),
                "message_count": len(st.session_state.chat_history),
                "messages": st.session_state.chat_history,
            },
            limit=10,
        )
        st.success("Chat snapshot saved.")
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.chat_history = [
            {
                "role": "assistant",
                "content": "Namaste! 🙏 Main aapka AI Dietician hoon! Kya aap apni diet ke baare mein kuch poochna chahte hain? 😊"
            }
        ]
        update_user_bucket(active_user, {"chat_history": st.session_state.chat_history})
        st.rerun()

# --- Chat Input (must be last — renders sticky at bottom) ---
user_input = st.chat_input("Apna sawaal poochein... (Ask your question...)")

if user_input:
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("🤔 Thinking..."):
            response = chat_with_dietician(
                user_input,
                st.session_state.chat_history[:-1],
                profile
            )
        st.markdown(response)

    st.session_state.chat_history.append({"role": "assistant", "content": response})
    update_user_bucket(active_user, {"chat_history": st.session_state.chat_history})
