from pathlib import Path

DEFAULT_IMAGE_DOWNLOAD_BASE_DIR = Path().home()

DEFAULT_OCR_OUTPUT_BASE_DIR = Path().home()


class BaseConfig:
    def __init__(
        self, ocr_engine: str, ocr_output_base_dir: Path = DEFAULT_OCR_OUTPUT_BASE_DIR
    ) -> None:
        self.ocr_engine = ocr_engine
        self.ocr_output_base_dir = ocr_output_base_dir


class ImportConfig(BaseConfig):
    def __init__(
        self,
        ocr_engine: str,
        ocr_output_base_dir: Path = DEFAULT_OCR_OUTPUT_BASE_DIR,
        img_download_base_dir: Path = DEFAULT_IMAGE_DOWNLOAD_BASE_DIR,
        model_type: str = "",
        lang_hint: str = "",
    ) -> None:
        super().__init__(ocr_engine=ocr_engine, ocr_output_base_dir=ocr_output_base_dir)
        self.model_type = model_type
        self.lang_hint = lang_hint
        self.img_download_base_dir = img_download_base_dir


class ReimportConfig(BaseConfig):
    def __init__(
        self, ocr_engine: str, ocr_output_base_dir: Path = DEFAULT_OCR_OUTPUT_BASE_DIR
    ) -> None:
        super().__init__(ocr_engine=ocr_engine, ocr_output_base_dir=ocr_output_base_dir)


GOOGLE_VISION_PARSER_LINK = ""
GOOGLE_HOCR_PARSER_LINK = ""
NAMSEL_PARSER_LINK = ""

BATCH_PREFIX = "batch"
