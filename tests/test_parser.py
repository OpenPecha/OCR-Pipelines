from pathlib import Path

import pytest
from openpecha.core.pecha import OpenPechaFS

from ocr_pipelines.config import ImportConfig
from ocr_pipelines.metadata import Metadata
from ocr_pipelines.parser import OCRParser


class MockOCRFormatter:
    def __init__(self, *args, **kwargs) -> None:
        for key, value in kwargs.items():
            setattr(self, key, value)

    def create_opf(self, *args, **kwargs):
        pecha_path = self.output_path / "pecha"  # type: ignore
        return OpenPechaFS(path=pecha_path)


class MockDataProvider:
    def __init__(self, bdrc_scan_id, ocr_import_info, ocr_disk_path=None, mode="local"):
        # ocr_base_path should be the output/ folder in the case of BDRC OCR files
        self.ocr_import_info = ocr_import_info
        self.ocr_disk_path = ocr_disk_path
        self.bdrc_scan_id = bdrc_scan_id
        self.mode = mode


def test_ocr_parser_get_ocr_import_info():
    # arrange
    config = ImportConfig(
        ocr_engine="test_engine",
        model_type="default",
        lang_hint="bo",
    )
    metadata = Metadata(
        pipeline_config=config,
        sponsor="sponsor",
        sponsor_consent=True,
        batch_id="batch_id",
    )
    parser = OCRParser(
        config=config,
        ocr_output_path=Path("/W00001"),
        output_path=Path("/output"),
        metadata=metadata,
    )

    # act
    ocr_import_info = parser.get_ocr_import_info()

    # assert
    assert ocr_import_info == {
        "bdrc_scan_id": "W00001",
        "source": "bdrc",
        "imported_at": metadata.timestamp,
        "ocr_info": {
            "engine": metadata.pipeline_config.ocr_engine,
            "model_type": metadata.pipeline_config.model_type,
            "language_hint": metadata.pipeline_config.lang_hint,
        },
        "batch_id": metadata.batch_id,
        "software_id": f"ocr-pipelines@v{metadata.pipeline_config.version}",
        "expected_default_language": "",
        "sponsor": {
            "name": "sponsor",
            "consent": True,
        },
    }


@pytest.fixture(scope="module")
def config_and_metadata():
    config = ImportConfig(
        ocr_engine="test_engine",
        model_type="default",
        lang_hint="bo",
    )
    metadata = Metadata(
        pipeline_config=config,
        sponsor="sponsor",
        sponsor_consent=True,
        batch_id="batch_id",
    )
    return config, metadata


def test_ocr_parser_with_import_config(tmp_path, config_and_metadata):
    # arrange
    config, metadata = config_and_metadata
    parsers_register = {config.ocr_engine: MockOCRFormatter}
    data_provider_register = {config.ocr_engine: MockDataProvider}
    ocr_output_path = Path(tmp_path) / "W123456"
    parser = OCRParser(
        config=config,
        metadata=metadata,
        ocr_output_path=ocr_output_path,
        output_path=tmp_path,
        parsers_register=parsers_register,
        data_provider_register=data_provider_register,
    )

    # act
    pecha = parser.parse()

    # assert
    assert isinstance(pecha, OpenPechaFS)
