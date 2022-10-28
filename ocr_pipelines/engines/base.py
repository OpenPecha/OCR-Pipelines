ocr_engine_class_register = {}


class BaseEngine:
    def __init_subclass__(cls) -> None:
        super().__init_subclass__()
        ocr_engine_class_register[cls.__name__] = cls

    def __init__(self, *args, **kwargs) -> None:
        pass

    def ocr(self, image) -> dict:
        raise NotImplementedError
