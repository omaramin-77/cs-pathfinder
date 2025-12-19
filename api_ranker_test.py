import io
import os
import sys
import pytest

# Allow importing from parent directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from api_ranker import APICVRanker


@pytest.fixture
def ranker(monkeypatch):
    """
    Create APICVRanker with mocked API key
    """
    monkeypatch.setenv("CHATPDF_API_KEY", "fake_api_key")
    return APICVRanker()


def test_detect_language_english(ranker):
    text = "This is a simple English sentence used for testing."
    lang = ranker.detect_language(text)
    assert lang == "en"


def test_detect_language_short_text_defaults_to_en(ranker):
    text = "Hi"
    lang = ranker.detect_language(text)
    assert lang == "en"


def test_parse_valid_json_response(ranker):
    response = """
    {
        "matching_analysis": "Strong Python and backend experience.",
        "description": "Backend developer with 3 years experience.",
        "score": 85,
        "recommendation": "Highly recommended for interview."
    }
    """
    result = ranker.parse_ranking_response(response)

    assert result["overall_score"] == 85
    assert "Python" in result["matching_analysis"]


def test_parse_invalid_json_response(ranker):
    response = "This is not JSON at all"
    result = ranker.parse_ranking_response(response)

    assert result["overall_score"] == 50
    assert "Manual review" in result["recommendation"]
