"""
Mock OMR processing utilities for testing without OpenCV.
"""

import logging
from typing import Dict
from models import OMRResult

logger = logging.getLogger(__name__)

class OMRProcessor:
    """Mock OMR processor for testing without OpenCV."""
    
    def __init__(self):
        """Initialize mock processor."""
        pass
    
    def process_omr_sheet(self, image_path: str, answer_key: Dict[str, str]) -> OMRResult:
        """
        Mock process OMR sheet - returns sample results for testing.
        
        Args:
            image_path: Path to the uploaded image
            answer_key: Dictionary with correct answers
            
        Returns:
            OMRResult: Mock processing results
        """
        logger.info(f"Mock processing image: {image_path}")
        
        # Mock marked answers (simulate some correct, some incorrect)
        marked_answers = {
            "1": "A",
            "2": "C",  # Incorrect if answer key has B
            "3": "C",
            "4": "D",
            "5": "A",
            "6": "",   # Not attempted
            "7": "B",
            "8": "D",
            "9": "",   # Not attempted
            "10": "A"
        }
        
        # Calculate results
        total_questions = len(answer_key)
        correct_count = 0
        result_details = {}
        
        for question_num, correct_answer in answer_key.items():
            marked_answer = marked_answers.get(question_num, "")
            
            if not marked_answer:
                result_details[question_num] = "not_attempted"
            elif marked_answer == correct_answer:
                result_details[question_num] = "correct"
                correct_count += 1
            else:
                result_details[question_num] = "incorrect"
        
        percentage = (correct_count / total_questions * 100) if total_questions > 0 else 0
        
        # Fill in missing marked answers
        complete_marked_answers = {}
        for question_num in answer_key.keys():
            complete_marked_answers[question_num] = marked_answers.get(question_num, "")
        
        processing_info = {
            "total_bubbles_detected": len([a for a in marked_answers.values() if a]),
            "detection_threshold": 0.65,
            "image_processing": "mock_processing"
        }
        
        return OMRResult(
            score=correct_count,
            total=total_questions,
            percentage=round(percentage, 2),
            marked_answers=complete_marked_answers,
            correct_answers=answer_key,
            result=result_details,
            processing_info=processing_info
        )
