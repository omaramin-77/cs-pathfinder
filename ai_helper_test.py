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