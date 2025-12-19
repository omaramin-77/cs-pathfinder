import os
import pytest
import sys
from unittest.mock import patch, MagicMock

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ai_helper import build_prompt, choose_field_from_answers, get_available_fields

# Test build_prompt function
def test_build_prompt_with_empty_answers():
    """Test building a prompt with empty answers"""
    prompt = build_prompt({}, ["Field1", "Field2"])
    assert "Field1, Field2" in prompt
    assert "No answers provided" in prompt

def test_build_prompt_with_special_chars():
    """Test building a prompt with special characters in answers"""
    answers = {"1": {"question": "What's your experience?", "answer": "I've worked with Python & SQL"}}
    prompt = build_prompt(answers, ["Field1"])
    assert "What's your experience?" in prompt
    assert "I've worked with Python & SQL" in prompt

# Test choose_field_from_answers function
@patch("ai_helper.get_available_fields")
@patch("ai_helper.genai.GenerativeModel")
@patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"})
def test_choose_field_api_success(mock_model, mock_get_fields):
    """Test successful field selection from API"""
    # Setup mocks
    mock_get_fields.return_value = ["AI Engineer", "Web Developer"]
    mock_response = MagicMock()
    mock_response.text = "Web Developer"
    mock_instance = MagicMock()
    mock_instance.generate_content.return_value = mock_response
    mock_model.return_value = mock_instance
    
    # Test
    result = choose_field_from_answers({"1": "I love web development"})
    assert result == "Web Developer"

@patch("ai_helper.get_available_fields")
def test_choose_field_no_api_key(mock_get_fields):
    """Test field selection falls back when no API key"""
    mock_get_fields.return_value = ["AI Engineer", "Web Developer"]
    
    # Test without API key
    with patch.dict(os.environ, {"GEMINI_API_KEY": ""}):
        result = choose_field_from_answers({"1": "Test"})
        assert result in ["AI Engineer", "Web Developer"]

# Test get_available_fields function
@patch("ai_helper.get_db_connection")
def test_get_available_fields_database_error(mock_get_db):
    """Test fallback when database is unavailable"""
    mock_get_db.side_effect = Exception("DB Error")
    fields = get_available_fields()
    assert isinstance(fields, list)
    assert len(fields) > 0  # Should return default fields

# Test error handling in field selection
@patch("ai_helper.get_available_fields")
@patch("ai_helper.genai.GenerativeModel")
@patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"})
def test_choose_field_api_failure(mock_model, mock_get_fields):
    """Test field selection handles API errors gracefully"""
    mock_get_fields.return_value = ["AI Engineer", "Web Developer"]
    mock_model.side_effect = Exception("API Error")
    
    result = choose_field_from_answers({"1": "Test"})
    assert result in ["AI Engineer", "Web Developer"]  # Should return first available field on error

# Integration Tests
# These tests require proper environment setup and may call external services

@pytest.mark.integration
def test_choose_field_real_gemini_call():
    """
    Integration test:
    - Uses real database
    - Uses real Gemini API
    - Verifies returned field is valid
    """
    # Skip if running in CI environment without API key
    if not os.getenv("GEMINI_API_KEY"):
        pytest.skip("GEMINI_API_KEY not set, skipping integration test")

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
