"""
Document Comparison Page

This page handles document comparison functionality.
"""

import streamlit as st
import requests
import pandas as pd
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

def show_comparison_page():
    st.title("Document Comparison")
    st.markdown("Compare two PDF documents to identify differences and changes")
    
    # File upload section
    st.subheader("Upload Documents for Comparison")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Reference Document**")
        reference_file = st.file_uploader(
            "Upload reference PDF", 
            type=['pdf'],
            key="reference",
            help="This will be used as the baseline for comparison"
        )
        
        if reference_file:
            st.success(f"Reference: {reference_file.name}")
            st.caption(f"Size: {reference_file.size:,} bytes")
    
    with col2:
        st.markdown("**Actual Document**")
        actual_file = st.file_uploader(
            "Upload actual PDF", 
            type=['pdf'],
            key="actual",
            help="This document will be compared against the reference"
        )
        
        if actual_file:
            st.success(f"Actual: {actual_file.name}")
            st.caption(f"Size: {actual_file.size:,} bytes")
    
    # Comparison section
    if reference_file and actual_file:
        st.markdown("---")
        st.subheader("Comparison Settings")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.info("Reference Document Ready")
        with col2:
            st.info("Actual Document Ready")
        with col3:
            if st.button("Compare Documents", type="primary", use_container_width=True):
                with st.spinner("Comparing documents... This may take a few moments."):
                    # Prepare files for API
                    files = {
                        "reference": (reference_file.name, reference_file.getvalue(), reference_file.type),
                        "actual": (actual_file.name, actual_file.getvalue(), actual_file.type)
                    }
                    
                    # Make API request
                    result = make_api_request("/compare", method="POST", files=files)
                    
                    # Display results
                    if result["success"]:
                        st.success("Document comparison completed successfully!")
                        data = result["data"]
                        
                        # Display session info
                        if "session_id" in data:
                            st.info(f"Comparison Session ID: {data['session_id']}")
                        
                        st.subheader("Comparison Results")
                        
                        # Display comparison table
                        if "rows" in data and data["rows"]:
                            df = pd.DataFrame(data["rows"])
                            
                            # Display metrics
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Total Changes", len(df))
                            with col2:
                                if "Page" in df.columns:
                                    unique_pages = df["Page"].nunique() if "Page" in df.columns else 0
                                    st.metric("Pages with Changes", unique_pages)
                            with col3:
                                st.metric("Comparison Status", "Complete")
                            
                            # Display the comparison table
                            st.dataframe(
                                df, 
                                use_container_width=True,
                                hide_index=True
                            )
                            
                            # Download options
                            st.markdown("---")
                            st.subheader("Download Results")
                            
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                csv = df.to_csv(index=False)
                                st.download_button(
                                    label="Download as CSV",
                                    data=csv,
                                    file_name=f"comparison_{reference_file.name}_{actual_file.name}.csv",
                                    mime="text/csv",
                                    use_container_width=True
                                )
                            with col2:
                                excel_data = df.to_excel(index=False)
                                st.download_button(
                                    label="Download as Excel",
                                    data=excel_data,
                                    file_name=f"comparison_{reference_file.name}_{actual_file.name}.xlsx",
                                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                    use_container_width=True
                                )
                            with col3:
                                json_data = df.to_json(orient='records', indent=2)
                                st.download_button(
                                    label="Download as JSON",
                                    data=json_data,
                                    file_name=f"comparison_{reference_file.name}_{actual_file.name}.json",
                                    mime="application/json",
                                    use_container_width=True
                                )
                            
                        else:
                            st.success("No differences found between the documents!")
                            st.balloons()
                    else:
                        st.error(f"Comparison failed: {result['error']}")
    
    else:
        st.info("Please upload both reference and actual PDF files to begin comparison.")
        
        # Help section
        with st.expander("How to use Document Comparison"):
            st.markdown("""
            **Steps:**
            1. Upload a reference PDF document (your baseline)
            2. Upload an actual PDF document (to compare against the reference)
            3. Click 'Compare Documents' to start the comparison
            4. View the results in the table below
            5. Download the results in CSV, Excel, or JSON format
            
            **Supported formats:**
            - PDF files only
            
            **What you'll get:**
            - Page-by-page comparison results
            - Detailed changes and differences
            - Exportable results in multiple formats
            
            **Tips:**
            - Use descriptive file names for easier identification
            - The reference document should be your original or baseline version
            - The actual document should be the version you want to check for changes
            """)

if __name__ == "__main__":
    show_comparison_page()
