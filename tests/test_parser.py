import tempfile
from pathlib import Path

from openpecha.core.pecha import OpenPechaFS

from ocr_pipelines.config import ImportConfig, ReimportConfig
from ocr_pipelines.parser import OCRParser


class MockOCRFormatter:
    def __init__(self, *args, **kwargs) -> None:
        pass

    def create_opf(self, *args, **kwargs):
        return OpenPechaFS(path=Path("/tmp"))


class MockDataProvider:
    def __init__(self, bdrc_scan_id, ocr_import_info, ocr_disk_path=None, mode="local"):
        # ocr_base_path should be the output/ folder in the case of BDRC OCR files
        self.ocr_import_info = ocr_import_info
        self.ocr_disk_path = ocr_disk_path
        self.bdrc_scan_id = bdrc_scan_id
        self.mode = mode


def test_ocr_parser_with_import_config():
    config = ImportConfig(ocr_engine="mock_ocr")
    parsers_register = {"mock_ocr": MockOCRFormatter}
    data_provider_register = {"mock_ocr": MockDataProvider}

    with tempfile.TemporaryDirectory() as tmpdirname:
        ocr_output_path = Path(tmpdirname) / "W123456"
        parser = OCRParser(
            config=config,
            ocr_output_path=ocr_output_path,
            opf_dir="",
            pecha_id=None,
            parsers_register=parsers_register,
            data_provider_register=data_provider_register,
        )
        pecha = parser.parse()

        assert isinstance(pecha, OpenPechaFS)


def test_ocr_parser_with_reimport_config():
    config = ReimportConfig(ocr_engine="mock_ocr")
    parsers_register = {"mock_ocr": MockOCRFormatter}
    data_provider_register = {"mock_ocr": MockDataProvider}

    with tempfile.TemporaryDirectory() as tmpdirname:
        ocr_output_path = Path(tmpdirname) / "W123456"
        parser = OCRParser(
            config=config,
            ocr_output_path=ocr_output_path,
            opf_dir="",
            pecha_id=None,
            parsers_register=parsers_register,
            data_provider_register=data_provider_register,
        )
        pecha = parser.parse()

        assert isinstance(pecha, OpenPechaFS)
