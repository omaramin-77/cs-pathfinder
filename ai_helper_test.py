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


# ------------------------------------------------------------------
# Tests for get_available_fields
# ------------------------------------------------------------------

@patch("ai_helper.get_db_connection")
def test_get_available_fields_from_database(mock_get_db):
    # Mock DB cursor and connection
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = [
        {"field_name": "AI Engineer"},
        {"field_name": "Data Scientist"}
    ]

    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_get_db.return_value = mock_conn

    fields = get_available_fields()

    assert fields == ["AI Engineer", "Data Scientist"]


@patch("ai_helper.get_db_connection", side_effect=Exception("DB error"))
def test_get_available_fields_fallback_on_error(mock_get_db):
    fields = get_available_fields()

    assert "AI Engineer" in fields
    assert len(fields) > 0


# ------------------------------------------------------------------
# Tests for choose_field_from_answers
# ------------------------------------------------------------------

def test_choose_field_without_api_key(monkeypatch):
    # Remove API key if it exists
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    answers = {"1": "A", "2": "B"}
    result = choose_field_from_answers(answers)

    assert result == "AI Engineer"


@patch("ai_helper.get_available_fields")
@patch("ai_helper.os.getenv")
@patch("ai_helper.genai.GenerativeModel")
def test_choose_field_exact_match(
    mock_model,
    mock_getenv,
    mock_get_fields
):
    mock_getenv.return_value = "fake-api-key"
    mock_get_fields.return_value = ["AI Engineer", "Web Developer"]

    mock_response = MagicMock()
    mock_response.text = "Web Developer"

    mock_instance = MagicMock()
    mock_instance.generate_content.return_value = mock_response
    mock_model.return_value = mock_instance

    answers = {"1": "A", "2": "B"}
    result = choose_field_from_answers(answers)

    assert result == "Web Developer"
