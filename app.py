import streamlit as st
import requests

# Streamlit UI setup
st.set_page_config(page_title="Gadget Advisor", page_icon="🤖")
st.title("🤖 Ask Gadget Advisor")
st.markdown("Get expert help choosing electronics like phones, laptops, and tablets.")

# Hugging Face Token from Streamlit Secrets
HF_API_TOKEN = st.secrets["HF_API_TOKEN"]
API_URL = "https://api-inference.huggingface.co/models/meta-llama/Llama-3-70b-instruct"

HEADERS = {
    "Authorization": f"Bearer {HF_API_TOKEN}",
    "Content-Type": "application/json"
}

# Custom system prompt for domain expertise
SYSTEM_PROMPT = """
You are Gadget Advisor, a helpful and knowledgeable assistant that helps users choose the right electronic devices such as phones, tablets, and laptops.
Always respond with detailed specifications like processor, RAM, display, battery life, and camera features.
Then provide clear and honest recommendations based on user needs (budget, purpose, brand preferences).
Use a friendly, professional tone suitable for both tech-savvy and non-tech users.
"""

# Get user input
user_input = st.text_input("Ask your question (e.g., Best phone under ₹30,000 with good camera):")

if st.button("Ask") and user_input:
    with st.spinner("Thinking..."):
        final_prompt = f"{SYSTEM_PROMPT}\n\nUser: {user_input}\n\nAssistant:"

        response = requests.post(
            API_URL,
            headers=HEADERS,
            json={"inputs": final_prompt}
        )

        if response.status_code == 200:
            try:
                result = response.json()
                reply = result[0]["generated_text"].split("Assistant:")[-1].strip()
                st.success(reply)
            except Exception:
                st.error("✅ Model worked, but could not parse response correctly.")
        else:
            st.error(f"❌ Error: {response.status_code} - {response.text}")
