from src.config import ImportConfig


def test_import_config():
    ocr_engine = "google_vision"
    model_type = "weekly-built-in"

    import_config = ImportConfig(ocr_engine='google_vision', model_type='weekly-built-in')

    assert import_config.ocr_engine == ocr_engine
    assert import_config.model_type == model_type
    

