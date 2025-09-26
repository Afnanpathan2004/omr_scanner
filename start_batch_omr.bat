@echo off
echo Starting Enhanced Batch OMR Checker...
echo.
echo Installing/Updating dependencies...
pip install -r backend\enhanced_requirements.txt
echo.
echo Starting Streamlit application...
cd backend
streamlit run batch_omr_app.py
pause
