from openpecha.formatters.google_ocr import GoogleOCRFormatter

from src.config import BaseConfig, GOOGLE_VISION_PARSER_LINK
from src.exceptions import OCREngineNotSupported


PARSERS_REGISTER = {
    "google_vision": GoogleOCRFormatter,
}
class OCRParser:

    def __init__(self, config:BaseConfig, ocr_output_path:str, opf_dir:str, pecha_id=None, parsers_register=PARSERS_REGISTER) -> None:
        self.config = config
        self.ocr_output_path = ocr_output_path
        self.opf_dir = opf_dir
        self.parsers_register = parsers_register
        self.pecha_id = pecha_id

    def parse(self):
        try:
            formatter_class = self.parsers_register[self.config.ocr_engine]
        except OCREngineNotSupported:
            raise OCREngineNotSupported(
                f'{self.config.ocr_engine} not supported. Please select from {PARSERS_REGISTER.keys()}'
            )
        formatter = formatter_class(output_path=self.opf_dir)
        opf_path = formatter.create_opf(input_path=self.ocr_output_path, pecha_id=self.pecha_id, parser_link=GOOGLE_VISION_PARSER_LINK)
        return opf_path