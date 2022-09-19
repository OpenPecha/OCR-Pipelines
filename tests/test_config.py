from src.config import BaseConfig, ImportConfig

def test_base_config():
    formatter_type = "google_vision"

    base_config = BaseConfig(formatter_type=formatter_type)

    assert base_config.formatter_type == formatter_type

def test_import_config():
    ocr_engine = "google_vision"
    formatter_type = "google_vision"
    model_type = "weekly-built-in"

    import_config = ImportConfig(formatter_type=formatter_type, ocr_engine=ocr_engine, model_type=model_type)

    assert import_config.ocr_engine == ocr_engine
    assert import_config.model_type == model_type
    assert import_config.formatter_type == formatter_type