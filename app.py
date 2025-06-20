import streamlit as st
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline

st.set_page_config(page_title="AIRA – Gadget Assistant", page_icon="🤖")
st.title("🤖 AIRA – Gadget Advisor")
st.markdown("Ask about phones, laptops, tablets, or any gadgets. Get expert help instantly!")

@st.cache_resource
def load_model():
    model_name = "google/flan-t5-small"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
    return pipeline("text2text-generation", model=model, tokenizer=tokenizer)

pipe = load_model()

SYSTEM_PROMPT = (
    "You are AIRA, a helpful gadget advisor. "
    "Suggest 2–3 options with bullet points for name, features, pros, and cons. "
    "Keep it short and beginner-friendly. End with: 'Would you like more options?'"
)

if "chat" not in st.session_state:
    st.session_state.chat = []

user_input = st.text_input("Ask your gadget question", placeholder="e.g., Best laptop under ₹40,000")

def get_response(prompt):
    input_text = f"{SYSTEM_PROMPT}\nUser: {prompt}\nAssistant:"
    output = pipe(input_text, max_new_tokens=256)[0]['generated_text']
    return output.replace(input_text, "").strip()

if st.button("Ask") and user_input:
    with st.spinner("Thinking..."):
        reply = get_response(user_input)
        st.session_state.chat.append({"role": "user", "content": user_input})
        st.session_state.chat.append({"role": "assistant", "content": reply})
        st.rerun()

for msg in reversed(st.session_state.chat):
    with st.chat_message(msg["role"]):
        st.markdown(f"**{msg['role'].capitalize()}:** {msg['content']}")

st.markdown("---")
st.markdown("Built with ❤️ using FLAN-T5 Small (local)")
