from src.config import BaseConfig, ImportConfig, ReimportConfig

def test_base_config():
    name = "import_config"

    base_config = BaseConfig(name='import_config')

    assert base_config.name == name

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