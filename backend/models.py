"""
Pydantic models for OMR Checker API requests and responses.
"""

from pydantic import BaseModel
from typing import Dict, Optional, Any

class OMRResult(BaseModel):
    """Response model for OMR processing results."""
    score: int
    total: int
    percentage: float
    marked_answers: Dict[str, str]
    correct_answers: Dict[str, str]
    result: Dict[str, str]  # "correct", "incorrect", "not_attempted", "invalid"
    processing_info: Optional[Dict[str, Any]] = None

class ErrorResponse(BaseModel):
    """Error response model."""
    detail: str
    error_code: Optional[str] = None
