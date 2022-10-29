from abc import ABC, abstractmethod
from pathlib import Path
from typing import Union

ImagePath = Union[str, Path]
ImageBytes = bytes
ImageType = Union[ImagePath, ImageBytes]


register = {}


class OcrEngine(ABC):
    def __init_subclass__(cls) -> None:
        super().__init_subclass__()
        register[cls.__name__] = cls

    def __init__(self, *args, **kwargs) -> None:
        pass

    @abstractmethod
    def ocr(self, image: ImageType) -> dict:
        raise NotImplementedError
