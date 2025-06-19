import streamlit as st
import requests
import json

# ----------------------------
# Streamlit App Config
# ----------------------------
st.set_page_config(page_title="📱 Gadget Assistant", page_icon="🤖")
st.title("🤖 Gadget Advisor")
st.markdown("Your smart assistant for electronics recommendations and advice.")

# ----------------------------
# Constants
# ----------------------------
HF_TOKEN = "YOUR_HUGGINGFACE_API_TOKEN"  # 🔁 Replace with your token
MODEL = "mistralai/Mistral-7B-Instruct-v0.1"
API_URL = f"https://api-inference.huggingface.co/models/{MODEL}"
HEADERS = {
    "Authorization": f"Bearer {HF_TOKEN}",
    "Content-Type": "application/json"
}

# ----------------------------
# System Prompt for the Assistant
# ----------------------------
SYSTEM_PROMPT = """
You are a helpful and knowledgeable gadget advisor. You assist users in choosing the best electronic devices — including smartphones, laptops, tablets, smartwatches, and more.

Always consider the user’s needs such as budget, usage (e.g., gaming, work, photography), and preferences (e.g., battery life, camera quality, performance). Provide detailed but easy-to-understand explanations of device specifications like processor, RAM, camera setup, display type, battery, and software.

Compare models clearly when asked, and suggest the best options available in the market as of 2025. Be honest and unbiased — highlight both pros and cons.

Your tone is friendly, professional, and trustworthy. You do not fake information — if you're unsure, explain that and suggest how the user could verify it.
"""

# ----------------------------
# Helper Functions
# ----------------------------
def get_response_from_mistral(user_message):
    full_prompt = f"[INST] {SYSTEM_PROMPT}\n{user_message} [/INST]"
    payload = {
        "inputs": full_prompt,
        "parameters": {
            "max_new_tokens": 500,
            "temperature": 0.7
        }
    }

    try:
        response = requests.post(API_URL, headers=HEADERS, json=payload)
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list):
                return result[0]['generated_text'].replace(full_prompt, "").strip()
            elif 'generated_text' in result:
                return result['generated_text'].strip()
            else:
                return "⚠️ Unexpected response format."
        elif response.status_code == 503:
            return "⏳ Model is loading on Hugging Face. Try again shortly."
        elif response.status_code == 401:
            return "🔒 Unauthorized. Please check your Hugging Face token."
        else:
            return f"❌ Error {response.status_code}: {response.text}"
    except Exception as e:
        return f"🚫 Request failed: {str(e)}"

# ----------------------------
# Chat UI
# ----------------------------
if "history" not in st.session_state:
    st.session_state.history = []

user_input = st.text_input("Ask about a gadget:", placeholder="What's the best phone under ₹30,000?")
if st.button("Ask") and user_input:
    with st.spinner("Thinking..."):
        reply = get_response_from_mistral(user_input)
        st.session_state.history.append((user_input, reply))
        st.experimental_rerun()

# ----------------------------
# Display Chat History
# ----------------------------
if st.session_state.history:
    st.subheader("💬 Chat History")
    for q, a in reversed(st.session_state.history):
        st.markdown(f"**You:** {q}")
        st.markdown(f"**Assistant:** {a}")

# ----------------------------
# Footer
# ----------------------------
st.markdown("---")
st.markdown("Built with ❤️ using Streamlit and Mistral")
