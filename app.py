import streamlit as st
import requests

# Streamlit UI setup
st.set_page_config(page_title="Gadget Advisor", page_icon="🤖")
st.title("🤖 Ask Gadget Advisor")
st.markdown("Get expert help choosing electronics like phones, laptops, and tablets.")

# Hugging Face Token from Streamlit secrets
HF_API_TOKEN = st.secrets["HF_API_TOKEN"]
API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.1"

HEADERS = {
    "Authorization": f"Bearer {HF_API_TOKEN}",
    "Content-Type": "application/json"
}

# Custom system prompt
SYSTEM_PROMPT = """
You are Gadget Advisor, an expert AI assistant that helps users choose phones, tablets, and laptops.
Always include detailed specs (processor, RAM, battery, camera, display) and recommend based on budget, use-case, and quality.
Be clear, helpful, and friendly.
"""

# Get user input
user_input = st.text_input("Ask your question (e.g., Best phone under ₹30,000):")

if st.button("Ask") and user_input:
    with st.spinner("Thinking..."):
        final_prompt = f"{SYSTEM_PROMPT}\n\nUser: {user_input}\n\nAssistant:"

        response = requests.post(
            API_URL,
            headers=HEADERS,
            json={"inputs": final_prompt}
        )

        if response.status_code == 200:
            result = response.json()
            reply = result[0]["generated_text"].split("Assistant:")[-1].strip()
            st.success(reply)
        else:
            st.error(f"❌ Error: {response.status_code} - {response.text}")
