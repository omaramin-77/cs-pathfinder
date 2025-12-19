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
