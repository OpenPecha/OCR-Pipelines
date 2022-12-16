import uuid
from pathlib import Path
from typing import Optional, Union

from ocr_pipelines import __version__ as ocr_pipelines_version

# setup paths
DATA_PATH = Path.home() / ".ocr_pipelines_data"

IMAGES_PATH = DATA_PATH / "images"
OCR_OUTPUTS_PATH = DATA_PATH / "ocr_outputs"

# Constants
GOOGLE_VISION_PARSER_LINK = ""
GOOGLE_HOCR_PARSER_LINK = ""
NAMSEL_PARSER_LINK = ""
BATCH_PREFIX = "batch"

# types
Credentials = Union[dict, str]


def get_batch_id() -> str:
    return f"batch-{uuid.uuid4().hex[:4]}"


class ImportConfig:
    def __init__(
        self,
        ocr_engine: str,
        *,
        model_type: str = "",
        lang_hint: str = "",
        credentials: Optional[Credentials] = None,
        images_path: Path = IMAGES_PATH,
        ocr_outputs_path: Path = OCR_OUTPUTS_PATH,
    ) -> None:
        self.ocr_engine = ocr_engine
        self.model_type = model_type
        self.lang_hint = lang_hint
        self.credentials = credentials
        self.images_path = Path(images_path)
        self.ocr_outputs_path = Path(ocr_outputs_path)
        self.version = ocr_pipelines_version

    def create_paths(self):
        self.images_path.mkdir(parents=True, exist_ok=True)
        self.ocr_outputs_path.mkdir(parents=True, exist_ok=True)

    @classmethod
    def from_dict(cls, config_dict: dict) -> "ImportConfig":
        """Deserialize the config from a dictionary."""
        return cls(**config_dict)

    def to_dict(self):
        """Serialize the config to a dictionary which is JSON serializable."""
        return {
            "ocr_engine": self.ocr_engine,
            "model_type": self.model_type,
            "lang_hint": self.lang_hint,
            "credentials": self.credentials,
            "images_path": str(self.images_path),
            "ocr_outputs_path": str(self.ocr_outputs_path),
        }


class ReimportConfig:
    def __init__(
        self, ocr_engine: str, ocr_outputs_path: Path = OCR_OUTPUTS_PATH
    ) -> None:
        self.ocr_engine = ocr_engine
        self.ocr_outputs_path = ocr_outputs_path
