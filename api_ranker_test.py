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
