import streamlit as st
import requests
import json

# --- Page Config ---
st.set_page_config(page_title="Gadget Advisor", page_icon="📱")
st.title("🤖 Gadget Advisor AI")
st.markdown("Ask about smartphones, laptops, earbuds, tablets, and more!")

# --- System Prompt ---
SYSTEM_PROMPT = """
You are a professional and friendly gadget advisor. Your role is to recommend the best electronic gadgets based on user needs.

You specialize in smartphones, laptops, headphones, tablets, smartwatches, gaming gear, cameras, and smart home devices.

Instructions:
- Suggest specific products with names and features.
- Consider user budget and use-case (e.g., gaming, office work, student).
- Explain differences when comparing options.
- Always be honest and up-to-date.
- Mention pros and cons when possible.
- If you don’t know something, say so politely.
"""

# --- Hugging Face Config ---
MODEL = "HuggingFaceH4/zephyr-7b-beta"
HF_TOKEN = st.secrets.get("HF_TOKEN", "")

if not HF_TOKEN:
    st.error("❌ Please add your HF_TOKEN to Streamlit secrets!")
    st.stop()

API_URL = f"https://api-inference.huggingface.co/models/{MODEL}"
HEADERS = {
    "Authorization": f"Bearer {HF_TOKEN}",
    "Content-Type": "application/json"
}

# --- Chat History ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- Input ---
user_input = st.text_input("Ask a gadget question:", placeholder="e.g., Best phone under ₹30000")

def format_prompt(history, user_input):
    prompt = f"System: {SYSTEM_PROMPT}\n\n"
    for msg in history:
        role = "Human" if msg["role"] == "user" else "Assistant"
        prompt += f"{role}: {msg['content']}\n"
    prompt += f"Human: {user_input}\nAssistant:"
    return prompt

if st.button("Ask") and user_input:
    full_prompt = format_prompt(st.session_state.chat_history, user_input)
    
    response = requests.post(API_URL, headers=HEADERS, json={
        "inputs": full_prompt,
        "parameters": {
            "max_new_tokens": 512,
            "temperature": 0.7,
            "do_sample": True,
            "return_full_text": False
        }
    })

    if response.status_code == 200:
        result = response.json()
        reply = result[0]["generated_text"].strip()
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        st.session_state.chat_history.append({"role": "assistant", "content": reply})
        st.markdown(f"**Assistant:** {reply}")
    else:
        st.error(f"Error {response.status_code}: {response.text}")

# --- Display Chat History ---
if st.session_state.chat_history:
    st.markdown("---")
    st.subheader("🕘 Chat History")
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

st.markdown("---")
st.markdown("Powered by Hugging Face • Model: Zephyr-7B Beta")
