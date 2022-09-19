class BaseConfig:
    def __init__(self, formatter_type: str) -> None:
        self.formatter_type = formatter_type

class ImportConfig(BaseConfig):

    def __init__(self, formatter_type: str, ocr_engine: str, model_type: str = None) -> None:
        super().__init__(formatter_type=formatter_type)
        self.ocr_engine = ocr_engine
        self.model_type = model_type