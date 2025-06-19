import streamlit as st
import requests
import json

# ----------------------------
# Streamlit Config
# ----------------------------
st.set_page_config(page_title="📱 Gadget Advisor", page_icon="🤖")
st.title("🤖 Gadget Advisor")
st.markdown("Get expert help with phones, laptops, tablets, and other tech!")

# ----------------------------
# Hugging Face Inference API Setup
# ----------------------------
HF_TOKEN = st.secrets["HF_TOKEN"]  # Set this in Streamlit Cloud Secrets
MODEL = "mistralai/Mistral-7B-Instruct-v0.1"
API_URL = f"https://api-inference.huggingface.co/models/{MODEL}"

HEADERS = {
    "Authorization": f"Bearer {HF_TOKEN}",
    "Content-Type": "application/json"
}

# ----------------------------
# System Prompt
# ----------------------------
SYSTEM_PROMPT = """
You are a friendly and knowledgeable gadget expert assistant.

Help users pick electronics like smartphones, laptops, headphones, smartwatches, and tablets based on their needs (e.g., budget, use-case, features). Offer pros and cons, latest recommendations, and explain specs in simple terms. Be honest and helpful.
"""

# ----------------------------
# Get Response Function
# ----------------------------
def get_response(message):
    prompt = f"{SYSTEM_PROMPT}\nUser: {message}\nAssistant:"

    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 512,
            "temperature": 0.7
        }
    }

    try:
        response = requests.post(API_URL, headers=HEADERS, json=payload)
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list) and result:
                return result[0].get("generated_text", "").replace(prompt, "").strip()
            elif isinstance(result, dict):
                return result.get("generated_text", "").strip()
            else:
                return "⚠️ Unexpected response format."
        elif response.status_code == 503:
            return "⏳ Model is currently loading. Try again shortly."
        elif response.status_code == 401:
            return "🔒 Invalid or expired Hugging Face token."
        elif response.status_code == 404:
            return "❌ Model not found or not accessible."
        else:
            return f"❌ Error {response.status_code}: {response.text}"
    except Exception as e:
        return f"🚫 Request failed: {str(e)}"

# ----------------------------
# Chat UI
# ----------------------------
if "history" not in st.session_state:
    st.session_state.history = []

user_input = st.text_input("💬 Ask your question:", placeholder="e.g. Best phone under ₹30,000")
if st.button("Ask") and user_input:
    with st.spinner("Thinking..."):
        reply = get_response(user_input)
        st.session_state.history.append(("You", user_input))
        st.session_state.history.append(("Assistant", reply))
        st.rerun()

# ----------------------------
# Display History
# ----------------------------
if st.session_state.history:
    st.subheader("🧠 Chat History")
    for role, msg in reversed(st.session_state.history):
        st.markdown(f"**{role}:** {msg}")

# ----------------------------
# Footer
# ----------------------------
st.markdown("---")
st.markdown("🔌 Powered by Hugging Face + Mistral")
