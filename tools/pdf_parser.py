"""
PDF Parser Tool
Extracts text content from PDF files for analysis.
Useful for parsing research papers, reports, and documents.
"""

import logging
from typing import Dict, Any, Optional
import os

class PDFParserTool:
    """Tool for extracting text from PDF files."""
    
    def __init__(self):
        """Initialize the PDF parser tool."""
        self.logger = logging.getLogger(__name__)
        
        # Try to import PDF libraries
        self.has_pypdf2 = False
        self.has_pdfplumber = False
        
        try:
            import PyPDF2
            self.has_pypdf2 = True
            self.PyPDF2 = PyPDF2
        except ImportError:
            self.logger.warning("PyPDF2 not installed. Install with: pip install PyPDF2")
        
        try:
            import pdfplumber
            self.has_pdfplumber = True
            self.pdfplumber = pdfplumber
        except ImportError:
            self.logger.warning("pdfplumber not installed. Install with: pip install pdfplumber")
    
    def extract_text_pypdf2(self, pdf_path: str) -> Optional[str]:
        """
        Extract text using PyPDF2.
        
        Args:
            pdf_path (str): Path to PDF file
            
        Returns:
            Optional[str]: Extracted text or None
        """
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = self.PyPDF2.PdfReader(file)
                text = ""
                
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text += page.extract_text() + "\n"
                
                return text.strip()
                
        except Exception as e:
            self.logger.error(f"PyPDF2 extraction error: {e}")
            return None
    
    def extract_text_pdfplumber(self, pdf_path: str) -> Optional[str]:
        """
        Extract text using pdfplumber (better for complex layouts).
        
        Args:
            pdf_path (str): Path to PDF file
            
        Returns:
            Optional[str]: Extracted text or None
        """
        try:
            with self.pdfplumber.open(pdf_path) as pdf:
                text = ""
                
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                
                return text.strip()
                
        except Exception as e:
            self.logger.error(f"pdfplumber extraction error: {e}")
            return None
    
    def parse_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """
        Parse PDF and extract metadata and text.
        
        Args:
            pdf_path (str): Path to PDF file
            
        Returns:
            Dict: Parsed PDF information
        """
        if not os.path.exists(pdf_path):
            return {
                'success': False,
                'error': f'PDF file not found: {pdf_path}',
                'text': '',
                'metadata': {}
            }
        
        if not self.has_pypdf2 and not self.has_pdfplumber:
            return {
                'success': False,
                'error': 'No PDF parsing library available. Install PyPDF2 or pdfplumber.',
                'text': '',
                'metadata': {}
            }
        
        # Try pdfplumber first (better quality), fall back to PyPDF2
        text = None
        if self.has_pdfplumber:
            self.logger.info(f"Parsing PDF with pdfplumber: {pdf_path}")
            text = self.extract_text_pdfplumber(pdf_path)
        
        if text is None and self.has_pypdf2:
            self.logger.info(f"Parsing PDF with PyPDF2: {pdf_path}")
            text = self.extract_text_pypdf2(pdf_path)
        
        if text is None:
            return {
                'success': False,
                'error': 'Failed to extract text from PDF',
                'text': '',
                'metadata': {}
            }
        
        # Get metadata
        metadata = {
            'filename': os.path.basename(pdf_path),
            'file_size': os.path.getsize(pdf_path),
            'text_length': len(text),
            'word_count': len(text.split())
        }
        
        return {
            'success': True,
            'text': text,
            'metadata': metadata,
            'error': None
        }
    
    def format_result(self, result: Dict[str, Any], max_preview: int = 1000) -> str:
        """
        Format PDF parsing result into readable string.
        
        Args:
            result (Dict): Parsing result
            max_preview (int): Maximum characters to preview
            
        Returns:
            str: Formatted result
        """
        if not result['success']:
            return f"❌ **PDF Parsing Error**: {result['error']}"
        
        metadata = result['metadata']
        text = result['text']
        
        output = "## 📄 PDF Parsing Results\n\n"
        output += f"**File**: {metadata['filename']}\n"
        output += f"**Size**: {metadata['file_size']:,} bytes\n"
        output += f"**Text Length**: {metadata['text_length']:,} characters\n"
        output += f"**Word Count**: {metadata['word_count']:,} words\n\n"
        
        output += "### 📖 Text Preview (first 1000 characters):\n\n"
        preview = text[:max_preview]
        if len(text) > max_preview:
            preview += "...\n\n[Text truncated. Full text extracted and available for analysis.]"
        
        output += preview + "\n"
        
        return output
    
    def run(self, pdf_path: str) -> str:
        """
        Main method to run the PDF parser tool.
        
        Args:
            pdf_path (str): Path to PDF file
            
        Returns:
            str: Formatted parsing results
        """
        result = self.parse_pdf(pdf_path)
        return self.format_result(result)


def pdf_parser_tool(pdf_path: str) -> str:
    """
    Standalone function for PDF parser tool.
    
    Args:
        pdf_path (str): Path to PDF file
        
    Returns:
        str: Formatted parsing results
    """
    tool = PDFParserTool()
    return tool.run(pdf_path)
