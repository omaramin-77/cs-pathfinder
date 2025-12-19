from ai_helper import choose_field_from_answers

def test_choose_field_fallback():
    sample_answers = {
        "1": {"question": "Do you enjoy building UIs?", "answer": "Yes"},
        "2": {"question": "Do you like working with data?", "answer": "Sometimes"},
        "3": {"question": "Do you enjoy backend work?", "answer": "No"}
    }

    result = choose_field_from_answers(sample_answers)

    assert result == "AI Engineer"
