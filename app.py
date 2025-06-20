import streamlit as st
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
import torch

st.set_page_config(page_title="AIRA – Gadget Assistant", page_icon="🤖")
st.title("🤖 AIRA – Gadget Advisor")
st.markdown("Ask about phones, laptops, tablets, or any gadgets. Get expert help instantly!")

@st.cache_resource
def load_model():
    model_name = "google/flan-t5-base"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
    pipe = pipeline("text2text-generation", model=model, tokenizer=tokenizer)
    return pipe

pipe = load_model()

SYSTEM_PROMPT = (
    "You are AIRA, a friendly and concise gadget assistant. "
    "Based on the user's question, suggest 2–3 device options using bullet points, "
    "mentioning name, key features, pros, and cons. Keep it short and beginner-friendly. "
    "End with: 'Would you like more options or details on any of these?'"
)

if "chat" not in st.session_state:
    st.session_state.chat = []

user_input = st.text_input("Ask your gadget question", placeholder="e.g., Best phone under ₹25,000")

def get_response(prompt):
    full_prompt = f"{SYSTEM_PROMPT}\nUser: {prompt}"
    result = pipe(full_prompt, max_new_tokens=256)[0]["generated_text"]
    return result

if st.button("Ask") and user_input:
    with st.spinner("Thinking..."):
        reply = get_response(user_input)
        st.session_state.chat.append({"role": "user", "content": user_input})
        st.session_state.chat.append({"role": "assistant", "content": reply})
        st.rerun()

for message in reversed(st.session_state.chat):
    with st.chat_message(message["role"]):
        st.markdown(f"**{message['role'].capitalize()}:** {message['content']}")

st.markdown("---")
st.markdown("Built with ❤️ using FLAN-T5 base (local)")
