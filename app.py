import streamlit as st
import requests

# --- Config ---
st.set_page_config(page_title="📱 Gadget Advisor", page_icon="🤖")
st.title("🤖 Gadget Advisor")
st.markdown("Get helpful, unbiased electronic recommendations.")

# --- HF config ---
HF_TOKEN = st.secrets["HF_TOKEN"]  # Add to Streamlit secrets
MODEL = "mistralai/Mistral-7B-Instruct-v0.1"
API_URL = f"https://api-inference.huggingface.co/models/{MODEL}"
HEADERS = {
    "Authorization": f"Bearer {HF_TOKEN}",
    "Content-Type": "application/json"
}

# --- Prompt setup ---
SYSTEM_PROMPT = """
You are a gadget advisor who recommends smartphones, laptops, and electronics. Be clear, concise, friendly, and focus on actual suggestions, comparisons, and pros/cons. Always assume the latest market in 2025.
"""

def query_model(user_message):
    full_prompt = f"[INST] {SYSTEM_PROMPT}\nUser: {user_message} [/INST]"
    payload = {
        "inputs": full_prompt,
        "parameters": {
            "temperature": 0.7,
            "max_new_tokens": 512,
            "return_full_text": False
        }
    }
    res = requests.post(API_URL, headers=HEADERS, json=payload)
    if res.status_code == 200:
        return res.json()[0]['generated_text'].strip()
    elif res.status_code == 503:
        return "⏳ Model is loading. Try again soon."
    elif res.status_code == 401:
        return "🔒 Invalid HF token."
    else:
        return f"❌ Error: {res.status_code}"

# --- Chat history ---
if "chat" not in st.session_state:
    st.session_state.chat = []

user_input = st.text_input("Ask about gadgets:", placeholder="Best phones under ₹30K?")

if st.button("Ask") and user_input:
    with st.spinner("Thinking..."):
        answer = query_model(user_input)
        st.session_state.chat.append((user_input, answer))
        st.rerun()

# --- Show chat ---
for q, a in reversed(st.session_state.chat):
    st.markdown(f"**You:** {q}")
    st.markdown(f"**Assistant:** {a}")
