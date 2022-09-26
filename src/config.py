class BaseConfig:

    def __init__(self, ocr_engine: str) -> None:
        self.ocr_engine = ocr_engine

class ImportConfig(BaseConfig):

    def __init__(self, ocr_engine: str, model_type: str = None, lang_hint: str=None) -> None:
        super().__init__(ocr_engine=ocr_engine)
        self.model_type = model_type
        self.lang_hint = lang_hint

class ReimportConfig(BaseConfig):

    def __init__(self, ocr_engine: str) -> None:
        super().__init__(ocr_engine=ocr_engine)

GOOGLE_VISION_PARSER_LINK = ""
GOOGLE_HOCR_PARSER_LINK = ""
NAMSEL_PARSER_LINK = ""

BATCH_PREFIX = "batch"