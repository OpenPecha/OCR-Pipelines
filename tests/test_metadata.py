from ocr_pipelines.config import ImportConfig
from ocr_pipelines.metadata import Metadata


def test_metadata_to_dict():
    config = ImportConfig(
        ocr_engine="tesseract",
        model_type="htr",
        lang_hint="bo-x-ewts",
        batch="batch",
    )
    metadata = Metadata(
        pipeline_config=config,
        sponsor="BDRC",
        sponsor_consent=True,
    )
    assert metadata.to_dict() == {
        "timestamp": metadata.timestamp,
        "ocr_engine": config.ocr_engine,
        "ocr_model_type": config.model_type,
        "ocr_lang_hint": config.lang_hint,
        "ocr_pipeline_version": config.version,
        "sponsor": metadata.sponsor,
        "sponsor_consent": metadata.sponsor_consent,
        **metadata.kwargs,
    }
