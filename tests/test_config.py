from ocr_pipelines.config import ReimportConfig, ImportConfig

def test_base_config():
    ocr_engine = "google_vision"

    reimport_config = ReimportConfig(ocr_engine=ocr_engine)

    assert reimport_config.ocr_engine == ocr_engine

def test_import_config():
    ocr_engine = "google_vision"
    model_type = "weekly-built-in"

    import_config = ImportConfig(ocr_engine=ocr_engine, model_type=model_type)

    assert import_config.ocr_engine == ocr_engine
    assert import_config.model_type == model_type