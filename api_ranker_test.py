import io
import os
import sys
import pytest

# Allow importing from parent directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from api_ranker import APICVRanker
