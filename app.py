import streamlit as st
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

# Page setup
st.set_page_config(page_title="🤖 Gadget Advisor", page_icon="📱")
st.title("🤖 Gadget Advisor")
st.markdown("Ask me anything about phones, laptops, smartwatches, tablets & more!")

# Load model & tokenizer (cached for performance)
@st.cache_resource
def load_model():
    tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-medium")
    model = AutoModelForCausalLM.from_pretrained("microsoft/DialoGPT-medium")
    return tokenizer, model

tokenizer, model = load_model()

# 💬 System Prompt (your version)
SYSTEM_PROMPT = (
    "You are a helpful and knowledgeable gadget advisor. You assist users in choosing the best electronic devices — "
    "including smartphones, laptops, tablets, smartwatches, and more.\n\n"
    "Always consider the user’s needs such as budget, usage (e.g., gaming, work, photography), and preferences "
    "(e.g., battery life, camera quality, performance). Provide detailed but easy-to-understand explanations of "
    "device specifications like processor, RAM, camera setup, display type, battery, and software.\n\n"
    "Compare models clearly when asked, and suggest the best options available in the market as of 2025. "
    "Be honest and unbiased — highlight both pros and cons.\n\n"
    "Your tone is friendly, professional, and trustworthy. You do not fake information — if you're unsure, explain "
    "that and suggest how the user could verify it."
)

# Session state initialization
if "chat_history_ids" not in st.session_state:
    st.session_state.chat_history_ids = None
if "chat_log" not in st.session_state:
    st.session_state.chat_log = []
if "system_prompt_injected" not in st.session_state:
    st.session_state.system_prompt_injected = False

# Input field
user_input = st.text_input("You:", placeholder="What's the best phone under ₹30,000?")

# Submit message
if st.button("Send") and user_input:
    # Inject system prompt only once at beginning
    if not st.session_state.system_prompt_injected:
        sys_ids = tokenizer.encode(SYSTEM_PROMPT + tokenizer.eos_token, return_tensors="pt")
        st.session_state.chat_history_ids = sys_ids
        st.session_state.system_prompt_injected = True

    # Encode user input
    user_input_ids = tokenizer.encode(user_input + tokenizer.eos_token, return_tensors="pt")

    # Combine with previous context
    input_ids = torch.cat([st.session_state.chat_history_ids, user_input_ids], dim=-1)

    # Generate response
    output_ids = model.generate(
        input_ids,
        max_length=1000,
        pad_token_id=tokenizer.eos_token_id,
        do_sample=True,
        temperature=0.8,
        top_p=0.9
    )

    # Decode response
    response = tokenizer.decode(output_ids[:, input_ids.shape[-1]:][0], skip_special_tokens=True)

    # Save conversation
    st.session_state.chat_log.append(("You", user_input))
    st.session_state.chat_log.append(("Bot", response))
    st.session_state.chat_history_ids = output_ids

    # Refresh the screen
    st.experimental_rerun()

# Show chat history
if st.session_state.chat_log:
    for speaker, msg in st.session_state.chat_log:
        with st.chat_message("user" if speaker == "You" else "assistant"):
            st.write(msg)

# Reset button
if st.button("Reset Chat"):
    st.session_state.chat_log = []
    st.session_state.chat_history_ids = None
    st.session_state.system_prompt_injected = False
    st.experimental_rerun()
