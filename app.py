import streamlit as st
import requests

# Your Hugging Face Assistant details
ASSISTANT_ID = "6852ecc9aa34895faa80b436"
HF_API_TOKEN = st.secrets["HF_API_TOKEN"]
  # Paste your token from HF

API_URL = f"https://api-inference.huggingface.co/chat/assistants/6852ecc9aa34895faa80b436"
HEADERS = {
    "Authorization": f"Bearer {HF_API_TOKEN}",
    "Content-Type": "application/json"
}

# Streamlit UI setup
st.set_page_config(page_title="Gadget Advisor", page_icon="📱")
st.title("🤖 Ask Gadget Advisor")
st.markdown("Get expert help choosing electronics like phones, laptops, and tablets.")

user_prompt = st.text_input("Ask a question:")

if st.button("Ask") and user_prompt:
    with st.spinner("Thinking..."):
        response = requests.post(
            API_URL,
            headers=HEADERS,
            json={"inputs": {"text": user_prompt}}
        )

        if response.status_code == 200:
            output = response.json()
            st.success(output.get("generated_text", "No response received."))
        else:
            st.error(f"Error: {response.status_code} - {response.text}")
