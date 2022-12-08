import gzip
import io
import json
import logging
from pathlib import Path

from ocr_pipelines.config import ImportConfig
from ocr_pipelines.engines import register as ocr_engine_class_register
from ocr_pipelines.engines.engine import OcrEngine
from ocr_pipelines.engines.google_vision import GoogleVisionEngine
from ocr_pipelines.exceptions import (
    GoogleVisionCredentialsError,
    OCREngineNotSupported,
    OcrExecutorError,
)


def gzip_str(string_):
    # taken from https://gist.github.com/Garrett-R/dc6f08fc1eab63f94d2cbb89cb61c33d
    out = io.BytesIO()

    with gzip.GzipFile(fileobj=out, mode="w") as fo:
        fo.write(string_.encode())

    bytes_obj = out.getvalue()
    return bytes_obj


class OCRExecutor:
    def __init__(
        self,
        config: ImportConfig,
        image_download_dir: Path,
    ) -> None:
        self.config = config
        self.image_download_dir = image_download_dir
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    def get_ocr_engine(self) -> OcrEngine:
        ocr_engine_class = ocr_engine_class_register.get(self.config.ocr_engine)
        if ocr_engine_class == GoogleVisionEngine:
            ocr_engine = ocr_engine_class(
                self.config.credentials,
                self.config.model_type,
                self.config.lang_hint,
                self.image_download_dir,
                self.config.ocr_outputs_path,
            )
            return ocr_engine
        else:
            raise OCREngineNotSupported(
                f"OCR engine `{self.config.ocr_engine}` not suporrted"
            )

    def run(self):
        ocr_engine = self.get_ocr_engine()
        bdrc_scan_id = self.image_download_dir.name
        img_group_paths = list(self.image_download_dir.iterdir())
        img_group_paths.sort()
        for img_group_path in img_group_paths:
            img_group_id = img_group_path.name
            ocr_output_dir = (
                self.config.ocr_outputs_path
                / bdrc_scan_id
                / f"{bdrc_scan_id}-{img_group_id}"
            )
            ocr_output_dir.mkdir(exist_ok=True, parents=True)
            img_paths = list(img_group_path.iterdir())
            img_paths.sort()
            for img_path in img_paths:
                result_fn = ocr_output_dir / f"{img_path.stem}.json.gz"
                if result_fn.is_file():
                    continue
                try:
                    result = ocr_engine.ocr(img_path)
                except GoogleVisionCredentialsError as e:
                    self.logger.exception(e)
                    raise OcrExecutorError("OCR Executor failed") from e
                except Exception as e:
                    self.logger.error(
                        f"{ocr_engine.__class__.__name__} failed to ocr {result_fn}"
                    )
                    self.logger.exception(e)
                    continue
                result_json = json.dumps(result)
                gzip_result = gzip_str(result_json)
                result_fn.write_bytes(gzip_result)

        return self.config.ocr_outputs_path / bdrc_scan_id
