"""
Enhanced Streamlit app for batch OMR processing with OCR and PDF report generation.
"""

import os
import uuid
import json
import tempfile
import zipfile
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

import streamlit as st
import pandas as pd
from PIL import Image

# Import our enhanced processors
from enhanced_omr_utils import EnhancedOMRProcessor
from pdf_generator import OMRReportGenerator

# Configure page
st.set_page_config(
    page_title="Batch OMR Checker", 
    page_icon="📊", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'processing_results' not in st.session_state:
    st.session_state.processing_results = []
if 'answer_key' not in st.session_state:
    st.session_state.answer_key = {}
if 'exam_name' not in st.session_state:
    st.session_state.exam_name = "OMR Test"

# Setup directories
BASE_DIR = Path(__file__).parent
UPLOAD_DIR = BASE_DIR / "batch_uploads"
RESULTS_DIR = BASE_DIR / "batch_results"
TEMP_DIR = BASE_DIR / "temp"

for directory in [UPLOAD_DIR, RESULTS_DIR, TEMP_DIR]:
    directory.mkdir(exist_ok=True)

def main():
    """Main application function."""
    
    st.title("🎯 Batch OMR Checker")
    st.markdown("---")
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Exam name
        exam_name = st.text_input("Exam Name", value=st.session_state.exam_name)
        st.session_state.exam_name = exam_name
        
        # Processing mode selection
        processing_mode = st.radio(
            "Processing Mode",
            ["Use Reference Sheet", "Use Existing Answer Key"],
            help="Choose how to determine correct answers"
        )
        
        st.markdown("---")
        st.header("📋 Instructions")
        st.markdown("""
        **Step 1:** Choose processing mode
        - **Reference Sheet**: Upload a filled answer sheet with correct answers
        - **Answer Key**: Use existing JSON answer key
        
        **Step 2:** Upload student answer sheets
        - Upload multiple images (JPG, PNG)
        - Each sheet should have student name and roll number written clearly
        
        **Step 3:** Process and download reports
        - View results in real-time
        - Download PDF and CSV reports
        """)
    
    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("📝 Step 1: Setup Answer Key")
        
        if processing_mode == "Use Reference Sheet":
            setup_reference_sheet()
        else:
            setup_existing_answer_key()
    
    with col2:
        st.header("📤 Step 2: Upload Student Sheets")
        upload_student_sheets()
    
    # Processing section
    st.markdown("---")
    st.header("⚡ Step 3: Process & Results")
    
    col3, col4 = st.columns([1, 1])
    
    with col3:
        process_batch()
    
    with col4:
        display_results()
    
    # Download section
    if st.session_state.processing_results:
        st.markdown("---")
        st.header("📥 Step 4: Download Reports")
        download_reports()

def setup_reference_sheet():
    """Setup answer key using reference sheet."""
    st.subheader("Upload Reference Answer Sheet")
    
    reference_file = st.file_uploader(
        "Upload the answer sheet with correct answers marked",
        type=['jpg', 'jpeg', 'png'],
        key="reference_upload",
        help="Upload a clear image of the answer sheet with correct answers filled"
    )
    
    if reference_file is not None:
        # Display preview
        st.image(reference_file, caption="Reference Sheet Preview", use_container_width=True)
        
        if st.button("🔍 Extract Answer Key from Reference", type="primary"):
            with st.spinner("Processing reference sheet..."):
                try:
                    # Save reference file temporarily
                    temp_path = TEMP_DIR / f"reference_{uuid.uuid4()}.jpg"
                    with open(temp_path, "wb") as f:
                        f.write(reference_file.getbuffer())
                    
                    # Process reference sheet
                    processor = EnhancedOMRProcessor()
                    answer_key = processor.process_reference_sheet(str(temp_path))
                    
                    # Clean up temp file
                    os.remove(temp_path)
                    
                    # Store answer key
                    st.session_state.answer_key = answer_key
                    
                    st.success(f"✅ Answer key extracted! Found answers for {len(answer_key)} questions.")
                    
                    # Display extracted answers
                    st.subheader("Extracted Answer Key")
                    answer_df = pd.DataFrame([
                        {"Question": q, "Answer": a} 
                        for q, a in sorted(answer_key.items(), key=lambda x: int(x[0]))
                    ])
                    st.dataframe(answer_df, use_container_width=True)
                    
                except Exception as e:
                    st.error(f"❌ Error processing reference sheet: {str(e)}")

def setup_existing_answer_key():
    """Setup answer key using existing JSON files."""
    st.subheader("Select Existing Answer Key")
    
    # Load available answer keys
    answer_keys_dir = BASE_DIR / "answer_keys"
    answer_keys = []
    
    if answer_keys_dir.exists():
        answer_keys = [f.stem for f in answer_keys_dir.glob("*.json")]
    
    if answer_keys:
        selected_key = st.selectbox("Choose Answer Key", answer_keys)
        
        if st.button("📋 Load Answer Key", type="primary"):
            try:
                key_path = answer_keys_dir / f"{selected_key}.json"
                with open(key_path, 'r') as f:
                    answer_key = json.load(f)
                
                st.session_state.answer_key = answer_key
                st.success(f"✅ Answer key '{selected_key}' loaded successfully!")
                
                # Display answer key
                st.subheader("Loaded Answer Key")
                answer_df = pd.DataFrame([
                    {"Question": q, "Answer": a} 
                    for q, a in sorted(answer_key.items(), key=lambda x: int(x[0]))
                ])
                st.dataframe(answer_df, use_container_width=True)
                
            except Exception as e:
                st.error(f"❌ Error loading answer key: {str(e)}")
    else:
        st.warning("⚠️ No answer key files found in 'answer_keys' directory.")
        
        # Option to create new answer key
        st.subheader("Create New Answer Key")
        
        num_questions = st.number_input("Number of Questions", min_value=1, max_value=50, value=10)
        
        if st.button("➕ Create Answer Key Form"):
            st.session_state.create_answer_key = True
            st.session_state.num_questions = num_questions
        
        if getattr(st.session_state, 'create_answer_key', False):
            create_answer_key_form(st.session_state.num_questions)

def create_answer_key_form(num_questions: int):
    """Create form for manual answer key entry."""
    st.subheader("Enter Correct Answers")
    
    answers = {}
    cols = st.columns(5)
    
    for i in range(1, num_questions + 1):
        col_idx = (i - 1) % 5
        with cols[col_idx]:
            answer = st.selectbox(f"Q{i}", ["A", "B", "C", "D", "E"], key=f"q_{i}")
            answers[str(i)] = answer
    
    col_save, col_cancel = st.columns([1, 1])
    
    with col_save:
        if st.button("💾 Save Answer Key", type="primary"):
            st.session_state.answer_key = answers
            st.session_state.create_answer_key = False
            st.success("✅ Answer key created successfully!")
            st.experimental_rerun()
    
    with col_cancel:
        if st.button("❌ Cancel"):
            st.session_state.create_answer_key = False
            st.experimental_rerun()

def upload_student_sheets():
    """Handle student answer sheet uploads."""
    st.subheader("Upload Student Answer Sheets")
    
    uploaded_files = st.file_uploader(
        "Upload multiple student answer sheets",
        type=['jpg', 'jpeg', 'png'],
        accept_multiple_files=True,
        key="student_uploads",
        help="Upload clear images of student answer sheets with names and roll numbers visible"
    )
    
    if uploaded_files:
        st.success(f"📁 {len(uploaded_files)} files uploaded successfully!")
        
        # Show preview of first few files
        st.subheader("Preview (First 3 files)")
        
        preview_cols = st.columns(3)
        for i, file in enumerate(uploaded_files[:3]):
            with preview_cols[i]:
                st.image(file, caption=f"{file.name}", use_container_width=True)
        
        if len(uploaded_files) > 3:
            st.info(f"... and {len(uploaded_files) - 3} more files")
        
        # Store files in session state
        st.session_state.uploaded_files = uploaded_files

def process_batch():
    """Process batch of student answer sheets."""
    st.subheader("Batch Processing")
    
    # Check if we have everything needed
    has_answer_key = bool(st.session_state.answer_key)
    has_files = hasattr(st.session_state, 'uploaded_files') and st.session_state.uploaded_files
    
    st.write(f"✅ Answer Key: {'Ready' if has_answer_key else 'Not Set'}")
    st.write(f"✅ Student Sheets: {len(getattr(st.session_state, 'uploaded_files', [])) if has_files else 0} files")
    
    if has_answer_key and has_files:
        if st.button("🚀 Start Batch Processing", type="primary"):
            process_all_sheets()
    else:
        st.warning("⚠️ Please complete Steps 1 and 2 before processing.")

def process_all_sheets():
    """Process all uploaded student sheets."""
    processor = EnhancedOMRProcessor()
    results = []
    
    # Create progress bar
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    total_files = len(st.session_state.uploaded_files)
    
    for i, uploaded_file in enumerate(st.session_state.uploaded_files):
        try:
            # Update progress
            progress = (i + 1) / total_files
            progress_bar.progress(progress)
            status_text.text(f"Processing {uploaded_file.name} ({i+1}/{total_files})")
            
            # Save file temporarily
            temp_path = TEMP_DIR / f"student_{uuid.uuid4()}.jpg"
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Process student sheet
            result = processor.process_student_sheet(str(temp_path), st.session_state.answer_key)
            result['filename'] = uploaded_file.name
            results.append(result)
            
            # Clean up temp file
            os.remove(temp_path)
            
        except Exception as e:
            st.error(f"❌ Error processing {uploaded_file.name}: {str(e)}")
            # Add error result
            results.append({
                'filename': uploaded_file.name,
                'error': str(e),
                'student_info': {'name': 'Error', 'roll_number': 'Error'},
                'omr_result': None
            })
    
    # Store results
    st.session_state.processing_results = results
    
    # Clear progress indicators
    progress_bar.empty()
    status_text.empty()
    
    st.success(f"🎉 Batch processing completed! Processed {len(results)} sheets.")

def display_results():
    """Display processing results."""
    st.subheader("Processing Results")
    
    if st.session_state.processing_results:
        # Summary statistics
        valid_results = [r for r in st.session_state.processing_results if r.get('omr_result')]
        
        if valid_results:
            scores = [r['omr_result'].score for r in valid_results]
            percentages = [r['omr_result'].percentage for r in valid_results]
            
            col_stats1, col_stats2, col_stats3 = st.columns(3)
            
            with col_stats1:
                st.metric("Total Students", len(st.session_state.processing_results))
            
            with col_stats2:
                avg_score = sum(scores) / len(scores) if scores else 0
                st.metric("Average Score", f"{avg_score:.1f}")
            
            with col_stats3:
                avg_percentage = sum(percentages) / len(percentages) if percentages else 0
                st.metric("Average %", f"{avg_percentage:.1f}%")
            
            # Results table
            st.subheader("Detailed Results")
            
            table_data = []
            for result in st.session_state.processing_results:
                if result.get('omr_result'):
                    student_info = result.get('student_info', {})
                    omr_result = result['omr_result']
                    
                    table_data.append({
                        'Name': student_info.get('name', 'Unknown'),
                        'Roll Number': student_info.get('roll_number', 'Unknown'),
                        'Score': f"{omr_result.score}/{omr_result.total}",
                        'Percentage': f"{omr_result.percentage}%",
                        'Grade': calculate_grade(omr_result.percentage),
                        'File': result.get('filename', 'Unknown')
                    })
                else:
                    # Error case
                    table_data.append({
                        'Name': 'Error',
                        'Roll Number': 'Error',
                        'Score': 'Error',
                        'Percentage': 'Error',
                        'Grade': 'Error',
                        'File': result.get('filename', 'Unknown')
                    })
            
            df = pd.DataFrame(table_data)
            st.dataframe(df, use_container_width=True)
        
        else:
            st.warning("⚠️ No valid results found. Please check your images and try again.")
    
    else:
        st.info("📊 Results will appear here after processing.")

def calculate_grade(percentage: float) -> str:
    """Calculate grade based on percentage."""
    if percentage >= 90:
        return 'A+'
    elif percentage >= 80:
        return 'A'
    elif percentage >= 70:
        return 'B+'
    elif percentage >= 60:
        return 'B'
    elif percentage >= 50:
        return 'C'
    elif percentage >= 40:
        return 'D'
    else:
        return 'F'

def download_reports():
    """Generate and provide download links for reports."""
    st.subheader("Download Reports")
    
    col_pdf, col_csv = st.columns(2)
    
    with col_pdf:
        if st.button("📄 Generate PDF Report", type="primary"):
            with st.spinner("Generating PDF report..."):
                try:
                    report_generator = OMRReportGenerator()
                    
                    # Generate PDF
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    pdf_path = RESULTS_DIR / f"omr_report_{timestamp}.pdf"
                    
                    report_generator.generate_batch_report(
                        st.session_state.processing_results,
                        st.session_state.exam_name,
                        str(pdf_path)
                    )
                    
                    # Provide download
                    with open(pdf_path, "rb") as pdf_file:
                        st.download_button(
                            label="📥 Download PDF Report",
                            data=pdf_file.read(),
                            file_name=f"omr_report_{timestamp}.pdf",
                            mime="application/pdf"
                        )
                    
                    st.success("✅ PDF report generated successfully!")
                    
                except Exception as e:
                    st.error(f"❌ Error generating PDF: {str(e)}")
    
    with col_csv:
        if st.button("📊 Generate CSV Report", type="secondary"):
            with st.spinner("Generating CSV report..."):
                try:
                    report_generator = OMRReportGenerator()
                    
                    # Generate CSV
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    csv_path = RESULTS_DIR / f"omr_results_{timestamp}.csv"
                    
                    report_generator.generate_summary_csv(
                        st.session_state.processing_results,
                        str(csv_path)
                    )
                    
                    # Provide download
                    with open(csv_path, "rb") as csv_file:
                        st.download_button(
                            label="📥 Download CSV Report",
                            data=csv_file.read(),
                            file_name=f"omr_results_{timestamp}.csv",
                            mime="text/csv"
                        )
                    
                    st.success("✅ CSV report generated successfully!")
                    
                except Exception as e:
                    st.error(f"❌ Error generating CSV: {str(e)}")
    
    # Clear results button
    st.markdown("---")
    if st.button("🗑️ Clear All Results", type="secondary"):
        st.session_state.processing_results = []
        st.session_state.answer_key = {}
        if hasattr(st.session_state, 'uploaded_files'):
            del st.session_state.uploaded_files
        st.success("✅ All results cleared!")
        st.experimental_rerun()

if __name__ == "__main__":
    main()
