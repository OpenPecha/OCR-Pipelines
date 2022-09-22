import tempfile

from pathlib import Path

from src.config import ImportConfig
from src.executor import OCRExecutor


class MockGoogleOCREngine:

    def __init__(self) -> None:
        pass

    def run():
        return Path.home()

ENGINE_REGISTER = {
    'mock_google_ocr_engine': MockGoogleOCREngine
}


def test_executor_with_google_vision():
    images_base_dir = Path('./')
    import_config = ImportConfig(
        ocr_engine="google_vision",
        model_type="weekly-inbuit"
    )

    with tempfile.TemporaryDirectory() as tmpdirname:
        ocr_base_dir = Path(tmpdirname)
        ocr_executor = OCRExecutor(images_base_dir=images_base_dir, config=import_config, ocr_base_dir=ocr_base_dir)
        ocr_output_path = ocr_executor.run()
    

        assert isinstance(ocr_output_path, Path)