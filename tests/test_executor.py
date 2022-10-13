import tempfile

from pathlib import Path

from ocr_pipelines.config import ImportConfig
from ocr_pipelines.executor import OCRExecutor


class MockGoogleOCREngine:

    def __init__(self, images_base_dir: Path, config: ImportConfig, ocr_base_dir: Path) -> None:
        self.images_base_dir = images_base_dir
        self.model_type = config.model_type
        self.lang_hint = config.lang_hint
        self.ocr_base_dir = ocr_base_dir

    def run(self):
        return Path.home()

ENGINE_REGISTER = {
    'mock_google_vision': MockGoogleOCREngine
}


def test_executor_with_google_vision():
    images_base_dir = Path('./')
    import_config = ImportConfig(
        ocr_engine="mock_google_vision",
        model_type="weekly-inbuit"
    )

    with tempfile.TemporaryDirectory() as tmpdirname:
        ocr_base_dir = Path(tmpdirname)
        ocr_executor = OCRExecutor(images_base_dir=images_base_dir, config=import_config, ocr_base_dir=ocr_base_dir, engine_register=ENGINE_REGISTER)
        ocr_output_path = ocr_executor.run()
    

        assert isinstance(ocr_output_path, Path)