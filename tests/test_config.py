import json
import tempfile
from pathlib import Path

from ocr_pipelines.config import ImportConfig, ReimportConfig, get_batch_id


def test_get_batch_id():
    batch_id = get_batch_id()

    assert isinstance(batch_id, str)
    assert batch_id.startswith("batch-")
    assert len(batch_id) == 10


def test_import_config():
    ocr_engine = "google_vision"
    model_type = "weekly-built-in"
    lang_hint = "bo"
    credentials = {"fake-token": "fake-token_value"}
    images_path = Path("/fake/images/path")
    ocr_output_path = Path("/fake/ocr_output/path")

    import_config = ImportConfig(
        ocr_engine=ocr_engine,
        model_type=model_type,
        lang_hint=lang_hint,
        credentials=credentials,
        images_path=images_path,
        ocr_outputs_path=ocr_output_path,
    )

    assert import_config.ocr_engine == ocr_engine
    assert import_config.model_type == model_type
    assert import_config.lang_hint == lang_hint
    assert import_config.credentials == credentials
    assert import_config.images_path == images_path
    assert import_config.ocr_outputs_path == ocr_output_path


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
        images_path=images_path,
        ocr_outputs_path=ocr_output_path,
    )
    config_dict = import_config.to_dict()

    assert config_dict == {
        "ocr_engine": ocr_engine,
        "model_type": model_type,
        "lang_hint": lang_hint,
        "credentials": credentials,
        "images_path": str(images_path),
        "ocr_outputs_path": str(ocr_output_path),
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
        "images_path": str(images_path),
        "ocr_outputs_path": str(ocr_output_path),
    }

    import_config = ImportConfig.from_dict(config_dict)

    assert import_config.ocr_engine == ocr_engine
    assert import_config.model_type == model_type
    assert import_config.lang_hint == lang_hint
    assert import_config.credentials == credentials
    assert import_config.images_path == images_path
    assert import_config.ocr_outputs_path == ocr_output_path


def test_import_config_creates_paths():
    with tempfile.TemporaryDirectory() as tmpdir:
        # arrange
        ocr_engine = "google_vision"
        images_path = Path(tmpdir) / "images"
        ocr_outputs_path = Path(tmpdir) / "ocr_outputs"

        # act
        import_config = ImportConfig(
            ocr_engine=ocr_engine,
            images_path=images_path,
            ocr_outputs_path=ocr_outputs_path,
        )
        import_config.create_paths()

        # assert
        assert images_path.is_dir()
        assert ocr_outputs_path.is_dir()
        assert import_config.images_path.is_dir()
        assert import_config.ocr_outputs_path.is_dir()


def test_reimport_config():
    ocr_engine = "google_vision"

    reimport_config = ReimportConfig(ocr_engine=ocr_engine)

    assert reimport_config.ocr_engine == ocr_engine
    assert (
        reimport_config.ocr_outputs_path
        == Path.home() / ".ocr_pipelines_data" / "ocr_outputs"
    )
