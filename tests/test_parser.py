from pathlib import Path

from src.config import ReimportConfig, ImportConfig
from src.parser import OCRParser

class MockOCRFormatter:

    def __init__(self, *args, **kwargs) -> None:
        pass

    def create_opf(self, *args, **kwargs):
        return Path.home()
        

def test_ocr_parser_with_import_config():
    config = ImportConfig(ocr_engine="mock_ocr")
    parsers_register = {
        'mock_ocr': MockOCRFormatter
    }

    parser = OCRParser(config=config, ocr_output_path=None, opf_dir=None, pecha_id=None, parsers_register=parsers_register)
    pecha_path = parser.parse()

    assert isinstance(pecha_path, Path)

def test_ocr_parser_with_reimport_config():
    config = ReimportConfig(ocr_engine="mock_ocr")
    parsers_register = {
        'mock_ocr': MockOCRFormatter
    }

    parser = OCRParser(config=config, ocr_output_path=None, opf_dir=None, pecha_id=None, parsers_register=parsers_register)
    pecha_path = parser.parse()

    assert isinstance(pecha_path, Path)