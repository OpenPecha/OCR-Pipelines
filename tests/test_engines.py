import json
import os
from pathlib import Path
from unittest import mock

import pytest

from ocr_pipelines.engines import GoogleVisionEngine


def test_load_image_with_image_bytes(test_data_path):
    # arrange
    test_image_path = test_data_path / "test_script_image.jpg"
    image_bytes = test_image_path.read_bytes()

    # action
    loaded_image_bytes = GoogleVisionEngine.load_image_bytes(image_bytes)

    # assert
    assert loaded_image_bytes == image_bytes


def test_google_vision_engine_on_invalid_image_type():
    # arrange
    invalid_image = 123

    # action and assert
    with pytest.raises(TypeError):
        GoogleVisionEngine.load_image_bytes(invalid_image)  # type: ignore


def test_google_vision_engine_image_path_not_found():
    # arrange
    image_path_not_found = Path("fake-path")

    # action assert
    with pytest.raises(FileNotFoundError):
        GoogleVisionEngine.load_image_bytes(image_path_not_found)


@mock.patch(
    "ocr_pipelines.engines.google_vision.AnnotateImageResponse",
    spec=True,
    spec_set=True,
)
@mock.patch("google.cloud.vision.ImageAnnotatorClient", autospec=True, spec_set=True)
@mock.patch(
    "ocr_pipelines.engines.google_vision.Credentials", autospec=True, spec_set=True
)
def test_google_vision_engine(
    mock_credentials,
    mock_client_class,
    mock_response,
    test_data_path,
):
    # arrange
    expected_response = {"test": "test"}
    credentials = {"fake-key": "fake-value"}
    test_image_path = test_data_path / "test_script_image.jpg"
    mock_credentials.from_service_account_info.return_value = "fake-credentials_obj"
    mock_client = mock.MagicMock()
    mock_client.annotate_image.return_value = "response"
    mock_client_class.return_value = mock_client
    mock_response.to_json.return_value = json.dumps(expected_response)

    # action
    google_vision = GoogleVisionEngine(credentials)
    response = google_vision.ocr(test_image_path)

    # assert
    assert isinstance(response, dict)
    assert response == expected_response
    mock_client_class.assert_called_once_with(credentials="fake-credentials_obj")
    mock_credentials.from_service_account_info.assert_called_once_with(credentials)
    mock_response.to_json.assert_called_once_with("response")


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
