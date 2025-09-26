"""
Demo data generator for testing the enhanced OMR checker.
"""

import json
import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import random

def create_sample_answer_keys():
    """Create sample answer keys for testing."""
    
    base_dir = Path(__file__).parent
    answer_keys_dir = base_dir / "answer_keys"
    answer_keys_dir.mkdir(exist_ok=True)
    
    # Sample answer key 1 - Math Test
    math_answers = {
        "1": "A", "2": "B", "3": "C", "4": "D", "5": "A",
        "6": "B", "7": "C", "8": "D", "9": "A", "10": "B"
    }
    
    with open(answer_keys_dir / "math_test.json", "w") as f:
        json.dump(math_answers, f, indent=2)
    
    # Sample answer key 2 - Science Test
    science_answers = {
        "1": "C", "2": "A", "3": "B", "4": "D", "5": "C",
        "6": "A", "7": "B", "8": "D", "9": "C", "10": "A"
    }
    
    with open(answer_keys_dir / "science_test.json", "w") as f:
        json.dump(science_answers, f, indent=2)
    
    # Sample answer key 3 - English Test
    english_answers = {
        "1": "B", "2": "D", "3": "A", "4": "C", "5": "B",
        "6": "D", "7": "A", "8": "C", "9": "B", "10": "D"
    }
    
    with open(answer_keys_dir / "english_test.json", "w") as f:
        json.dump(english_answers, f, indent=2)
    
    print("✅ Created sample answer keys:")
    print("   - math_test.json")
    print("   - science_test.json") 
    print("   - english_test.json")

def create_sample_omr_sheet(student_name, roll_number, answers, filename):
    """Create a sample OMR sheet image for testing."""
    
    # Create a white image (A4 size simulation)
    width, height = 800, 1000
    img = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(img)
    
    try:
        # Try to use a default font
        font_large = ImageFont.truetype("arial.ttf", 24)
        font_medium = ImageFont.truetype("arial.ttf", 18)
        font_small = ImageFont.truetype("arial.ttf", 14)
    except:
        # Fallback to default font
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # Draw header
    draw.text((50, 30), "OMR ANSWER SHEET", fill='black', font=font_large)
    
    # Draw student information area
    draw.text((50, 80), f"Name: {student_name}", fill='black', font=font_medium)
    draw.text((50, 110), f"Roll Number: {roll_number}", fill='black', font=font_medium)
    
    # Draw a line separator
    draw.line([(50, 150), (750, 150)], fill='black', width=2)
    
    # Draw questions and bubbles
    start_y = 180
    bubble_radius = 12
    
    for i in range(1, 11):  # 10 questions
        question_y = start_y + (i-1) * 50
        
        # Question number
        draw.text((50, question_y), f"Q{i}:", fill='black', font=font_medium)
        
        # Draw 5 bubbles (A, B, C, D, E)
        for j, option in enumerate(['A', 'B', 'C', 'D', 'E']):
            bubble_x = 120 + j * 80
            bubble_y = question_y + 5
            
            # Draw bubble circle
            draw.ellipse([bubble_x - bubble_radius, bubble_y - bubble_radius,
                         bubble_x + bubble_radius, bubble_y + bubble_radius], 
                        outline='black', width=2)
            
            # Fill bubble if it's the selected answer
            if answers.get(str(i)) == option:
                draw.ellipse([bubble_x - bubble_radius + 3, bubble_y - bubble_radius + 3,
                             bubble_x + bubble_radius - 3, bubble_y + bubble_radius - 3], 
                            fill='black')
            
            # Draw option letter
            draw.text((bubble_x - 5, bubble_y + 20), option, fill='black', font=font_small)
    
    return img

def create_sample_student_sheets():
    """Create sample student OMR sheets for testing."""
    
    base_dir = Path(__file__).parent
    sample_dir = base_dir / "sample_sheets"
    sample_dir.mkdir(exist_ok=True)
    
    # Sample students with their answers
    students = [
        {
            "name": "JOHN SMITH",
            "roll": "2024001",
            "answers": {"1": "A", "2": "B", "3": "C", "4": "D", "5": "A", 
                       "6": "B", "7": "C", "8": "D", "9": "A", "10": "B"}
        },
        {
            "name": "ALICE JOHNSON", 
            "roll": "2024002",
            "answers": {"1": "A", "2": "C", "3": "C", "4": "D", "5": "A",
                       "6": "B", "7": "B", "8": "D", "9": "A", "10": "B"}
        },
        {
            "name": "BOB WILSON",
            "roll": "2024003", 
            "answers": {"1": "B", "2": "B", "3": "C", "4": "A", "5": "A",
                       "6": "C", "7": "C", "8": "D", "9": "B", "10": "B"}
        },
        {
            "name": "CAROL DAVIS",
            "roll": "2024004",
            "answers": {"1": "A", "2": "B", "3": "A", "4": "D", "5": "C",
                       "6": "B", "7": "C", "8": "C", "9": "A", "10": "A"}
        },
        {
            "name": "DAVID BROWN",
            "roll": "2024005",
            "answers": {"1": "A", "2": "B", "3": "C", "4": "D", "5": "A",
                       "6": "B", "7": "C", "8": "D", "9": "A", "10": "B"}
        }
    ]
    
    print("🎨 Creating sample OMR sheets...")
    
    for student in students:
        filename = f"{student['name'].replace(' ', '_').lower()}_sheet.png"
        img = create_sample_omr_sheet(
            student['name'], 
            student['roll'], 
            student['answers'], 
            filename
        )
        
        img.save(sample_dir / filename)
        print(f"   ✅ Created: {filename}")
    
    # Create a reference sheet (teacher's answer key)
    reference_answers = {"1": "A", "2": "B", "3": "C", "4": "D", "5": "A",
                        "6": "B", "7": "C", "8": "D", "9": "A", "10": "B"}
    
    ref_img = create_sample_omr_sheet("TEACHER REFERENCE", "REF001", reference_answers, "reference.png")
    ref_img.save(sample_dir / "reference_answer_sheet.png")
    print(f"   ✅ Created: reference_answer_sheet.png")
    
    print(f"\n📁 Sample sheets saved in: {sample_dir}")

def main():
    """Create all demo data."""
    print("🚀 Creating demo data for Enhanced OMR Checker...")
    print("=" * 50)
    
    # Create sample answer keys
    create_sample_answer_keys()
    print()
    
    # Create sample OMR sheets
    create_sample_student_sheets()
    
    print("\n" + "=" * 50)
    print("✅ Demo data creation completed!")
    print("\n📋 What was created:")
    print("1. Sample answer keys (JSON files)")
    print("2. Sample student OMR sheets (PNG images)")
    print("3. Reference answer sheet for testing")
    
    print("\n🎯 Next steps:")
    print("1. Run: streamlit run batch_omr_app.py")
    print("2. Use the sample files to test the application")
    print("3. Try both reference sheet and manual answer key modes")

if __name__ == "__main__":
    main()
