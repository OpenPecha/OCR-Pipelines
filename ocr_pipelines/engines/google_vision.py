import json
import logging
from pathlib import Path

from google.api_core import exceptions as gcloud_exceptions
from google.cloud import vision
from google.cloud.vision import AnnotateImageResponse
from google.oauth2.service_account import Credentials

from ocr_pipelines.engines import OcrEngine
from ocr_pipelines.engines.engine import ImageBytes, ImageType
from ocr_pipelines.exceptions import GoogleVisionCredentialsError

GoogleVisionFeatures = list[dict]


class GoogleVisionEngine(OcrEngine):
    # TODO: remove dirs

    def __init__(
        self,
        credentials: dict,
        model_type: str = None,
        lang_hint: str = None,
        image_download_dir: Path = Path.home(),
        ocr_outputs_path: Path = Path.home(),
    ) -> None:
        self.model_type = model_type
        self.lang_hint = lang_hint
        self.image_download_dir = image_download_dir
        self.ocr_outputs_path = ocr_outputs_path

        self.credentials = Credentials.from_service_account_info(credentials)
        self.vision_client = vision.ImageAnnotatorClient(credentials=self.credentials)
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    @staticmethod
    def load_image_bytes(image: ImageType) -> ImageBytes:
        """Load image bytes from image path or image bytes.

        Args:
            image: file_path or image bytes
        Returns:
            image_bytes: image bytes

        Raises:
            FileNotFoundError: if image path is not found
            TypeError: if image is not str or Path or bytes
        """
        if isinstance(image, (str, Path)):
            image = Path(image)
            if not image.is_file():
                raise FileNotFoundError(f"Image file not found: {image}")
            return image.read_bytes()
        elif isinstance(image, ImageBytes):
            return image
        else:
            raise TypeError("image must be a file path or image bytes")

    @property
    def features(self) -> GoogleVisionFeatures:
        return [
            {
                "type_": vision.Feature.Type.DOCUMENT_TEXT_DETECTION,
                "model": self.model_type,
            }
        ]

    @property
    def image_context(self) -> dict:
        image_context = {}
        if self.lang_hint:
            image_context["language_hints"] = [self.lang_hint]
        return image_context

    @staticmethod
    def response_to_dict(response: AnnotateImageResponse) -> dict:
        response_json = AnnotateImageResponse.to_json(response)
        return json.loads(response_json)

    def ocr(self, image: ImageType) -> dict:
        """Run OCR on a single image.

        Args:
            image: file_path or image bytes
        Returns:
            response: ocr response in dict
        """

        image_bytes = self.load_image_bytes(image)
        ocr_image = vision.Image(content=image_bytes)

        try:
            response = self.vision_client.annotate_image(
                {
                    "image": ocr_image,
                    "features": self.features,
                    "image_context": self.image_context,
                }
            )
        except gcloud_exceptions.PermissionDenied as e:
            raise GoogleVisionCredentialsError(
                "Cannot access Google OCR. "
                "Please check your credentials, make sure both Google Vision API and Billing are enabled"
            ) from e
        except gcloud_exceptions.ClientError as e:
            self.logger.exception(e)
            raise e
        except Exception as e:
            self.logger.exception(e)
            raise e

        response_dict = self.response_to_dict(response)

        return response_dict
