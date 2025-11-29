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

def choose_field_from_answers(answers):
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        print("⚠️ GEMINI_API_KEY missing — using fallback.")
        return "AI Engineer"

    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)

        model = genai.GenerativeModel("gemini-2.5-flash-lite")
        prompt = build_prompt(answers)

        response = model.generate_content(prompt)
        field = response.text.strip()

        # Validate
        if field in AVAILABLE_FIELDS:
            return field

        for f in AVAILABLE_FIELDS:
            if f.lower() in field.lower():
                return f

        print("⚠️ Unexpected output:", field)
        return "AI Engineer"

    except Exception as e:
        print("Error:", e)
        return "AI Engineer"
