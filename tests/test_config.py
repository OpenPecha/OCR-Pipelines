from src.config import ImportConfig, ReimportConfig


def test_import_config():
    ocr_engine = "google_vision"
    model_type = "weekly-built-in"

    import_config = ImportConfig(ocr_engine='google_vision', model_type='weekly-built-in')

    assert import_config.ocr_engine == ocr_engine
    assert import_config.model_type == model_type
    

def test_reimport_config():
    formatter_type = "namsel_ocr"

    reimport_config = ReimportConfig(formatter_type="namsel_ocr")

    assert reimport_config.formatter_type == formatter_type