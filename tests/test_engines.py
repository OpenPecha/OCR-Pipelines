import json
import os
from pathlib import Path

import pytest

from ocr_pipelines.engines import GoogleVisionEngine


@pytest.mark.engine
@pytest.mark.skipif(
    bool(os.environ.get("OP_OCR_TEST_ENGINE")) is False,
    reason="only run to intentionally test the engines",
)
def test_google_vision_engine_with_image_path(test_data_path):
    test_image_path = test_data_path / "test_script_image.jpg"
    credentials_path = Path.home() / ".gcloud" / "service_account_key.json"
    credentials = json.loads(credentials_path.read_text())
    google_vision = GoogleVisionEngine(credentials)

    response = google_vision.ocr(test_image_path)
    print(response)

    assert isinstance(response, dict)
