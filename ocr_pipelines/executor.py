import gzip
import io
import json
from pathlib import Path

from ocr_pipelines.config import ImportConfig
from ocr_pipelines.engines import BaseEngine, ocr_engine_class_register
from ocr_pipelines.engines.google_vision import GoogleVisionEngine
from ocr_pipelines.exceptions import OCREngineNotSupported


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

    def get_ocr_engine(self) -> BaseEngine:
        ocr_engine_class = ocr_engine_class_register.get(self.config.ocr_engine)
        if ocr_engine_class == GoogleVisionEngine:
            ocr_engine = ocr_engine_class(
                self.config.credentials,
                self.config.model_type,
                self.config.lang_hint,
                self.image_download_dir,
                self.config.ocr_output_base_dir,
            )
            return ocr_engine
        else:
            raise OCREngineNotSupported(
                f"OCR engine `{self.config.ocr_engine}` not suporrted"
            )

    def run(self):
        ocr_engine = self.get_ocr_engine()
        print("==========", __file__, ocr_engine)

        bdrc_scan_id = self.image_download_dir.name
        img_group_paths = list(self.image_download_dir.iterdir())
        img_group_paths.sort()
        for img_group_path in img_group_paths:
            img_group_id = img_group_path.name
            ocr_output_dir = (
                self.config.ocr_output_base_dir
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
                except Exception:
                    print(f"Google OCR issue: {result_fn}")
                    continue
                result_json = json.dumps(result)
                gzip_result = gzip_str(result_json)
                result_fn.write_bytes(gzip_result)

        return self.config.ocr_output_base_dir / bdrc_scan_id
