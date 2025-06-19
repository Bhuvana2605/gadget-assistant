import streamlit as st
import requests

st.set_page_config(page_title="🎯 Gadget Assistant", page_icon="🤖")
st.title("🤖 Ask My AI Assistant")
st.markdown("Talk to your Hugging Face Assistant for gadget recommendations!")

# Get secrets
HF_TOKEN = st.secrets["HF_TOKEN"]
ASSISTANT_ID = st.secrets["6852ecc9aa34895faa80b436"]

API_URL = f"https://api.huggingface.co/chat/assistants/6852ecc9aa34895faa80b436/messages"
HEADERS = {
    "Authorization": f"Bearer {HF_TOKEN}",
    "Content-Type": "application/json"
}

# Store the conversation
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# User input
user_input = st.text_input("Ask anything about electronics:")

if st.button("Send") and user_input:
    with st.spinner("Thinking..."):
        payload = {
            "inputs": {
                "messages": st.session_state.chat_history + [{"role": "user", "content": user_input}]
            }
        }
        response = requests.post(API_URL, headers=HEADERS, json=payload)

        if response.status_code == 200:
            result = response.json()
            assistant_message = result.get("generated_message", {}).get("content", "")
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            st.session_state.chat_history.append({"role": "assistant", "content": assistant_message})
        else:
            st.error(f"❌ Error {response.status_code}: {response.text}")

# Display chat history
for msg in st.session_state.chat_history:
    role = "🧑 You" if msg["role"] == "user" else "🤖 Assistant"
    st.markdown(f"**{role}:** {msg['content']}")
