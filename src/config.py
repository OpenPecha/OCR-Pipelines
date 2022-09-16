class BaseConfig:

    def __init__(self, name:str) -> None:
        self.name = name
class ImportConfig(BaseConfig):

    def __init__(self, ocr_engine: str, model_type: str = None) -> None:
        self.ocr_engine = ocr_engine
        self.model_type = model_type
        


class ReimportConfig(BaseConfig):
    
    def __init__(self, formatter_type: str) -> None:
        self.formatter_type = formatter_type
    