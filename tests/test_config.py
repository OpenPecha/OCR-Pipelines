from pathlib import Path

from ocr_pipelines.config import ImportConfig, ReimportConfig


def test_import_config():
    ocr_engine = "google_vision"
    model_type = "weekly-built-in"

    import_config = ImportConfig(ocr_engine=ocr_engine, model_type=model_type)

    assert import_config.ocr_engine == ocr_engine
    assert import_config.model_type == model_type
    assert import_config.img_download_base_dir.is_dir()
    assert import_config.ocr_output_base_dir.is_dir()
    assert (
        import_config.img_download_base_dir
        == Path().home() / ".ocr_pipelines_data" / "images"
    )
    assert (
        import_config.ocr_output_base_dir
        == Path().home() / ".ocr_pipelines_data" / "ocr_outputs"
    )


def test_reimport_config():
    ocr_engine = "google_vision"

    reimport_config = ReimportConfig(ocr_engine=ocr_engine)

    assert reimport_config.ocr_engine == ocr_engine
    assert (
        reimport_config.ocr_output_base_dir
        == Path.home() / ".ocr_pipelines_data" / "ocr_outputs"
    )
