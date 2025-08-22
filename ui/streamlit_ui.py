"""
Streamlit UI for Document Portal

This application provides a user interface for the Document Portal backend API.
It includes separate pages for document analysis, comparison, and chat functionality.
"""

import streamlit as st
import requests
import json
import pandas as pd
from typing import Optional, Dict, Any
import time

# Configuration
API_BASE_URL = "http://localhost:8000"  # Update this to match your FastAPI server

# Page configuration
st.set_page_config(
    page_title="Document Portal",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        padding: 1rem 0;
        border-bottom: 2px solid #f0f2f6;
        margin-bottom: 2rem;
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        margin: 1rem 0;
    }
    .error-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        margin: 1rem 0;
    }
    .info-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        margin: 1rem 0;
    }
    .stSelectbox > div > div > div {
        background-color: white;
    }
</style>
""", unsafe_allow_html=True)

# Utility functions
def make_api_request(endpoint: str, method: str = "GET", files: Optional[Dict] = None, data: Optional[Dict] = None) -> Dict[str, Any]:
    """Make API request to backend server"""
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

def display_result(result: Dict[str, Any], title: str = "Result"):
    """Display API result with proper formatting"""
    if result["success"]:
        st.markdown(f'<div class="success-box"><strong>Success!</strong> {title} completed successfully.</div>', unsafe_allow_html=True)
        return result["data"]
    else:
        st.markdown(f'<div class="error-box"><strong>Error:</strong> {result["error"]}</div>', unsafe_allow_html=True)
        return None

# Sidebar navigation
st.sidebar.title("Document Portal")
st.sidebar.markdown("---")

# Page selection
page = st.sidebar.selectbox(
    "Choose a page:",
    ["Home", "Document Analysis", "Document Comparison", "Document Chat"],
    index=0
)

st.sidebar.markdown("---")

# API status check
with st.sidebar:
    if st.button("Check API Status", key="api_status"):
        with st.spinner("Checking API status..."):
            health_result = make_api_request("/health")
            if health_result["success"]:
                st.success("API Server is running")
            else:
                st.error("API Server is not accessible")

# Main content area
if page == "Home":
    st.markdown('<div class="main-header">', unsafe_allow_html=True)
    st.title("Document Portal")
    st.markdown("Welcome to the Document Portal application")
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("""
    ## Available Features
    
    **Document Analysis**
    - Upload a PDF document for automated analysis
    - Get structured insights and information extraction
    
    **Document Comparison** 
    - Compare two PDF documents side by side
    - Identify differences and changes between versions
    
    **Document Chat**
    - Upload multiple documents and chat with them
    - Ask questions and get AI-powered answers from your documents
    
    ## Getting Started
    
    1. Use the sidebar to navigate between different features
    2. Make sure your backend API server is running on port 8000
    3. Check the API status using the button in the sidebar
    
    ## System Requirements
    
    - Backend API server running on localhost:8000
    - Supported file formats: PDF, DOCX, TXT (varies by feature)
    """)

elif page == "Document Analysis":
    st.markdown('<div class="main-header">', unsafe_allow_html=True)
    st.title("Document Analysis")
    st.markdown("Upload a PDF document to get detailed analysis and insights")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # File upload
    uploaded_file = st.file_uploader(
        "Choose a PDF file", 
        type=['pdf'],
        help="Only PDF files are supported for analysis"
    )
    
    if uploaded_file is not None:
        st.markdown(f'<div class="info-box">File uploaded: <strong>{uploaded_file.name}</strong> ({uploaded_file.size} bytes)</div>', unsafe_allow_html=True)
        
        if st.button("Analyze Document", type="primary"):
            with st.spinner("Analyzing document... This may take a few moments."):
                # Prepare file for API
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                
                # Make API request
                result = make_api_request("/analyze", method="POST", files=files)
                
                # Display results
                data = display_result(result, "Document analysis")
                if data:
                    st.subheader("Analysis Results")
                    
                    # Display results in expandable sections
                    if isinstance(data, dict):
                        for key, value in data.items():
                            with st.expander(f"{key.replace('_', ' ').title()}", expanded=True):
                                if isinstance(value, (dict, list)):
                                    st.json(value)
                                else:
                                    st.write(value)
                    else:
                        st.json(data)
                    
                    # Download results
                    st.download_button(
                        label="Download Analysis Results (JSON)",
                        data=json.dumps(data, indent=2),
                        file_name=f"analysis_{uploaded_file.name}.json",
                        mime="application/json"
                    )

elif page == "Document Comparison":
    st.markdown('<div class="main-header">', unsafe_allow_html=True)
    st.title("Document Comparison")
    st.markdown("Compare two PDF documents to identify differences and changes")
    st.markdown('</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Reference Document")
        reference_file = st.file_uploader(
            "Upload reference PDF", 
            type=['pdf'],
            key="reference",
            help="This will be used as the baseline for comparison"
        )
    
    with col2:
        st.subheader("Actual Document")
        actual_file = st.file_uploader(
            "Upload actual PDF", 
            type=['pdf'],
            key="actual",
            help="This document will be compared against the reference"
        )
    
    if reference_file and actual_file:
        st.markdown(f'<div class="info-box">Ready to compare:<br><strong>Reference:</strong> {reference_file.name}<br><strong>Actual:</strong> {actual_file.name}</div>', unsafe_allow_html=True)
        
        if st.button("Compare Documents", type="primary"):
            with st.spinner("Comparing documents... This may take a few moments."):
                # Prepare files for API
                files = {
                    "reference": (reference_file.name, reference_file.getvalue(), reference_file.type),
                    "actual": (actual_file.name, actual_file.getvalue(), actual_file.type)
                }
                
                # Make API request
                result = make_api_request("/compare", method="POST", files=files)
                
                # Display results
                data = display_result(result, "Document comparison")
                if data:
                    st.subheader("Comparison Results")
                    
                    # Display session info
                    if "session_id" in data:
                        st.info(f"Session ID: {data['session_id']}")
                    
                    # Display comparison table
                    if "rows" in data and data["rows"]:
                        df = pd.DataFrame(data["rows"])
                        st.dataframe(df, use_container_width=True)
                        
                        # Download results
                        csv = df.to_csv(index=False)
                        st.download_button(
                            label="Download Comparison Results (CSV)",
                            data=csv,
                            file_name=f"comparison_{reference_file.name}_{actual_file.name}.csv",
                            mime="text/csv"
                        )
                    else:
                        st.success("No differences found between the documents!")

elif page == "Document Chat":
    st.markdown('<div class="main-header">', unsafe_allow_html=True)
    st.title("Document Chat")
    st.markdown("Upload documents and chat with them using AI-powered question answering")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Initialize session state
    if "chat_session_id" not in st.session_state:
        st.session_state.chat_session_id = None
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []
    if "index_built" not in st.session_state:
        st.session_state.index_built = False
    
    # Document indexing section
    st.subheader("Step 1: Upload and Index Documents")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        uploaded_files = st.file_uploader(
            "Choose documents to upload", 
            type=['pdf', 'docx', 'txt'],
            accept_multiple_files=True,
            help="You can upload multiple files. Supported formats: PDF, DOCX, TXT"
        )
    
    with col2:
        st.markdown("**Index Settings**")
        chunk_size = st.number_input("Chunk Size", value=1000, min_value=200, step=100)
        chunk_overlap = st.number_input("Chunk Overlap", value=200, min_value=0, step=50)
        k_value = st.number_input("Top-K Results", value=5, min_value=1, max_value=20)
    
    # Advanced settings
    with st.expander("Advanced Settings"):
        session_id = st.text_input("Custom Session ID (optional)", placeholder="Leave blank for auto-generated")
        use_session_dirs = st.checkbox("Use Session-based Storage", value=True)
    
    if uploaded_files:
        st.markdown(f'<div class="info-box">Ready to index {len(uploaded_files)} file(s)</div>', unsafe_allow_html=True)
        
        if st.button("Build/Update Index", type="primary"):
            with st.spinner("Building document index... This may take a few moments."):
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
                
                # Make API request
                result = make_api_request("/chat/index", method="POST", files=dict(files), data=form_data)
                
                # Display results
                data = display_result(result, "Document indexing")
                if data:
                    st.session_state.chat_session_id = data.get("session_id")
                    st.session_state.index_built = True
                    st.success(f"Index built successfully! Session ID: {st.session_state.chat_session_id}")
    
    # Chat section
    st.markdown("---")
    st.subheader("Step 2: Chat with Your Documents")
    
    if not st.session_state.index_built:
        st.warning("Please upload and index documents first before starting a chat.")
    else:
        # Display chat history
        if st.session_state.chat_messages:
            st.subheader("Chat History")
            for i, message in enumerate(st.session_state.chat_messages):
                if message["role"] == "user":
                    st.markdown(f"**You:** {message['content']}")
                else:
                    st.markdown(f"**Assistant:** {message['content']}")
                st.markdown("---")
        
        # Chat input
        question = st.text_input("Ask a question about your documents:", key="chat_input")
        
        col1, col2 = st.columns([1, 4])
        with col1:
            send_button = st.button("Send Question", type="primary")
        with col2:
            if st.button("Clear Chat History"):
                st.session_state.chat_messages = []
                st.rerun()
        
        if send_button and question:
            with st.spinner("Getting answer from your documents..."):
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
                
                # Add user message to chat
                st.session_state.chat_messages.append({"role": "user", "content": question})
                
                # Process response
                if result["success"]:
                    data = result["data"]
                    answer = data.get("answer", "No answer received")
                    st.session_state.chat_messages.append({"role": "assistant", "content": answer})
                    st.rerun()
                else:
                    error_msg = f"Error: {result['error']}"
                    st.session_state.chat_messages.append({"role": "assistant", "content": error_msg})
                    st.rerun()

# Footer
st.markdown("---")
st.markdown("Document Portal - Streamlit UI")
