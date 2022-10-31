import tempfile
from pathlib import Path
from unittest import mock

from ocr_pipelines.config import ImportConfig
from ocr_pipelines.executor import OCRExecutor


@mock.patch("ocr_pipelines.executor.ocr_engine_class_register")
@mock.patch("ocr_pipelines.executor.GoogleVisionEngine", autospec=True)
def test_executor(
    mock_google_vision_engine, mock_ocr_engine_class_register, test_data_path
):

    # mock ocr_engine_class_register and GoogleVisionEngine
    mock_google_vision_engine_instance = mock_google_vision_engine.return_value
    mock_google_vision_engine_instance.ocr.return_value = {}
    mock_google_vision_engine.return_value = mock_google_vision_engine_instance
    mock_ocr_engine_class_register.get.return_value = mock_google_vision_engine

    image_download_dir = Path(test_data_path / "images", "bdrc_work")

    with tempfile.TemporaryDirectory() as tmpdirname:
        ocr_outputs_path = Path(tmpdirname)
        import_config = ImportConfig(
            ocr_engine=str(mock_google_vision_engine),
            model_type="weekly-inbuit",
            ocr_outputs_path=ocr_outputs_path,
        )
        ocr_executor = OCRExecutor(
            config=import_config,
            image_download_dir=image_download_dir,
        )
        ocr_output_path = ocr_executor.run()

        assert isinstance(ocr_output_path, Path)
