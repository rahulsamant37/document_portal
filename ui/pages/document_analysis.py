"""
Document Analysis Page

This page handles single document analysis functionality.
"""

import streamlit as st
import requests
import json
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

def show_analysis_page():
    st.title("Document Analysis")
    st.markdown("Upload a PDF document to get detailed analysis and insights")
    
    # File upload section
    st.subheader("Upload Document")
    uploaded_file = st.file_uploader(
        "Choose a PDF file", 
        type=['pdf'],
        help="Only PDF files are supported for analysis"
    )
    
    if uploaded_file is not None:
        # Display file info
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("File Name", uploaded_file.name)
        with col2:
            st.metric("File Size", f"{uploaded_file.size:,} bytes")
        with col3:
            st.metric("File Type", uploaded_file.type)
        
        st.markdown("---")
        
        # Analysis button
        if st.button("Analyze Document", type="primary", use_container_width=True):
            with st.spinner("Analyzing document... This may take a few moments."):
                # Prepare file for API
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                
                # Make API request
                result = make_api_request("/analyze", method="POST", files=files)
                
                # Display results
                if result["success"]:
                    st.success("Document analysis completed successfully!")
                    data = result["data"]
                    
                    st.subheader("Analysis Results")
                    
                    # Create tabs for different sections of results
                    if isinstance(data, dict):
                        tab_names = list(data.keys())
                        if len(tab_names) > 1:
                            tabs = st.tabs([name.replace('_', ' ').title() for name in tab_names])
                            for i, (key, value) in enumerate(data.items()):
                                with tabs[i]:
                                    if isinstance(value, (dict, list)):
                                        st.json(value)
                                    else:
                                        st.write(value)
                        else:
                            # Single result
                            key, value = list(data.items())[0]
                            st.subheader(key.replace('_', ' ').title())
                            if isinstance(value, (dict, list)):
                                st.json(value)
                            else:
                                st.write(value)
                    else:
                        st.json(data)
                    
                    # Download section
                    st.markdown("---")
                    st.subheader("Download Results")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.download_button(
                            label="Download as JSON",
                            data=json.dumps(data, indent=2),
                            file_name=f"analysis_{uploaded_file.name}.json",
                            mime="application/json",
                            use_container_width=True
                        )
                    with col2:
                        # Convert to text format for simple download
                        text_result = json.dumps(data, indent=2)
                        st.download_button(
                            label="Download as Text",
                            data=text_result,
                            file_name=f"analysis_{uploaded_file.name}.txt",
                            mime="text/plain",
                            use_container_width=True
                        )
                else:
                    st.error(f"Analysis failed: {result['error']}")
    
    else:
        st.info("Please upload a PDF file to begin analysis.")
        
        # Help section
        with st.expander("How to use Document Analysis"):
            st.markdown("""
            **Steps:**
            1. Click 'Browse files' to upload a PDF document
            2. Select your PDF file from your computer
            3. Click 'Analyze Document' to start the analysis
            4. View the results in the expandable sections below
            5. Download the results in JSON or text format if needed
            
            **Supported formats:**
            - PDF files only
            
            **What you'll get:**
            - Structured analysis of document content
            - Key information extraction
            - Document insights and metadata
            """)

if __name__ == "__main__":
    show_analysis_page()
