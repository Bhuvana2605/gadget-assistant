import streamlit as st
import requests
import time
import json

# Page configuration
st.set_page_config(page_title="🎯 Gadget Assistant", page_icon="🤖")
st.title("🤖 Ask My AI Assistant")
st.markdown("Talk to your Hugging Face Assistant for gadget recommendations!")

# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Get secrets with proper error handling
def get_secrets():
    try:
        hf_token = st.secrets.get("HF_TOKEN", "")
        assistant_id = st.secrets.get("ASSISTANT_ID", "")
        
        if not hf_token:
            st.error("❌ HF_TOKEN not found in secrets. Please add it to your Streamlit secrets.")
            st.info("💡 Go to your app settings and add HF_TOKEN to secrets.")
            return None, None
            
        if not assistant_id:
            st.error("❌ ASSISTANT_ID not found in secrets. Please add it to your Streamlit secrets.")
            st.info("💡 Go to your app settings and add ASSISTANT_ID to secrets.")
            return None, None
            
        return hf_token, assistant_id
        
    except Exception as e:
        st.error(f"❌ Error accessing secrets: {str(e)}")
        return None, None

# Get the secrets
HF_TOKEN, ASSISTANT_ID = get_secrets()

# Only proceed if we have valid secrets
if HF_TOKEN and ASSISTANT_ID:
    
    # API configuration
    API_URL = f"https://api.huggingface.co/chat/assistants/{ASSISTANT_ID}/messages"
    HEADERS = {
        "Authorization": f"Bearer {HF_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # Safe API call function
    def call_huggingface_api(user_message):
        """Make a safe API call to Hugging Face"""
        
        try:
            # Prepare the payload
            payload = {
                "inputs": {
                    "messages": st.session_state.chat_history + [{"role": "user", "content": user_message}]
                }
            }
            
            # Make the request with proper error handling
            with st.spinner("🤔 Getting response from AI assistant..."):
                try:
                    response = requests.post(
                        API_URL,
                        headers=HEADERS,
                        json=payload,
                        timeout=60,  # Longer timeout
                        verify=True
                    )
                    
                    # Check response status
                    if response.status_code == 200:
                        try:
                            result = response.json()
                            assistant_message = result.get("generated_message", {}).get("content", "")
                            
                            if assistant_message:
                                return assistant_message, None
                            else:
                                return None, "❌ Empty response from assistant. Please try again."
                                
                        except json.JSONDecodeError:
                            return None, "❌ Invalid response format from API."
                            
                    elif response.status_code == 401:
                        return None, "❌ Authentication failed. Please check your HF_TOKEN."
                        
                    elif response.status_code == 404:
                        return None, "❌ Assistant not found. Please check your ASSISTANT_ID."
                        
                    elif response.status_code == 429:
                        return None, "❌ Rate limit exceeded. Please wait a moment and try again."
                        
                    elif response.status_code >= 500:
                        return None, "❌ Hugging Face server error. Please try again later."
                        
                    else:
                        return None, f"❌ API returned status code {response.status_code}. Please try again."
                
                except requests.exceptions.Timeout:
                    return None, "❌ Request timed out. The API might be slow. Please try again."
                    
                except requests.exceptions.ConnectionError:
                    return None, "❌ Cannot connect to Hugging Face API. Please check your internet connection and try again."
                    
                except requests.exceptions.RequestException as e:
                    return None, f"❌ Network error: Please check your connection and try again."
                    
                except Exception as e:
                    return None, f"❌ Unexpected error: Please try again."
                    
        except Exception as e:
            return None, f"❌ Error preparing request: Please try again."
    
    # Add clear chat button in sidebar
    with st.sidebar:
        st.header("🔧 Controls")
        if st.button("🗑 Clear Chat"):
            st.session_state.chat_history = []
            st.rerun()
        
        st.header("📊 Stats")
        if st.session_state.chat_history:
            user_messages = len([msg for msg in st.session_state.chat_history if msg["role"] == "user"])
            st.metric("Messages sent", user_messages)
    
    # User input
    user_input = st.text_input("Ask anything about electronics:", placeholder="e.g., What's the best laptop under $1000?")
    
    # Send button
    if st.button("Send", type="primary") and user_input.strip():
        
        # Call the API
        assistant_response, error = call_huggingface_api(user_input.strip())
        
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
        
        for msg in st.session_state.chat_history:
            role = "🧑 *You" if msg["role"] == "user" else "🤖 **Assistant*"
            
            if msg["role"] == "user":
                st.markdown(f"{role}: {msg['content']}")
            else:
                st.markdown(f"{role}: {msg['content']}")
            
            st.markdown("")  # Add spacing
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
        
        for example in examples:
            if st.button(example, key=f"example_{example}"):
                # Set the input and trigger send
                st.session_state.example_input = example
                st.rerun()
    
    # Handle example input
    if "example_input" in st.session_state:
        example_input = st.session_state.example_input
        del st.session_state.example_input
        
        assistant_response, error = call_huggingface_api(example_input)
        
        if assistant_response:
            st.session_state.chat_history.append({"role": "user", "content": example_input})
            st.session_state.chat_history.append({"role": "assistant", "content": assistant_response})
            st.rerun()
        else:
            st.error(error)

else:
    st.stop()  # Stop execution if secrets are missing

# Footer
st.markdown("---")
st.markdown("Powered by Hugging Face Assistant API")
