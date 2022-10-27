import json
import tempfile
from pathlib import Path

import pytest

from ocr_pipelines.config import ImportConfig
from ocr_pipelines.executor import GoogleVisionEngine, OCRExecutor


class MockGoogleOCREngine:
    def __init__(self, config: ImportConfig, image_download_dir) -> None:
        self.image_download_dir = image_download_dir
        self.model_type = config.model_type
        self.lang_hint = config.lang_hint
        self.ocr_output_base_dir = config.ocr_output_base_dir

    def run(self):
        return Path.home()


ENGINE_REGISTER = {"mock_google_vision": MockGoogleOCREngine}


def test_executor_with_google_vision():
    image_download_dir = Path("./")

    with tempfile.TemporaryDirectory() as tmpdirname:
        ocr_output_base_dir = Path(tmpdirname)
        import_config = ImportConfig(
            ocr_engine="mock_google_vision",
            model_type="weekly-inbuit",
            ocr_output_base_dir=ocr_output_base_dir,
        )
        ocr_executor = OCRExecutor(
            config=import_config,
            image_download_dir=image_download_dir,
            engine_register=ENGINE_REGISTER,
        )
        ocr_output_path = ocr_executor.run()

        assert isinstance(ocr_output_path, Path)


@pytest.mark.skip("Third pary API call")
def test_google_vision_engine_with_image_path(test_data_path):
    test_image_path = test_data_path / "test_script_image.jpg"
    credentials_path = Path.home() / ".gcloud" / "service_account_key.json"
    credentials = json.loads(credentials_path.read_text())
    google_vision_ocr = GoogleVisionEngine(credentials)

    response = google_vision_ocr.extract_text(test_image_path)

    print(response)
    assert response
