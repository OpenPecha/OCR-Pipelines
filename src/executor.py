import gzip
import io
import os
import json

from google.cloud import vision
from google.cloud.vision import AnnotateImageResponse
from pathlib import Path

from src.config import ImportConfig

def gzip_str(string_):
    # taken from https://gist.github.com/Garrett-R/dc6f08fc1eab63f94d2cbb89cb61c33d
    out = io.BytesIO()

    with gzip.GzipFile(fileobj=out, mode="w") as fo:
        fo.write(string_.encode())

    bytes_obj = out.getvalue()
    return bytes_obj


class GoogleVisionEngine:

    def __init__(self, images_base_dir: Path, config: ImportConfig, ocr_base_dir: Path) -> None:
        self.images_base_dir = images_base_dir
        self.model_type = config.model_type
        self.lang_hint = config.lang_hint
        self.ocr_base_dir = ocr_base_dir
        self.vision_client = vision.ImageAnnotatorClient()

    def google_ocr(self, image):
        """
        image: file_path or image bytes
        return: google ocr response in Json
        """
        if isinstance(image, (str, Path)):
            with io.open(image, "rb") as image_file:
                content = image_file.read()
        else:
            content = image
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
        work_id = self.images_base_dir.name
        img_group_paths = list(self.images_base_dir.iterdir())
        img_group_paths.sort()
        for img_group_path in img_group_paths:
            img_group_id = img_group_path.name
            ocr_output_dir = self.ocr_base_dir / work_id / f"{work_id}-{img_group_id}"
            ocr_output_dir.mkdir(exist_ok=True, parents=True)
            img_paths = list(img_group_path.iterdir())
            img_paths.sort()
            for img_path in img_paths:
                result_fn = ocr_output_dir / f"{img_path.stem}.json.gz"
                if result_fn.is_file():
                    continue
                try:
                    result = self.google_ocr(str(img_path))
                except:
                    print(f"Google OCR issue: {result_fn}")
                    continue
                result = json.dumps(result)
                gzip_result = gzip_str(result)
                result_fn.write_bytes(gzip_result)

        return self.ocr_base_dir / work_id

ENGINE_REGISTER = {
    'google_vision': GoogleVisionEngine
}

class OCRExecutor:

    def __init__(self, images_base_dir : Path, config : ImportConfig, ocr_base_dir : Path, engine_register=ENGINE_REGISTER) -> None:
        self.images_base_dir = images_base_dir
        self.config = config
        self.ocr_base_dir= ocr_base_dir
        self.engine_register = engine_register

    
    def run(self):
        ocr_engine_class = self.engine_register[self.config.ocr_engine]
        ocr_engine = ocr_engine_class(self.images_base_dir, self.config, self.ocr_base_dir)
        ocr_output_path = ocr_engine.run()
        return ocr_output_path
