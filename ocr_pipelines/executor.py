import gzip
import io
import json
from pathlib import Path
from typing import Union

from google.cloud import vision
from google.cloud.vision import AnnotateImageResponse
from google.oauth2.service_account import Credentials

from ocr_pipelines.config import ImportConfig

ImagePath = Union[str, Path]
ImageBytes = bytes
Image = Union[ImagePath, ImageBytes]


def gzip_str(string_):
    # taken from https://gist.github.com/Garrett-R/dc6f08fc1eab63f94d2cbb89cb61c33d
    out = io.BytesIO()

    with gzip.GzipFile(fileobj=out, mode="w") as fo:
        fo.write(string_.encode())

    bytes_obj = out.getvalue()
    return bytes_obj


class GoogleVisionEngine:
    # TODO: remove dirs

    def __init__(
        self,
        credentials: dict,
        model_type: str = None,
        lang_hint: str = None,
        image_download_dir: Path = Path.home(),
        ocr_output_base_dir: Path = Path.home(),
    ) -> None:
        self.model_type = model_type
        self.lang_hint = lang_hint
        self.image_download_dir = image_download_dir
        self.ocr_output_base_dir = ocr_output_base_dir

        self.credentials = Credentials.from_service_account_info(credentials)
        self.vision_client = vision.ImageAnnotatorClient(credentials=self.credentials)

    def extract_text(self, image: Image) -> dict:
        """Run OCR on a single image.

        Args:
            image: file_path or image bytes
        Returns:
            response: ocr response in dict
        """
        if isinstance(image, (str, Path)):
            image = Path(image)
            if not image.is_file():
                raise FileNotFoundError(f"Image file not found: {image}")
            content = image.read_bytes()
        elif isinstance(image, bytes):
            content = image
        else:
            raise TypeError("image must be a file path or image bytes")

        ocr_image = vision.Image(content=content)

        features = [
            {
                "type_": vision.Feature.Type.DOCUMENT_TEXT_DETECTION,
                "model": self.model_type,
            }
        ]

        image_context = {}
        if self.lang_hint:
            image_context["language_hints"] = [self.lang_hint]

        response = self.vision_client.annotate_image(
            {"image": ocr_image, "features": features, "image_context": image_context}
        )

        response_json = AnnotateImageResponse.to_json(response)
        response = json.loads(response_json)

        return response

    def run(self):
        bdrc_scan_id = self.image_download_dir.name
        img_group_paths = list(self.image_download_dir.iterdir())
        img_group_paths.sort()
        for img_group_path in img_group_paths:
            img_group_id = img_group_path.name
            ocr_output_dir = (
                self.ocr_output_base_dir
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
                    result = self.extract_text(img_path)
                except Exception:
                    print(f"Google OCR issue: {result_fn}")
                    continue
                result_json = json.dumps(result)
                gzip_result = gzip_str(result_json)
                result_fn.write_bytes(gzip_result)

        return self.ocr_output_base_dir / bdrc_scan_id


ENGINE_REGISTER = {"google_vision": GoogleVisionEngine}


class OCRExecutor:
    def __init__(
        self,
        config: ImportConfig,
        image_download_dir: Path,
        engine_register=ENGINE_REGISTER,
    ) -> None:
        self.config = config
        self.image_download_dir = image_download_dir
        self.engine_register = engine_register

    def run(self):
        ocr_engine_class = self.engine_register[self.config.ocr_engine]
        ocr_engine = ocr_engine_class(self.config, self.image_download_dir)
        ocr_output_path = ocr_engine.run()
        return ocr_output_path
