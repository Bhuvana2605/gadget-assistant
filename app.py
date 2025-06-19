import streamlit as st
import requests

st.set_page_config(page_title="📱 Gadget Advisor", page_icon="🤖")
st.title("🤖 Gadget Advisor")
st.markdown("Ask me for gadget recommendations!")

HF_TOKEN = st.secrets["HF_TOKEN"]
MODEL = "microsoft/Phi-3-mini-4k-instruct"
API_URL = f"https://api-inference.huggingface.co/models/{MODEL}"

HEADERS = {
    "Authorization": f"Bearer {HF_TOKEN}",
    "Content-Type": "application/json"
}

SYSTEM_PROMPT = """
You are a gadget expert assistant. Recommend electronics like smartphones, laptops, tablets, etc., based on user needs and budgets. Explain clearly with pros and cons. Be honest and up-to-date.
"""

def query_model(user_message):
    full_prompt = f"{SYSTEM_PROMPT}\nUser: {user_message}\nAssistant:"
    payload = {
        "inputs": full_prompt,
        "parameters": {
            "temperature": 0.7,
            "max_new_tokens": 500,
            "return_full_text": False
        }
    }
    res = requests.post(API_URL, headers=HEADERS, json=payload)
    if res.status_code == 200:
        return res.json()[0]["generated_text"].strip()
    elif res.status_code == 401:
        return "🔒 Invalid Hugging Face Token"
    elif res.status_code == 503:
        return "⏳ Model is still loading. Try again in a moment."
    elif res.status_code == 404:
        return "❌ Model not found. Please use a supported model."
    else:
        return f"❌ Error: {res.status_code}"

if "chat" not in st.session_state:
    st.session_state.chat = []

user_input = st.text_input("Ask about gadgets:", placeholder="Best phone under ₹30,000?")
if st.button("Ask") and user_input:
    with st.spinner("Thinking..."):
        response = query_model(user_input)
        st.session_state.chat.append((user_input, response))
        st.rerun()

if st.session_state.chat:
    for q, a in reversed(st.session_state.chat):
        st.markdown(f"**You:** {q}")
        st.markdown(f"**Assistant:** {a}")
