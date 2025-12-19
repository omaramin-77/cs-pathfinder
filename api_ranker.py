"""
CV Ranker using ChatPDF API for translation and ranking
"""
import pdfplumber
import PyPDF2
from typing import Dict
import logging
import os
import requests
from langdetect import detect
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class APICVRanker:
    """CV Ranker using ChatPDF API"""

    def __init__(self):
        self.api_key = os.getenv("CHATPDF_API_KEY")
        if not self.api_key:
            raise ValueError("CHATPDF_API_KEY not found in environment variables")

    def detect_language(self, text: str) -> str:
        """Detect language of text"""
        try:
            if not text or len(text.strip()) < 10:
                return "en"
            return detect(" ".join(text.split()))
        except Exception:
            return "en"

    def extract_text_from_pdf(self, pdf_path) -> str:
        """Extract text from PDF file"""
        try:
            pdf_path.seek(0)
            with pdfplumber.open(pdf_path) as pdf:
                text = "\n".join(page.extract_text() or "" for page in pdf.pages)
                if text.strip():
                    return text.strip()
        except Exception:
            pass

        try:
            pdf_path.seek(0)
            pdf_reader = PyPDF2.PdfReader(pdf_path)
            text = "\n".join(page.extract_text() or "" for page in pdf_reader.pages)
            if text.strip():
                return text.strip()
        except Exception:
            pass

        return ""
