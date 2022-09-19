from openpecha.formatters.google_ocr import GoogleOCRFormatter
from openpecha.core.ids import get_initial_pecha_id
from src.config import BaseConfig

class OCRParser:

    def __init__(self, config:BaseConfig, ocr_output_path:str, opf_dir:str, pecha_id=None) -> None:
        self.config = config
        self.ocr_output_path = ocr_output_path
        self.opf_dir = opf_dir
        if pecha_id:
            self.pecha_id = pecha_id
        else:
            self.pecha_id = get_initial_pecha_id()

    def parse(self):
        opf_path = None
        if self.config.formatter_type == "google_vision":
            formatter = GoogleOCRFormatter(output_path=self.opf_dir)
            opf_path = formatter.create_opf(self.ocr_output_path, self.pecha_id)
        return opf_path