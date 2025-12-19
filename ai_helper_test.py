import os
import pytest
import sys
from unittest.mock import patch, MagicMock

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import functions from your module
from ai_helper import (
    build_prompt,
    get_available_fields,
    choose_field_from_answers
)

# ------------------------------------------------------------------
# Tests for build_prompt
# ------------------------------------------------------------------

def test_build_prompt_contains_answers_and_fields():
    answers = {
        "1": {"question": "Do you like AI?", "answer": "Yes"},
        "2": "I enjoy programming"
    }
    fields = ["AI Engineer", "Web Developer"]

    prompt = build_prompt(answers, fields)

    assert "Do you like AI?" in prompt
    assert "Yes" in prompt
    assert "I enjoy programming" in prompt
    assert "AI Engineer, Web Developer" in prompt
    assert "Respond *only* with the field name" in prompt

