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

def build_prompt(answers):
    lines = []
    for q, v in answers.items():
        if isinstance(v, dict):
            q_text = v.get('question', '').strip()
            a_text = v.get('answer', '').strip()
            if q_text:
                lines.append(f"Question {q}: {q_text}\nAnswer: {a_text}")
            else:
                lines.append(f"Question {q}: Answer: {a_text}")
        else:
            lines.append(f"Question {q}: {v}")

    answers_text = "\n\n".join(lines)

    return f"""
You are a career counselor for computer science students.

Based on the following quiz answers, recommend EXACTLY ONE career field from this list:
{', '.join(AVAILABLE_FIELDS)}

Quiz Answers:
{answers_text}

Instructions:
- Analyze the answers carefully
- Choose one best field
- Respond *only* with the field name

Your recommendation:
"""
