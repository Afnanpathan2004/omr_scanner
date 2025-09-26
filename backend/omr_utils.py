"""
OMR processing utilities using OpenCV for bubble detection and analysis.
"""

import cv2
import numpy as np
import logging
from typing import Dict, Tuple, List, Optional
from pathlib import Path
import json

from models import OMRResult

logger = logging.getLogger(__name__)

class OMRProcessor:
    """Main class for OMR sheet processing and evaluation."""
    
    def __init__(self):
        """Initialize OMR processor with default parameters."""
        # OMR sheet configuration (adjust based on your template)
        self.questions_per_row = 5  # Number of answer choices per question
        self.total_questions = 10   # Total number of questions
        self.bubble_threshold = 0.65  # Threshold for filled bubble detection
        
        # Image processing parameters
        self.gaussian_blur_kernel = (5, 5)
        self.threshold_value = 180
        self.min_contour_area = 20
        self.max_contour_area = 400
        
    def process_omr_sheet(self, image_path: str, answer_key: Dict[str, str]) -> OMRResult:
        """
        Process OMR sheet and return evaluation results.
        
        Args:
            image_path: Path to the uploaded image
            answer_key: Dictionary with correct answers
            
        Returns:
            OMRResult: Processing results with score and analysis
        """
        try:
            # Load and preprocess image
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"Could not load image from {image_path}")
            
            logger.info(f"Processing image: {image_path}")
            
            # Preprocess image
            processed_image = self._preprocess_image(image)
            
            # Detect bubbles
            bubbles = self._detect_bubbles(processed_image)
            
            # Analyze filled bubbles
            marked_answers = self._analyze_bubbles(processed_image, bubbles)
            
            # Compare with answer key and calculate score
            result = self._evaluate_answers(marked_answers, answer_key)
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing OMR sheet: {str(e)}")
            raise
    
    def _preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """
        Preprocess image for better bubble detection.
        
        Args:
            image: Input image
            
        Returns:
            Preprocessed grayscale image
        """
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, self.gaussian_blur_kernel, 0)
        
        # Apply adaptive thresholding for better bubble detection
        thresh = cv2.adaptiveThreshold(
            blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY_INV, 11, 2
        )
        
        return thresh
    
    def _detect_bubbles(self, image: np.ndarray) -> List[Dict]:
        """
        Detect bubble contours in the processed image.
        
        Args:
            image: Preprocessed binary image
            
        Returns:
            List of bubble information dictionaries
        """
        # Find contours
        contours, _ = cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        bubbles = []
        
        for contour in contours:
            # Calculate contour area
            area = cv2.contourArea(contour)
            
            # Filter contours by area (bubble size)
            if self.min_contour_area < area < self.max_contour_area:
                # Get bounding rectangle
                x, y, w, h = cv2.boundingRect(contour)
                
                # Check if contour is roughly circular (aspect ratio close to 1)
                aspect_ratio = w / float(h)
                if 0.7 <= aspect_ratio <= 1.3:
                    bubbles.append({
                        'contour': contour,
                        'x': x,
                        'y': y,
                        'w': w,
                        'h': h,
                        'area': area,
                        'center': (x + w//2, y + h//2)
                    })
        
        # Sort bubbles by position (top to bottom, left to right)
        bubbles.sort(key=lambda b: (b['y'], b['x']))
        
        logger.info(f"Detected {len(bubbles)} potential bubbles")
        return bubbles
    
    def _analyze_bubbles(self, image: np.ndarray, bubbles: List[Dict]) -> Dict[str, str]:
        """
        Analyze bubbles to determine which ones are filled.
        
        Args:
            image: Preprocessed binary image
            bubbles: List of detected bubbles
            
        Returns:
            Dictionary mapping question numbers to selected answers
        """
        marked_answers = {}
        
        # Group bubbles by rows (questions)
        bubble_rows = self._group_bubbles_by_rows(bubbles)
        
        for question_num, row_bubbles in enumerate(bubble_rows, 1):
            if len(row_bubbles) != self.questions_per_row:
                logger.warning(f"Question {question_num}: Expected {self.questions_per_row} bubbles, found {len(row_bubbles)}")
                continue
            
            # Analyze each bubble in the row
            bubble_scores = []
            for bubble in row_bubbles:
                # Extract bubble region
                x, y, w, h = bubble['x'], bubble['y'], bubble['w'], bubble['h']
                bubble_region = image[y:y+h, x:x+w]
                
                # Calculate fill percentage
                total_pixels = bubble_region.size
                filled_pixels = np.sum(bubble_region == 255)  # White pixels in binary image
                fill_percentage = filled_pixels / total_pixels if total_pixels > 0 else 0
                
                bubble_scores.append(fill_percentage)
            
            # Determine marked answer
            max_fill = max(bubble_scores)
            if max_fill > self.bubble_threshold:
                # Find the index of the most filled bubble
                marked_index = bubble_scores.index(max_fill)
                marked_letter = chr(ord('A') + marked_index)
                marked_answers[str(question_num)] = marked_letter
                
                logger.debug(f"Question {question_num}: Marked {marked_letter} (fill: {max_fill:.2f})")
            else:
                logger.debug(f"Question {question_num}: Not attempted (max fill: {max_fill:.2f})")
        
        return marked_answers
    
    def _group_bubbles_by_rows(self, bubbles: List[Dict]) -> List[List[Dict]]:
        """
        Group bubbles into rows representing questions.
        
        Args:
            bubbles: List of detected bubbles
            
        Returns:
            List of bubble rows
        """
        if not bubbles:
            return []
        
        rows = []
        current_row = [bubbles[0]]
        current_y = bubbles[0]['y']
        
        for bubble in bubbles[1:]:
            # If bubble is roughly on the same horizontal line
            if abs(bubble['y'] - current_y) < 30:  # Tolerance for row alignment
                current_row.append(bubble)
            else:
                # Start new row
                if current_row:
                    # Sort current row by x-coordinate (left to right)
                    current_row.sort(key=lambda b: b['x'])
                    rows.append(current_row)
                current_row = [bubble]
                current_y = bubble['y']
        
        # Add the last row
        if current_row:
            current_row.sort(key=lambda b: b['x'])
            rows.append(current_row)
        
        return rows
    
    def _evaluate_answers(self, marked_answers: Dict[str, str], answer_key: Dict[str, str]) -> OMRResult:
        """
        Evaluate marked answers against the answer key.
        
        Args:
            marked_answers: Dictionary of marked answers
            answer_key: Dictionary of correct answers
            
        Returns:
            OMRResult with evaluation results
        """
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
        
        # Fill in missing marked answers with empty strings
        complete_marked_answers = {}
        for question_num in answer_key.keys():
            complete_marked_answers[question_num] = marked_answers.get(question_num, "")
        
        processing_info = {
            "total_bubbles_detected": len(marked_answers),
            "detection_threshold": self.bubble_threshold,
            "image_processing": "adaptive_threshold"
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
