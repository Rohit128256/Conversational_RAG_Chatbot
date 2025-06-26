import os
import streamlit as st
from src.runnables import runnable_with_history
from src.add_info import add_info_from_file
import tempfile

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
    
if "user_id" not in st.session_state:
    st.session_state.user_id = ""

if "file_uploader_key" not in st.session_state:
    st.session_state.file_uploader_key = 0

# Page configuration
st.set_page_config(
    page_title="Conversational RAG",
    page_icon="🤖",
    layout="centered"
)

# Custom CSS for styling
st.markdown("""
<style>
    .header {
        text-align: center;
        color: #2E86C1;
        padding-bottom: 20px;
    }
    .sidebar-section {
        background-color: #F4F6F6;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 20px;
    }
    .chat-container {
        max-height: 500px;
        overflow-y: auto;
        margin-bottom: 20px;
        border: 1px solid #D6DBDF;
        border-radius: 10px;
        padding: 15px;
    }
    .user-message {
        background-color: #D6EAF8;
        padding: 10px;
        border-radius: 10px;
        margin-bottom: 10px;
    }
    .assistant-message {
        background-color: #EAECEE;
        padding: 10px;
        border-radius: 10px;
        margin-bottom: 10px;
    }
    .stButton button {
        width: 100%;
        background-color: #2E86C1 !important;
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# Main layout
st.title("🤖 Conversational RAG Assistant")
st.markdown("---")

# Sidebar for file upload and user settings
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # File upload section
    with st.expander("📁 Add Documents to Knowledge Base", expanded=True):
        st.write("Upload files to enhance the knowledge base")
        uploaded_file = st.file_uploader(
            "Select files (PDF, TXT, DOCX)",
            type=["pdf", "txt", "docx"],
            key=st.session_state.file_uploader_key
        )
        
        if uploaded_file is not None:
            try:
                # Save to temp file
                with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{uploaded_file.name}") as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    file_path = tmp_file.name
                
                # Add to vector store
                with st.spinner(f"Processing {uploaded_file.name}..."):
                    add_info_from_file(file_path)
                
                st.success(f"✅ {uploaded_file.name} added to knowledge base!")
                st.session_state.file_uploader_key += 1  # Reset uploader
            except Exception as e:
                st.error(f"❌ Error processing file: {str(e)}")
            finally:
                # Clean up temp file
                if 'file_path' in locals() and os.path.exists(file_path):
                    os.unlink(file_path)
    
    # User ID section
    with st.expander("👤 User Settings", expanded=True):
        new_user_id = st.text_input("Enter your username:", value=st.session_state.user_id)
        
        if new_user_id != st.session_state.user_id:
            if new_user_id.strip() == "":
                st.warning("Username cannot be empty")
            else:
                st.session_state.user_id = new_user_id
                st.session_state.messages = []
                st.success(f"Username set to: {new_user_id}")

# Main chat area
st.subheader("💬 Chat")

# Display chat messages
chat_container = st.container()
with chat_container:
    if st.session_state.messages:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])
    else:
        st.info("Enter your question below to start a conversation")

# Chat input
if st.session_state.user_id:
    if prompt := st.chat_input("Type your question..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with chat_container:
            with st.chat_message("user"):
                st.write(prompt)
        
        # Generate response
        with st.spinner("Thinking..."):
            try:
                config = {"configurable": {"session_id": st.session_state.user_id}}
                response = runnable_with_history.invoke(
                    {"input": prompt},
                    config=config
                )
                answer = response["answer"]
            except Exception as e:
                answer = f"❌ Error generating response: {str(e)}"
        
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": answer})
        
        # Display assistant response
        with chat_container:
            with st.chat_message("assistant"):
                st.write(answer)
else:
    st.warning("⚠️ Please set a username in the sidebar to start chatting")
    st.chat_input("Type your question...", disabled=True)

# Clear chat button
if st.session_state.messages:
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.rerun()

