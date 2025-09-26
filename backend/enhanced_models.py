"""
Enhanced Pydantic models for batch OMR processing with student information.
"""

from pydantic import BaseModel
from typing import Dict, Optional, Any, List
from datetime import datetime

class StudentInfo(BaseModel):
    """Model for student information extracted via OCR."""
    name: str = "Unknown"
    roll_number: str = "Unknown"
    confidence_score: Optional[float] = None

class OMRResult(BaseModel):
    """Response model for OMR processing results."""
    score: int
    total: int
    percentage: float
    marked_answers: Dict[str, str]
    correct_answers: Dict[str, str]
    result: Dict[str, str]  # "correct", "incorrect", "not_attempted", "invalid"
    processing_info: Optional[Dict[str, Any]] = None

class StudentResult(BaseModel):
    """Complete result for a single student."""
    student_info: StudentInfo
    omr_result: OMRResult
    image_path: Optional[str] = None
    processing_time: Optional[float] = None
    error_message: Optional[str] = None

class BatchProcessingResult(BaseModel):
    """Result for batch processing of multiple students."""
    exam_name: str
    total_students: int
    successful_processing: int
    failed_processing: int
    processing_time: float
    timestamp: datetime
    results: List[StudentResult]
    summary_statistics: Optional[Dict[str, Any]] = None

class AnswerKey(BaseModel):
    """Model for answer key information."""
    exam_id: str
    exam_name: str
    total_questions: int
    answers: Dict[str, str]
    created_date: datetime
    source: str  # "reference_sheet", "manual", "json_file"

class ProcessingConfig(BaseModel):
    """Configuration for OMR processing."""
    questions_per_row: int = 5
    total_questions: int = 10
    bubble_threshold: float = 0.65
    gaussian_blur_kernel: tuple = (5, 5)
    threshold_value: int = 180
    min_contour_area: int = 20
    max_contour_area: int = 400
    ocr_confidence_threshold: float = 0.5

class ReportConfig(BaseModel):
    """Configuration for report generation."""
    include_individual_reports: bool = True
    include_question_analysis: bool = True
    include_statistics: bool = True
    grade_scale: Dict[str, tuple] = {
        "A+": (90, 100),
        "A": (80, 89),
        "B+": (70, 79),
        "B": (60, 69),
        "C": (50, 59),
        "D": (40, 49),
        "F": (0, 39)
    }

class ErrorResponse(BaseModel):
    """Error response model."""
    detail: str
    error_code: Optional[str] = None
    timestamp: datetime = datetime.now()
    
class ProcessingStatus(BaseModel):
    """Status model for batch processing progress."""
    total_files: int
    processed_files: int
    current_file: str
    progress_percentage: float
    estimated_time_remaining: Optional[float] = None
    errors: List[str] = []
