import json
import os
from pathlib import Path
from unittest import mock

import pytest

from ocr_pipelines.engines import GoogleVisionEngine


@mock.patch("ocr_pipelines.engines.google_vision.AnnotateImageResponse")
@mock.patch("google.cloud.vision.ImageAnnotatorClient")
@mock.patch("ocr_pipelines.engines.google_vision.Credentials")
def test_google_vision_engine(
    mock_credentials,
    mock_image_annotator_client,
    mock_annotate_image_response,
    test_data_path,
):
    # prepare data
    expected_response = {"test": "test"}
    credentials = {"fake-key": "fake-value"}
    test_image_path = test_data_path / "test_script_image.jpg"

    # mock mocksgoogle.cloud.vision dependencies
    mock_credentials.from_service_account_info.return_value = "fake-credentials_obj"
    mock_image_annotator_client_instance = mock_image_annotator_client.return_value
    mock_image_annotator_client_instance.annotate_image.return_value = "response"
    mock_image_annotator_client.return_value = mock_image_annotator_client_instance
    mock_annotate_image_response.to_json.return_value = json.dumps(expected_response)

    # evaluate
    google_vision = GoogleVisionEngine(credentials)
    response = google_vision.ocr(test_image_path)

    # verify
    assert isinstance(response, dict)
    assert response == expected_response
    mock_image_annotator_client.assert_called_once_with(
        credentials="fake-credentials_obj"
    )
    mock_credentials.from_service_account_info.assert_called_once_with(credentials)
    mock_annotate_image_response.to_json.assert_called_once_with("response")


@pytest.mark.engine
@pytest.mark.skipif(
    bool(os.environ.get("OP_OCR_TEST_ENGINE")) is False,
    reason="only run to intentionally test the engines",
)
def test_google_vision_engine_with_google_vision_service(test_data_path):
    test_image_path = test_data_path / "test_script_image.jpg"
    credentials_path = Path.home() / ".gcloud" / "service_account_key.json"
    credentials = json.loads(credentials_path.read_text())
    google_vision = GoogleVisionEngine(credentials)

    response = google_vision.ocr(test_image_path)
    print(response)

    assert isinstance(response, dict)
