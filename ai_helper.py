# AI helper for Gemini API integration
import os
from dotenv import load_dotenv
from DB import get_db_connection

# Load environment variables from .env file
load_dotenv()


def build_prompt(answers, fields):
    lines = []
    for q, v in answers.items():
        if isinstance(v, dict):
            q_text = (v.get('question') or '').strip()
            a_text = (v.get('answer') or '').strip()
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
{', '.join(fields)}

Quiz Answers:
{answers_text}

Instructions:
- Analyze the answers carefully
- Choose one best field
- Respond *only* with the field name

Your recommendation:
"""

def get_available_fields():
    """
    Get list of available career fields from database
    
    Returns:
        List of field names (strings)
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT field_name FROM roadmaps ORDER BY field_name')
        roadmaps = cursor.fetchall()
        conn.close()
        
        if roadmaps:
            return [r['field_name'] for r in roadmaps]
        else:
            # Fallback to default fields if no roadmaps exist
            return [
                "AI Engineer",
                "ML Engineer",
                "Data Scientist",
                "Web Developer",
                "Cybersecurity Analyst",
                "Cloud Engineer",
                "Mobile Developer",
                "Game Developer"
            ]
    except Exception as e:
        print(f"Error fetching roadmaps from database: {e}")
        # Fallback to default fields on error
        return [
            "AI Engineer",
            "ML Engineer",
            "Data Scientist",
            "Web Developer",
            "Cybersecurity Analyst",
            "Cloud Engineer",
            "Mobile Developer",
            "Game Developer"
        ]


def choose_field_from_answers(answers):
    """
    Send quiz answers to Gemini API and get field recommendation
    
    Args:
        answers: Dictionary of question_id -> answer
    
    Returns:
        String with recommended field name
    """
    
    # Get available fields from database (includes newly created roadmaps)
    available_fields = get_available_fields()
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

if __name__ == '__main__':
    # Test the function
    test_answers = {
        "1": "A",
        "2": "B",
        "3": "C"
    }
    result = choose_field_from_answers(test_answers)
    print(f"Recommended field: {result}")
