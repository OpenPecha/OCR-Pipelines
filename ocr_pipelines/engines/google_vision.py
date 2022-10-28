import json
from pathlib import Path
from typing import Union

from google.cloud import vision
from google.cloud.vision import AnnotateImageResponse
from google.oauth2.service_account import Credentials

from ocr_pipelines.engines.base import BaseEngine

ImagePath = Union[str, Path]
ImageBytes = bytes
Image = Union[ImagePath, ImageBytes]


class GoogleVisionEngine(BaseEngine):
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

    def ocr(self, image: Image) -> dict:
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
