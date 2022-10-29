import json
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


def test_import_config_serialized():
    credentials = {"fake-token": "fake-token_value"}
    ocr_engine = "google_vision"
    model_type = "weekly-built-in"
    lang_hint = "en"
    images_path = Path("/fake/images/path")
    ocr_output_path = Path("/fake/ocr_output/path")

    import_config = ImportConfig(
        ocr_engine=ocr_engine,
        model_type=model_type,
        lang_hint=lang_hint,
        credentials=credentials,
        img_download_base_dir=images_path,
        ocr_output_base_dir=ocr_output_path,
    )
    config_dict = import_config.to_dict()

    assert config_dict == {
        "ocr_engine": ocr_engine,
        "model_type": model_type,
        "lang_hint": lang_hint,
        "credentials": credentials,
        "img_download_base_dir": str(images_path),
        "ocr_output_base_dir": str(ocr_output_path),
    }
    assert json.dumps(config_dict)


def test_import_config_from_dict():
    credentials = {"fake-token": "fake-token_value"}
    ocr_engine = "google_vision"
    model_type = "weekly-built-in"
    lang_hint = "en"
    images_path = Path("/fake/images/path")
    ocr_output_path = Path("/fake/ocr_output/path")

    config_dict = {
        "ocr_engine": ocr_engine,
        "model_type": model_type,
        "lang_hint": lang_hint,
        "credentials": credentials,
        "img_download_base_dir": str(images_path),
        "ocr_output_base_dir": str(ocr_output_path),
    }

    import_config = ImportConfig.from_dict(config_dict)

    assert import_config.ocr_engine == ocr_engine
    assert import_config.model_type == model_type
    assert import_config.lang_hint == lang_hint
    assert import_config.credentials == credentials
    assert import_config.img_download_base_dir == images_path
    assert import_config.ocr_output_base_dir == ocr_output_path


def test_reimport_config():
    ocr_engine = "google_vision"

    reimport_config = ReimportConfig(ocr_engine=ocr_engine)

    assert reimport_config.ocr_engine == ocr_engine
    assert (
        reimport_config.ocr_output_base_dir
        == Path.home() / ".ocr_pipelines_data" / "ocr_outputs"
    )
