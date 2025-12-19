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

    def upload_pdf_to_chatpdf(self, pdf_path) -> str:
        """Upload PDF to ChatPDF and return source ID"""
        try:
            filename = getattr(pdf_path, 'filename', 'uploaded_cv.pdf')
            pdf_path.seek(0)
            files = {"file": (filename, pdf_path, "application/pdf")}
            response = requests.post(
                "https://api.chatpdf.com/v1/sources/add-file",
                headers={"x-api-key": self.api_key},
                files=files,
                timeout=120,
            )
                
            if response.status_code == 200:
                source_id = response.json().get("sourceId")
                logger.info(f"📤 PDF uploaded to ChatPDF with ID: {source_id}")
                return source_id
            else:
                logger.error(
                    f"ChatPDF upload failed: {response.status_code} - {response.text}"
                )
                return None
        except Exception as e:
            logger.error(f"Error uploading PDF to ChatPDF: {e}")
            return None  

    def chat_with_chatpdf(self, source_id: str, message: str) -> str:
        """Send a message to ChatPDF and get response"""
        try:
            headers = {"x-api-key": self.api_key, "Content-Type": "application/json"}

            payload = {
                "sourceId": source_id,
                "messages": [{"role": "user", "content": message}],
            }

            response = requests.post(
                "https://api.chatpdf.com/v1/chats/message",
                headers=headers,
                json=payload,
                timeout=120,
            )

            if response.status_code == 200:
                content = response.json().get("content", "").strip()
                return content
            else:
                logger.error(
                    f"ChatPDF chat failed: {response.status_code} - {response.text}"
                )
                return None
          
        except Exception as e:
            logger.error(f"Error during ChatPDF chat: {e}")
            return None

    def translate_with_chatpdf(self, source_id: str) -> str:
        """Translate CV to English using ChatPDF"""
        prompt = """Translate this entire CV/resume to professional English. Follow these rules:

1. Translate ALL text including personal information, education, experience, skills, certifications, languages, and projects.
2. Keep unchanged: email addresses, phone numbers, URLs, dates, and numbers.
3. Format as a structured CV with clear sections.
4. Use professional English terminology.

Provide the complete translated CV now."""
        return self.chat_with_chatpdf(source_id, prompt)
    
    def rank_with_chatpdf(self, source_id: str, job_description: str) -> str:
        """Rank CV against job description using ChatPDF"""
        prompt = f"""You are an expert HR recruiter. Analyze the uploaded CV against this job description and provide a detailed assessment.

Job Description:
{job_description[:3000]}

Analyze the CV and respond with ONLY valid JSON in this exact format:

{{
    "matching_analysis": "Detailed analysis of how the candidate matches the job requirements (200-300 characters)",
    "description": "Brief summary of candidate's profile (150-200 characters)",
    "score": 85,
    "recommendation": "Your hiring recommendation (150-200 characters)"
}}

Important:
- Score should be 0-100 based on job fit
- Be specific about matching skills and experience
- Mention any gaps or concerns
- Provide actionable recommendation

Respond with ONLY the JSON, no additional text."""
        return self.chat_with_chatpdf(source_id, prompt)

    def cleanup_chatpdf(self, source_id: str):
        """Delete uploaded PDF from ChatPDF"""
        try:
            requests.post(
                "https://api.chatpdf.com/v1/sources/delete",
                headers={"x-api-key": self.api_key},
                json={"sources": [source_id]},
                timeout=30,
            )
        except Exception:
            pass
