"""
Document Chat Page

This page handles document chat functionality with RAG capabilities.
"""

import streamlit as st
import requests
import time
from typing import Any

def make_api_request(endpoint: str, method: str = "GET", files: dict | None = None, data: dict | None = None) -> dict[str, Any]:
    """Make API request to backend server"""
    API_BASE_URL = "http://localhost:8000"
    url = f"{API_BASE_URL}{endpoint}"
    
    try:
        if method == "POST":
            if files:
                response = requests.post(url, files=files, data=data)
            else:
                response = requests.post(url, json=data)
        else:
            response = requests.get(url)
        
        response.raise_for_status()
        return {"success": True, "data": response.json()}
    
    except requests.exceptions.ConnectionError:
        return {"success": False, "error": "Cannot connect to backend server. Please ensure the API server is running."}
    except requests.exceptions.HTTPError as e:
        try:
            error_detail = response.json().get("detail", str(e))
        except:
            error_detail = str(e)
        return {"success": False, "error": f"API Error: {error_detail}"}
    except Exception as e:
        return {"success": False, "error": f"Unexpected error: {str(e)}"}

def show_chat_page():
    st.title("Document Chat")
    st.markdown("Upload documents and chat with them using AI-powered question answering")
    
    # Initialize session state
    if "chat_session_id" not in st.session_state:
        st.session_state.chat_session_id = None
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []
    if "index_built" not in st.session_state:
        st.session_state.index_built = False
    if "uploaded_files_info" not in st.session_state:
        st.session_state.uploaded_files_info = []
    
    # Step 1: Document Upload and Indexing
    st.subheader("Step 1: Upload and Index Documents")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        uploaded_files = st.file_uploader(
            "Choose documents to upload", 
            type=['pdf', 'docx', 'txt'],
            accept_multiple_files=True,
            help="You can upload multiple files. Supported formats: PDF, DOCX, TXT"
        )
        
        if uploaded_files:
            st.markdown("**Uploaded Files:**")
            total_size = 0
            for i, file in enumerate(uploaded_files):
                total_size += file.size
                st.write(f"{i+1}. {file.name} ({file.size:,} bytes)")
            st.caption(f"Total: {len(uploaded_files)} files, {total_size:,} bytes")
    
    with col2:
        st.markdown("**Index Configuration**")
        
        with st.expander("Basic Settings", expanded=True):
            chunk_size = st.number_input(
                "Chunk Size", 
                value=1000, 
                min_value=200, 
                step=100,
                help="Size of text chunks for processing"
            )
            chunk_overlap = st.number_input(
                "Chunk Overlap", 
                value=200, 
                min_value=0, 
                step=50,
                help="Overlap between consecutive chunks"
            )
            k_value = st.number_input(
                "Top-K Results", 
                value=5, 
                min_value=1, 
                max_value=20,
                help="Number of relevant chunks to retrieve"
            )
        
        with st.expander("Advanced Settings"):
            session_id = st.text_input(
                "Custom Session ID", 
                placeholder="Auto-generated if empty",
                help="Use custom session ID or leave empty for auto-generation"
            )
            use_session_dirs = st.checkbox(
                "Use Session-based Storage", 
                value=True,
                help="Store index in session-specific directory"
            )
    
    # Index building
    if uploaded_files:
        if st.button("Build/Update Document Index", type="primary", use_container_width=True):
            with st.spinner("Building document index... This may take a few moments."):
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Prepare files for API
                files = [("files", (file.name, file.getvalue(), file.type)) for file in uploaded_files]
                
                # Prepare form data
                form_data = {
                    "chunk_size": str(chunk_size),
                    "chunk_overlap": str(chunk_overlap),
                    "k": str(k_value),
                    "use_session_dirs": "true" if use_session_dirs else "false"
                }
                
                if session_id:
                    form_data["session_id"] = session_id
                
                progress_bar.progress(30)
                status_text.text("Uploading files...")
                
                # Make API request
                result = make_api_request("/chat/index", method="POST", files=dict(files), data=form_data)
                
                progress_bar.progress(80)
                status_text.text("Processing documents...")
                
                # Display results
                if result["success"]:
                    progress_bar.progress(100)
                    status_text.text("Index built successfully!")
                    
                    data = result["data"]
                    st.session_state.chat_session_id = data.get("session_id")
                    st.session_state.index_built = True
                    st.session_state.uploaded_files_info = [{"name": f.name, "size": f.size} for f in uploaded_files]
                    
                    st.success(f"Index built successfully! Session ID: {st.session_state.chat_session_id}")
                    
                    # Clear progress indicators
                    time.sleep(1)
                    progress_bar.empty()
                    status_text.empty()
                    
                else:
                    progress_bar.empty()
                    status_text.empty()
                    st.error(f"Indexing failed: {result['error']}")
    
    # Step 2: Chat Interface
    st.markdown("---")
    st.subheader("Step 2: Chat with Your Documents")
    
    if not st.session_state.index_built:
        st.warning("Please upload and index documents first before starting a chat.")
        
        # Show help for getting started
        with st.expander("Getting Started Guide"):
            st.markdown("""
            **To start chatting with your documents:**
            
            1. **Upload Files**: Click 'Browse files' and select your documents (PDF, DOCX, or TXT)
            2. **Configure Settings**: Adjust chunk size, overlap, and retrieval settings as needed
            3. **Build Index**: Click 'Build/Update Document Index' to process your documents
            4. **Start Chatting**: Once indexing is complete, you can ask questions below
            
            **Tips:**
            - Upload multiple related documents for better context
            - Use specific questions for more accurate answers
            - Adjust Top-K value to get more or fewer relevant chunks
            """)
    
    else:
        # Display current session info
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Session ID", st.session_state.chat_session_id or "Auto-generated")
        with col2:
            st.metric("Indexed Files", len(st.session_state.uploaded_files_info))
        with col3:
            st.metric("Status", "Ready for chat")
        
        # Chat interface
        st.markdown("**Chat Interface**")
        
        # Display chat history
        if st.session_state.chat_messages:
            chat_container = st.container()
            with chat_container:
                for i, message in enumerate(st.session_state.chat_messages):
                    if message["role"] == "user":
                        with st.chat_message("user"):
                            st.write(message["content"])
                    else:
                        with st.chat_message("assistant"):
                            st.write(message["content"])
        
        # Chat input
        col1, col2 = st.columns([4, 1])
        
        with col1:
            question = st.text_input(
                "Ask a question about your documents:",
                key="chat_input",
                placeholder="What is the main topic of these documents?"
            )
        
        with col2:
            send_button = st.button("Send", type="primary", use_container_width=True)
        
        # Action buttons
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Clear Chat History", use_container_width=True):
                st.session_state.chat_messages = []
                st.rerun()
        
        with col2:
            if st.button("Reset Session", use_container_width=True):
                st.session_state.chat_session_id = None
                st.session_state.chat_messages = []
                st.session_state.index_built = False
                st.session_state.uploaded_files_info = []
                st.rerun()
        
        with col3:
            if st.session_state.chat_messages:
                # Export chat history
                chat_export = "\n\n".join([
                    f"{'User' if msg['role'] == 'user' else 'Assistant'}: {msg['content']}"
                    for msg in st.session_state.chat_messages
                ])
                st.download_button(
                    "Export Chat",
                    data=chat_export,
                    file_name=f"chat_history_{st.session_state.chat_session_id}.txt",
                    mime="text/plain",
                    use_container_width=True
                )
        
        # Process question
        if send_button and question:
            with st.spinner("Getting answer from your documents..."):
                # Add user message to chat
                st.session_state.chat_messages.append({"role": "user", "content": question})
                
                # Prepare form data
                form_data = {
                    "question": question,
                    "k": str(k_value),
                    "use_session_dirs": "true" if use_session_dirs else "false"
                }
                
                if st.session_state.chat_session_id:
                    form_data["session_id"] = st.session_state.chat_session_id
                
                # Make API request
                result = make_api_request("/chat/query", method="POST", data=form_data)
                
                # Process response
                if result["success"]:
                    data = result["data"]
                    answer = data.get("answer", "No answer received")
                    st.session_state.chat_messages.append({"role": "assistant", "content": answer})
                else:
                    error_msg = f"Error: {result['error']}"
                    st.session_state.chat_messages.append({"role": "assistant", "content": error_msg})
                
                st.rerun()
        
        # Example questions
        if not st.session_state.chat_messages:
            st.markdown("**Example Questions:**")
            example_questions = [
                "What is the main topic of these documents?",
                "Can you summarize the key points?",
                "What are the important dates mentioned?",
                "Who are the main people or organizations discussed?",
                "What conclusions or recommendations are made?"
            ]
            
            for i, example in enumerate(example_questions):
                if st.button(f"Ask: {example}", key=f"example_{i}"):
                    st.session_state.chat_messages.append({"role": "user", "content": example})
                    # Process the example question
                    with st.spinner("Getting answer..."):
                        form_data = {
                            "question": example,
                            "k": str(k_value),
                            "use_session_dirs": "true" if use_session_dirs else "false"
                        }
                        if st.session_state.chat_session_id:
                            form_data["session_id"] = st.session_state.chat_session_id
                        
                        result = make_api_request("/chat/query", method="POST", data=form_data)
                        
                        if result["success"]:
                            data = result["data"]
                            answer = data.get("answer", "No answer received")
                            st.session_state.chat_messages.append({"role": "assistant", "content": answer})
                        else:
                            error_msg = f"Error: {result['error']}"
                            st.session_state.chat_messages.append({"role": "assistant", "content": error_msg})
                    
                    st.rerun()

if __name__ == "__main__":
    show_chat_page()
