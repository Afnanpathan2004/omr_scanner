"""
PDF report generator for OMR batch processing results.
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class OMRReportGenerator:
    """Generate comprehensive PDF reports for OMR batch processing results."""
    
    def __init__(self):
        """Initialize the report generator."""
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles."""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            textColor=colors.darkblue
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomNormal',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=6
        ))
    
    def generate_batch_report(self, results: List[Dict[str, Any]], 
                            exam_name: str = "OMR Test",
                            output_path: str = "omr_batch_report.pdf") -> str:
        """
        Generate comprehensive batch processing report.
        
        Args:
            results: List of student results
            exam_name: Name of the exam
            output_path: Output PDF file path
            
        Returns:
            Path to generated PDF file
        """
        try:
            doc = SimpleDocTemplate(output_path, pagesize=A4)
            story = []
            
            # Title page
            story.extend(self._create_title_page(exam_name, len(results)))
            
            # Summary statistics
            story.extend(self._create_summary_section(results))
            
            # Detailed results table
            story.extend(self._create_detailed_results_table(results))
            
            # Individual student reports
            story.extend(self._create_individual_reports(results))
            
            # Build PDF
            doc.build(story)
            
            logger.info(f"PDF report generated: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error generating PDF report: {str(e)}")
            raise
    
    def _create_title_page(self, exam_name: str, total_students: int) -> List:
        """Create title page elements."""
        elements = []
        
        # Main title
        title = Paragraph(f"OMR Test Results Report", self.styles['CustomTitle'])
        elements.append(title)
        elements.append(Spacer(1, 20))
        
        # Exam details
        exam_info = f"""
        <b>Exam:</b> {exam_name}<br/>
        <b>Total Students:</b> {total_students}<br/>
        <b>Report Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br/>
        """
        
        exam_para = Paragraph(exam_info, self.styles['CustomNormal'])
        elements.append(exam_para)
        elements.append(Spacer(1, 30))
        
        elements.append(PageBreak())
        
        return elements
    
    def _create_summary_section(self, results: List[Dict[str, Any]]) -> List:
        """Create summary statistics section."""
        elements = []
        
        # Section title
        title = Paragraph("Summary Statistics", self.styles['CustomHeading'])
        elements.append(title)
        
        # Calculate statistics
        scores = [r['omr_result'].score for r in results if 'omr_result' in r]
        percentages = [r['omr_result'].percentage for r in results if 'omr_result' in r]
        
        if scores:
            avg_score = sum(scores) / len(scores)
            avg_percentage = sum(percentages) / len(percentages)
            max_score = max(scores)
            min_score = min(scores)
            
            # Pass/fail analysis (assuming 60% as passing)
            passed = sum(1 for p in percentages if p >= 60)
            failed = len(percentages) - passed
            
            stats_data = [
                ['Metric', 'Value'],
                ['Total Students', str(len(results))],
                ['Average Score', f"{avg_score:.1f}"],
                ['Average Percentage', f"{avg_percentage:.1f}%"],
                ['Highest Score', str(max_score)],
                ['Lowest Score', str(min_score)],
                ['Students Passed (≥60%)', str(passed)],
                ['Students Failed (<60%)', str(failed)],
                ['Pass Rate', f"{(passed/len(percentages)*100):.1f}%"]
            ]
            
            stats_table = Table(stats_data, colWidths=[2.5*inch, 2*inch])
            stats_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elements.append(stats_table)
            elements.append(Spacer(1, 20))
        
        return elements
    
    def _create_detailed_results_table(self, results: List[Dict[str, Any]]) -> List:
        """Create detailed results table."""
        elements = []
        
        # Section title
        title = Paragraph("Detailed Results", self.styles['CustomHeading'])
        elements.append(title)
        
        # Prepare table data
        table_data = [['S.No.', 'Name', 'Roll Number', 'Score', 'Total', 'Percentage', 'Grade']]
        
        for i, result in enumerate(results, 1):
            student_info = result.get('student_info', {})
            omr_result = result.get('omr_result')
            
            if omr_result:
                name = student_info.get('name', 'Unknown')
                roll = student_info.get('roll_number', 'Unknown')
                score = omr_result.score
                total = omr_result.total
                percentage = omr_result.percentage
                grade = self._calculate_grade(percentage)
                
                table_data.append([
                    str(i),
                    name,
                    roll,
                    str(score),
                    str(total),
                    f"{percentage}%",
                    grade
                ])
        
        # Create table
        results_table = Table(table_data, colWidths=[0.5*inch, 2*inch, 1.2*inch, 0.7*inch, 0.7*inch, 1*inch, 0.8*inch])
        
        # Style the table
        results_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
        ]))
        
        # Add alternating row colors
        for i in range(1, len(table_data)):
            if i % 2 == 0:
                results_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, i), (-1, i), colors.lightgrey)
                ]))
        
        elements.append(results_table)
        elements.append(PageBreak())
        
        return elements
    
    def _create_individual_reports(self, results: List[Dict[str, Any]]) -> List:
        """Create individual student reports."""
        elements = []
        
        for i, result in enumerate(results):
            student_info = result.get('student_info', {})
            omr_result = result.get('omr_result')
            
            if not omr_result:
                continue
            
            # Student header
            name = student_info.get('name', 'Unknown')
            roll = student_info.get('roll_number', 'Unknown')
            
            header = Paragraph(f"<b>Student Report - {name} (Roll: {roll})</b>", self.styles['CustomHeading'])
            elements.append(header)
            
            # Score summary
            score_info = f"""
            <b>Score:</b> {omr_result.score}/{omr_result.total} ({omr_result.percentage}%)<br/>
            <b>Grade:</b> {self._calculate_grade(omr_result.percentage)}<br/>
            """
            
            score_para = Paragraph(score_info, self.styles['CustomNormal'])
            elements.append(score_para)
            elements.append(Spacer(1, 10))
            
            # Question-wise analysis
            qa_title = Paragraph("Question-wise Analysis:", self.styles['Normal'])
            elements.append(qa_title)
            
            # Create question analysis table
            qa_data = [['Question', 'Marked Answer', 'Correct Answer', 'Result']]
            
            for q_num in sorted(omr_result.correct_answers.keys(), key=lambda x: int(x)):
                marked = omr_result.marked_answers.get(q_num, '-')
                correct = omr_result.correct_answers.get(q_num, '-')
                status = omr_result.result.get(q_num, 'unknown')
                
                # Color code the result
                if status == 'correct':
                    result_text = '✓ Correct'
                elif status == 'incorrect':
                    result_text = '✗ Incorrect'
                else:
                    result_text = '- Not Attempted'
                
                qa_data.append([q_num, marked, correct, result_text])
            
            qa_table = Table(qa_data, colWidths=[1*inch, 1.5*inch, 1.5*inch, 2*inch])
            qa_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            
            elements.append(qa_table)
            
            # Add page break except for last student
            if i < len(results) - 1:
                elements.append(PageBreak())
            else:
                elements.append(Spacer(1, 20))
        
        return elements
    
    def _calculate_grade(self, percentage: float) -> str:
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
    
    def generate_summary_csv(self, results: List[Dict[str, Any]], output_path: str = "omr_results.csv") -> str:
        """
        Generate CSV summary of results.
        
        Args:
            results: List of student results
            output_path: Output CSV file path
            
        Returns:
            Path to generated CSV file
        """
        try:
            data = []
            
            for result in results:
                student_info = result.get('student_info', {})
                omr_result = result.get('omr_result')
                
                if omr_result:
                    row = {
                        'Name': student_info.get('name', 'Unknown'),
                        'Roll_Number': student_info.get('roll_number', 'Unknown'),
                        'Score': omr_result.score,
                        'Total': omr_result.total,
                        'Percentage': omr_result.percentage,
                        'Grade': self._calculate_grade(omr_result.percentage)
                    }
                    
                    # Add individual question results
                    for q_num in sorted(omr_result.correct_answers.keys(), key=lambda x: int(x)):
                        row[f'Q{q_num}_Marked'] = omr_result.marked_answers.get(q_num, '')
                        row[f'Q{q_num}_Correct'] = omr_result.correct_answers.get(q_num, '')
                        row[f'Q{q_num}_Result'] = omr_result.result.get(q_num, '')
                    
                    data.append(row)
            
            df = pd.DataFrame(data)
            df.to_csv(output_path, index=False)
            
            logger.info(f"CSV report generated: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error generating CSV report: {str(e)}")
            raise
