import streamlit as st
import requests
import time
import json

# Page configuration
st.set_page_config(page_title="🎯 Gadget Assistant", page_icon="🤖")
st.title("🤖 Ask My AI Assistant")
st.markdown("Talk to your AI Assistant for gadget recommendations!")

# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Custom system prompt for gadget recommendations
SYSTEM_PROMPT = """You are a knowledgeable and helpful gadget expert assistant. Your role is to provide detailed, accurate, and up-to-date recommendations about electronics, gadgets, and technology products. 

Key guidelines:
- Provide specific product recommendations with model names and key features
- Consider budget constraints when mentioned
- Explain the reasoning behind your recommendations
- Compare different options when relevant
- Include pros and cons for major recommendations
- Stay current with technology trends
- Be helpful, friendly, and conversational
- If you don't know something specific, be honest about it

Focus areas: smartphones, laptops, tablets, headphones, smart home devices, gaming equipment, cameras, and other consumer electronics."""

# Available models (you can change this to any free model)
AVAILABLE_MODELS = {
    "Qwen2.5-1.5B-Instruct": "Qwen/Qwen2.5-1.5B-Instruct",
    "Llama-3.1-8B-Instruct": "meta-llama/Llama-3.1-8B-Instruct", 
    "Hermes-3-Llama-3.1-8B": "NousResearch/Hermes-3-Llama-3.1-8B",
    "Phi-3.5-Mini-Instruct": "microsoft/Phi-3.5-mini-instruct"
}

# Get secrets with proper error handling
def get_secrets():
    try:
        hf_token = st.secrets.get("HF_TOKEN", "")
        
        if not hf_token:
            st.error("❌ HF_TOKEN not found in secrets. Please add it to your Streamlit secrets.")
            st.info("💡 Go to your app settings and add HF_TOKEN to secrets.")
            return None
            
        return hf_token
        
    except Exception as e:
        st.error(f"❌ Error accessing secrets: {str(e)}")
        return None

# Get the token
HF_TOKEN = get_secrets()

# Model selection in sidebar
with st.sidebar:
    st.header("🤖 Model Settings")
    selected_model_name = st.selectbox(
        "Choose AI Model:",
        list(AVAILABLE_MODELS.keys()),
        index=0
    )
    selected_model = AVAILABLE_MODELS[selected_model_name]
    
    # Model parameters
    max_length = st.slider("Max Response Length", 100, 1000, 500)
    temperature = st.slider("Creativity (Temperature)", 0.1, 1.0, 0.7, 0.1)
    
    st.header("🔧 Controls")
    if st.button("🗑 Clear Chat"):
        st.session_state.chat_history = []
        st.rerun()
    
    st.header("📊 Stats")
    if st.session_state.chat_history:
        user_messages = len([msg for msg in st.session_state.chat_history if msg["role"] == "user"])
        st.metric("Messages sent", user_messages)
        st.metric("Current Model", selected_model_name)

# Only proceed if we have valid token
if HF_TOKEN:
    
    def format_conversation(chat_history, user_message):
        """Format the conversation with system prompt for the model"""
        # Start with system prompt
        formatted_prompt = f"System: {SYSTEM_PROMPT}\n\n"
        
        # Add chat history
        for msg in chat_history:
            role = "Human" if msg["role"] == "user" else "Assistant"
            formatted_prompt += f"{role}: {msg['content']}\n\n"
        
        # Add current user message
        formatted_prompt += f"Human: {user_message}\n\nAssistant:"
        
        return formatted_prompt
    
    # Safe API call function
    def call_huggingface_inference_api(user_message):
        """Make a safe API call to Hugging Face Inference API"""
        
        try:
            # API URL for the selected model
            API_URL = f"https://api-inference.huggingface.co/models/{selected_model}"
            HEADERS = {
                "Authorization": f"Bearer {HF_TOKEN}",
                "Content-Type": "application/json"
            }
            
            # Format the conversation
            formatted_prompt = format_conversation(st.session_state.chat_history, user_message)
            
            # Prepare the payload
            payload = {
                "inputs": formatted_prompt,
                "parameters": {
                    "max_new_tokens": max_length,
                    "temperature": temperature,
                    "do_sample": True,
                    "return_full_text": False
                }
            }
            
            # Make the request with proper error handling
            with st.spinner(f"🤔 Getting response from {selected_model_name}..."):
                try:
                    response = requests.post(
                        API_URL,
                        headers=HEADERS,
                        json=payload,
                        timeout=60
                    )
                    
                    # Check response status
                    if response.status_code == 200:
                        try:
                            result = response.json()
                            
                            # Handle different response formats
                            if isinstance(result, list) and len(result) > 0:
                                assistant_message = result[0].get("generated_text", "").strip()
                            elif isinstance(result, dict):
                                assistant_message = result.get("generated_text", "").strip()
                            else:
                                return None, "❌ Unexpected response format from API."
                            
                            if assistant_message:
                                return assistant_message, None
                            else:
                                return None, "❌ Empty response from assistant. Please try again."
                                
                        except json.JSONDecodeError:
                            return None, "❌ Invalid response format from API."
                        except Exception as e:
                            return None, f"❌ Error parsing response: Please try again."
                            
                    elif response.status_code == 401:
                        return None, "❌ Authentication failed. Please check your HF_TOKEN."
                        
                    elif response.status_code == 404:
                        return None, f"❌ Model {selected_model} not found or not accessible."
                        
                    elif response.status_code == 429:
                        return None, "❌ Rate limit exceeded. Please wait a moment and try again."
                    
                    elif response.status_code == 503:
                        return None, "❌ Model is currently loading. Please wait a moment and try again."
                        
                    elif response.status_code >= 500:
                        return None, "❌ Hugging Face server error. Please try again later."
                        
                    else:
                        return None, f"❌ API returned status code {response.status_code}. Please try again."
                
                except requests.exceptions.Timeout:
                    return None, "❌ Request timed out. The model might be loading. Please try again."
                    
                except requests.exceptions.ConnectionError:
                    return None, "❌ Cannot connect to Hugging Face API. Please check your internet connection."
                    
                except requests.exceptions.RequestException:
                    return None, f"❌ Network error: Please check your connection and try again."
                    
        except Exception as e:
            return None, f"❌ Error preparing request: Please try again."
    
    # User input
    user_input = st.text_input(
        "Ask anything about electronics:", 
        placeholder="e.g., What's the best laptop under $1000?",
        key="user_input"
    )
    
    # Send button
    col1, col2 = st.columns([1, 4])
    with col1:
        send_clicked = st.button("Send", type="primary")
    
    if send_clicked and user_input.strip():
        
        # Call the API
        assistant_response, error = call_huggingface_inference_api(user_input.strip())
        
        if assistant_response:
            # Success - add to chat history
            st.session_state.chat_history.append({"role": "user", "content": user_input.strip()})
            st.session_state.chat_history.append({"role": "assistant", "content": assistant_response})
            st.rerun()
            
        else:
            # Error - show the error message
            st.error(error)
    
    # Display chat history
    if st.session_state.chat_history:
        st.markdown("---")
        st.subheader("💬 Conversation")
        
        for i, msg in enumerate(st.session_state.chat_history):
            if msg["role"] == "user":
                with st.chat_message("user"):
                    st.write(msg["content"])
            else:
                with st.chat_message("assistant"):
                    st.write(msg["content"])
    else:
        st.info("👋 Start a conversation by asking about electronics!")
    
    # Example questions
    with st.expander("💡 Example Questions"):
        examples = [
            "What's the best smartphone under $500?",
            "Recommend wireless headphones for workouts",
            "Compare iPhone vs Samsung Galaxy",
            "Best laptop for programming students",
            "What to look for in a gaming monitor?",
            "Budget tablet recommendations"
        ]
        
        cols = st.columns(2)
        for i, example in enumerate(examples):
            with cols[i % 2]:
                if st.button(example, key=f"example_{i}"):
                    assistant_response, error = call_huggingface_inference_api(example)
                    
                    if assistant_response:
                        st.session_state.chat_history.append({"role": "user", "content": example})
                        st.session_state.chat_history.append({"role": "assistant", "content": assistant_response})
                        st.rerun()
                    else:
                        st.error(error)

else:
    st.stop()  # Stop execution if token is missing

# Footer
st.markdown("---")
st.markdown(f"Powered by Hugging Face Inference API • Model: {selected_model_name}")
