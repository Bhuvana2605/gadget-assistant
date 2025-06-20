import streamlit as st
import requests
import os

# ----------------------------
# App Setup
# ----------------------------
st.set_page_config(page_title="📱 Gadget Assistant", page_icon="🤖")
st.title("🤖 Gadget Advisor")
st.markdown("Ask about phones, laptops, tablets, or any gadgets. Get expert help instantly!")

# ----------------------------
# System Prompt
# ----------------------------
SYSTEM_PROMPT = """You are AIRA, a helpful and knowledgeable AI assistant that helps users choose the best electronic gadgets such as smartphones, laptops, tablets, etc., based on their budget, use-case, and personal preferences.

Your tone is friendly, clear, and concise. Your goal is to make the user feel confident in their buying decision, especially if they are confused or unsure.

Always follow this response format:
1. Ask clarifying questions (if needed) about budget, use-case (e.g. gaming, office, college), and preferences (e.g. battery life, camera, display).
2. Present recommendations as **bullet points** for easy reading.
3. For each recommended device, give:
   - Device Name
   - Key Features
   - Pros
   - Cons
4. End by asking: “Would you like more options or details on any of these?”

**Response Style Guidelines:**
- Use clear bullet points (• or -) for all lists and comparisons.
- Avoid big paragraphs. Be brief, helpful, and structured.
- Only include products that are available in the market and suitable for the user’s region and budget.
- Avoid technical jargon unless the user is advanced or requests it.
- Be neutral — do not favor a brand unless the user does.

DO:
- Tailor every response to the user’s needs.
- Suggest 2–3 top products.
- Explain why each device might be a good fit.

DON’T:
- Give random or outdated suggestions.
- Speak in long paragraphs.
- Use overly technical terms unless necessary.

Your goal: Help users quickly compare and confidently choose a device.
"""

# ----------------------------
# Conversation History
# ----------------------------
if "chat" not in st.session_state:
    st.session_state.chat = []

# ----------------------------
# OpenRouter API Call (Mistral)
# ----------------------------
def query_mistral(prompt):
    headers = {
        "Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "mistralai/mistral-7b-instruct",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 600
    }

    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"].strip()
        elif response.status_code == 401:
            return "🔒 Invalid or missing OpenRouter API key."
        else:
            return f"❌ Error {response.status_code}: {response.text}"
    except Exception as e:
        return f"🚫 Failed to connect: {str(e)}"

# ----------------------------
# Chat Input
# ----------------------------
st.markdown("### 💬 Chat")
user_input = st.text_input("Ask your gadget question", placeholder="e.g., Best phone under ₹25,000")

if st.button("Ask") and user_input:
    with st.spinner("Thinking..."):
        reply = query_mistral(user_input)
        st.session_state.chat.append({"role": "user", "content": user_input})
        st.session_state.chat.append({"role": "assistant", "content": reply})
        st.rerun()

# ----------------------------
# Show Chat
# ----------------------------
for message in reversed(st.session_state.chat):
    if message["role"] == "user":
        with st.chat_message("user"):
            st.markdown(f"**You:** {message['content']}")
    else:
        with st.chat_message("assistant"):
            st.markdown(f"**Assistant:** {message['content']}")

# ----------------------------
# Footer
# ----------------------------
st.markdown("---")
st.markdown("Built with ❤️ using Mistral 7B via OpenRouter API")
