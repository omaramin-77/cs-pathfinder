# AI helper for Gemini API integration
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def choose_field_from_answers(answers):
    """
    Send quiz answers to Gemini API and get field recommendation
    
    Args:
        answers: Dictionary of question_id -> answer
    
    Returns:
        String with recommended field name
    """
    
    # Available CS career fields
    available_fields = [
        "AI Engineer",
        "ML Engineer",
        "Data Scientist",
        "Web Developer",
        "Cybersecurity Analyst",
        "Cloud Engineer",
        "Mobile Developer",
        "Game Developer"
    ]
