from pathlib import Path

# setup paths
DATA_PATH = Path.home() / ".ocr_pipelines_data"

IMAGES_PATH = DATA_PATH / "images"
OCR_OUTPUTS_PATH = DATA_PATH / "ocr_outputs"

# Constants
GOOGLE_VISION_PARSER_LINK = ""
GOOGLE_HOCR_PARSER_LINK = ""
NAMSEL_PARSER_LINK = ""
BATCH_PREFIX = "batch"


class BaseConfig:
    pass


class ImportConfig(BaseConfig):
    def __init__(
        self,
        ocr_engine: str,
        model_type: str = "",
        lang_hint: str = "",
        img_download_base_dir: Path = IMAGES_PATH,
        ocr_output_base_dir: Path = OCR_OUTPUTS_PATH,
    ) -> None:
        self.ocr_engine = ocr_engine
        self.model_type = model_type
        self.lang_hint = lang_hint
        self.img_download_base_dir = img_download_base_dir
        self.ocr_output_base_dir = ocr_output_base_dir


class ReimportConfig(BaseConfig):
    def __init__(
        self, ocr_engine: str, ocr_output_base_dir: Path = OCR_OUTPUTS_PATH
    ) -> None:
        self.ocr_engine = ocr_engine
        self.ocr_output_base_dir = ocr_output_base_dir
