from pathlib import Path

import pytest


@pytest.fixture
def test_data_path():
    return Path(__file__).parent / "data"
