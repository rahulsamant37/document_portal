"""
Document Portal - Streamlit Application Launcher

Main entry point for the Document Portal Streamlit application.
This script sets up the main navigation and loads the appropriate pages.
"""

import streamlit as st
import sys
import os

# Add the current directory to Python path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import page modules
from ui.pages.document_analysis import show_analysis_page
from ui.pages.document_comparison import show_comparison_page
from ui.pages.document_chat import show_chat_page

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
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
    }
</style>
""", unsafe_allow_html=True)

# Utility function for API health check
def check_api_health():
    """Check if the backend API is accessible"""
    import requests
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            return True, "API Server is running"
        else:
            return False, f"API Server returned status {response.status_code}"
    except requests.exceptions.ConnectionError:
        return False, "Cannot connect to API server"
    except requests.exceptions.Timeout:
        return False, "API server connection timeout"
    except Exception as e:
        return False, f"API check failed: {str(e)}"

# Sidebar configuration
st.sidebar.title("Document Portal")
st.sidebar.markdown("Navigate between different functionalities")
st.sidebar.markdown("---")

# Page selection
page_options = {
    "Home": "home",
    "Document Analysis": "analysis", 
    "Document Comparison": "comparison",
    "Document Chat": "chat"
}

selected_page = st.sidebar.selectbox(
    "Choose a page:",
    list(page_options.keys()),
    index=0
)

st.sidebar.markdown("---")

# API status section in sidebar
st.sidebar.subheader("System Status")
if st.sidebar.button("Check API Status", key="api_status"):
    with st.sidebar:
        with st.spinner("Checking..."):
            is_healthy, message = check_api_health()
            if is_healthy:
                st.success(message)
            else:
                st.error(message)

# Configuration section in sidebar
with st.sidebar.expander("Configuration"):
    st.markdown("**API Server:** localhost:8000")
    st.markdown("**Supported Files:**")
    st.markdown("- Analysis: PDF")
    st.markdown("- Comparison: PDF") 
    st.markdown("- Chat: PDF, DOCX, TXT")

# Main content area
page_value = page_options[selected_page]

if page_value == "home":
    st.markdown('<div class="main-header">', unsafe_allow_html=True)
    st.title("Document Portal")
    st.markdown("Welcome to the Document Portal - Your AI-powered document processing platform")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Feature overview
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### Document Analysis")
        st.markdown("""
        Upload a PDF document to get:
        - Structured content analysis
        - Key information extraction
        - Document insights and metadata
        - Downloadable results in multiple formats
        """)
        if st.button("Go to Analysis", key="nav_analysis", use_container_width=True):
            st.query_params = {"page": "analysis"}
            st.rerun()
    
    with col2:
        st.markdown("### Document Comparison")
        st.markdown("""
        Compare two PDF documents to identify:
        - Page-by-page differences
        - Content changes and modifications
        - Detailed comparison reports
        - Exportable comparison results
        """)
        if st.button("Go to Comparison", key="nav_comparison", use_container_width=True):
            st.query_params = {"page": "comparison"}
            st.rerun()
    
    with col3:
        st.markdown("### Document Chat")
        st.markdown("""
        Chat with your documents using AI:
        - Upload multiple documents
        - Ask questions in natural language
        - Get AI-powered answers
        - Maintain conversation history
        """)
        if st.button("Go to Chat", key="nav_chat", use_container_width=True):
            st.query_params = {"page": "chat"}
            st.rerun()
    
    st.markdown("---")
    
    # Getting started section
    st.subheader("Getting Started")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        **Quick Start Guide:**
        
        1. **Start the Backend API**
           - Ensure your FastAPI server is running on port 8000
           - Check the API status using the sidebar button
        
        2. **Choose Your Task**
           - Use the sidebar navigation to select a feature
           - Each page is dedicated to a specific functionality
        
        3. **Upload Documents**
           - Follow the instructions on each page
           - Supported formats vary by feature
        
        4. **Process and Download**
           - Process your documents with AI
           - Download results in various formats
        """)
    
    with col2:
        st.markdown("**System Requirements**")
        
        # Check API status for home page
        is_healthy, message = check_api_health()
        if is_healthy:
            st.success("Backend API: Online")
        else:
            st.error("Backend API: Offline")
            st.caption("Start your FastAPI server on port 8000")
        
        st.markdown("**Supported Browsers:**")
        st.markdown("- Chrome, Firefox, Safari, Edge")
        
        st.markdown("**File Size Limits:**")
        st.markdown("- Depends on your server configuration")

elif page_value == "analysis":
    show_analysis_page()

elif page_value == "comparison":
    show_comparison_page()

elif page_value == "chat":
    show_chat_page()

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666; font-size: 0.8em;'>
    Document Portal v1.0 | Built with Streamlit and FastAPI
    </div>
    """, 
    unsafe_allow_html=True
)