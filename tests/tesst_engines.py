import json
from pathlib import Path

import pytest

from ocr_pipelines.engines import GoogleVisionEngine


@pytest.mark.skip("Third pary API call")
def test_google_vision_engine_with_image_path(test_data_path):
    test_image_path = test_data_path / "test_script_image.jpg"
    credentials_path = Path.home() / ".gcloud" / "service_account_key.json"
    credentials = json.loads(credentials_path.read_text())
    google_vision = GoogleVisionEngine(credentials)

    response = google_vision.ocr(test_image_path)

    print(response)
    assert response
