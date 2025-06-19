import streamlit as st
import requests

# Streamlit UI
st.set_page_config(page_title="Gadget Advisor", page_icon="🤖")
st.title("🤖 Ask Gadget Advisor")
st.markdown("Get expert help choosing electronics like phones, laptops, and tablets.")

# Hugging Face Token from Streamlit secrets
HF_API_TOKEN = st.secrets["HF_API_TOKEN"]
API_URL = "https://api-inference.huggingface.co/models/Qwen/Qwen2.5-VL-32B-Instruct"

HEADERS = {
    "Authorization": f"Bearer {HF_API_TOKEN}",
    "Content-Type": "application/json"
}

# System prompt
SYSTEM_PROMPT = """
You are Gadget Advisor, an AI expert who helps users choose the right electronics such as phones, tablets, and laptops.
Always respond with detailed specs like processor, RAM, display, camera, battery, and software.
Then give a recommendation based on their needs.
Be concise, honest, and helpful.
"""

# User input
user_input = st.text_input("Ask your question (e.g., Best laptop for students under ₹50,000):")

if st.button("Ask") and user_input:
    with st.spinner("Thinking..."):
        prompt = f"{SYSTEM_PROMPT}\n\nUser: {user_input}\n\nAssistant:"

        response = requests.post(
            API_URL,
            headers=HEADERS,
            json={"inputs": prompt}
        )

        if response.status_code == 200:
            try:
                reply = response.json()[0]["generated_text"].split("Assistant:")[-1].strip()
                st.success(reply)
            except Exception as e:
                st.error("Could not parse response correctly.")
        else:
            st.error(f"Error: {response.status_code} - {response.text}")
