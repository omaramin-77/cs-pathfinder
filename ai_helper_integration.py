import os
import pytest
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ai_helper import choose_field_from_answers, get_available_fields


@pytest.mark.integration
def test_choose_field_real_gemini_call():
    """
    Integration test:
    - Uses real database
    - Uses real Gemini API
    - Verifies returned field is valid
    """
    # Ensure API key exists
    api_key = os.getenv("GEMINI_API_KEY")
    assert api_key is not None, "GEMINI_API_KEY must be set for this test"

    # Simulated student answers (can be 20 MCQs in real use)
    answers = {
        "1": {"question": "Do you enjoy math?", "answer": "Yes"},
        "2": {"question": "Do you like AI models?", "answer": "Very much"},
        "3": {"question": "Preferred work?", "answer": "Research"},
    }

    result = choose_field_from_answers(answers)
    available_fields = get_available_fields()

    # Core validation
    assert isinstance(result, str)
    assert result in available_fields
