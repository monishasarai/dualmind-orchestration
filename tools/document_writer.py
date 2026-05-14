"""
Document Writer Tool
Generates structured PDF reports using fpdf.
"""

from fpdf import FPDF
import json
import logging
import os
from typing import Dict, Any, List
from datetime import datetime

class DocumentWriter:
    """Tool for generating PDF reports."""

    def __init__(self):
        """Initialize the document writer."""
        self.output_dir = "output"
        self.logger = logging.getLogger(__name__)

        # Create output directory if it doesn't exist
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def create_pdf(self, content: Dict[str, Any], title: str = "Report") -> str:
        """
        Create a PDF document from content.

        Args:
            content (Dict[str, Any]): Content for the PDF
            title (str): PDF title

        Returns:
            str: Path to the generated PDF file
        """
        try:
            pdf = FPDF()
            pdf.add_page()

            # Set up fonts and styles
            pdf.set_font('Arial', 'B', 16)

            # Title
            pdf.cell(0, 10, title, 0, 1, 'C')
            pdf.ln(10)

            # Reset font for content
            pdf.set_font('Arial', '', 12)

            # Add sections based on content structure
            if 'sections' in content:
                for section in content['sections']:
                    self._add_section(pdf, section)

            # Add summary if provided
            if 'summary' in content:
                pdf.ln(5)
                pdf.set_font('Arial', 'B', 14)
                pdf.cell(0, 10, 'Summary', 0, 1)
                pdf.set_font('Arial', '', 12)
                pdf.multi_cell(0, 8, content['summary'])
                pdf.ln(5)

            # Add conclusion if provided
            if 'conclusion' in content:
                pdf.ln(5)
                pdf.set_font('Arial', 'B', 14)
                pdf.cell(0, 10, 'Conclusion', 0, 1)
                pdf.set_font('Arial', '', 12)
                pdf.multi_cell(0, 8, content['conclusion'])
                pdf.ln(5)

            # Add timestamp
            pdf.ln(10)
            pdf.set_font('Arial', 'I', 10)
            pdf.cell(0, 8, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 0, 0, 'R')

            # Save the PDF
            filename = f"report_{title.replace(' ', '_').lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            filepath = os.path.join(self.output_dir, filename)

            pdf.output(filepath)

            return filepath

        except Exception as e:
            self.logger.error(f"Error creating PDF: {e}")
            return ""

    def _add_section(self, pdf: FPDF, section: Dict[str, Any]):
        """Add a section to the PDF."""
        try:
            # Section title
            pdf.set_font('Arial', 'B', 14)
            pdf.cell(0, 10, section.get('title', 'Section'), 0, 1)
            pdf.ln(3)

            # Section content
            pdf.set_font('Arial', '', 12)

            content = section.get('content', '')
            if isinstance(content, list):
                for item in content:
                    if isinstance(item, dict):
                        # Handle structured content
                        for key, value in item.items():
                            pdf.cell(0, 8, f"{key}: {value}", 0, 1)
                    else:
                        pdf.cell(0, 8, str(item), 0, 1)
            else:
                pdf.multi_cell(0, 8, str(content))

            pdf.ln(5)

        except Exception as e:
            self.logger.error(f"Error adding section to PDF: {e}")

    def run(self, content_input: str, title: str = "Report") -> str:
        """
        Main method to run the document writer tool.

        Args:
            content_input (str): JSON string containing content for the PDF
            title (str): PDF title

        Returns:
            str: Path to the generated PDF file or error message
        """
        try:
            # Parse the content input
            try:
                content = json.loads(content_input)
            except json.JSONDecodeError:
                # If JSON parsing fails, create a simple default document with the input as text
                self.logger.warning(f"Invalid JSON input, using text as content. Input was: {content_input[:100]}")
                content = {
                    "sections": [
                        {
                            "title": "Content",
                            "content": content_input if len(content_input) < 500 else content_input[:500] + "..."
                        }
                    ]
                }

            # Ensure content has the expected structure
            if not isinstance(content, dict):
                content = {"sections": [{"title": "Content", "content": str(content)}]}
            
            if "sections" not in content:
                # If no sections, wrap the content
                content = {"sections": [{"title": "Content", "content": str(content)}]}

            filepath = self.create_pdf(content, title)

            if filepath:
                return f"PDF report successfully created: {filepath}"
            else:
                return "Error: Failed to create PDF report"

        except Exception as e:
            self.logger.error(f"Unexpected error in document writer: {e}")
            return f"Error: {str(e)}"


def document_writer_tool(content_input: str, title: str = "Report") -> str:
    """
    Standalone function for document writer tool.

    Args:
        content_input (str): JSON string containing content for the PDF
        title (str): PDF title

    Returns:
        str: Path to the generated PDF file or error message
    """
    writer = DocumentWriter()
    return writer.run(content_input, title)
