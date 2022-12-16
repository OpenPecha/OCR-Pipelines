import hashlib
import json
from pathlib import Path

import boto3


class BdrcS3Uploader:
    """Class to represent BDRC S3 Uploader.

    This uploader saves ocr images, output and metdatato s3

    Args:
        bdrc_scan_id (str): bdrc scan id
        service (str): service name (e.g. google-vision, namsel-ocr)
        batch (str): batch name
    """

    def __init__(self, bdrc_scan_id: str, service: str, batch: str):
        self.bdrc_scan_id = bdrc_scan_id
        self.service = service
        self.batch = batch

        self.bucket_name = "ocr.bdrc.io"
        self.client = boto3.client("s3")
        self.bucket = boto3.resource("s3").Bucket(self.bucket_name)

    def __get_first_two_chars_hash(self, string) -> str:
        return hashlib.md5(string.encode("utf-8")).hexdigest()[:2]

    @staticmethod
    def __get_s3_suffix_for_imagegroup(imagegroup: str) -> str:
        pre, rest = imagegroup[0], imagegroup[1:]
        if pre == "I" and rest.isdigit() and len(rest) == 4:
            return rest
        return imagegroup

    @property
    def base_dir(self) -> Path:
        """Returns the base dir to store the ocr outputs

        the function can be inspired from
        https://github.com/buda-base/volume-manifest-tool/blob/f8b495d908b8de66ef78665f1375f9fed13f6b9c/manifestforwork.py#L94
        """
        hash_ = self.__get_first_two_chars_hash(self.bdrc_scan_id)
        return Path("Works") / hash_ / self.bdrc_scan_id / self.service / self.batch

    @property
    def s3_ocr_outputs_dir(self) -> Path:
        return self.base_dir / "output"

    @property
    def s3_ocr_images_dir(self) -> Path:
        return self.base_dir / "images"

    def get_imagegroup_dir(self, base_dir: Path, imagegroup: str) -> Path:
        imagegroup_suffix = self.__get_s3_suffix_for_imagegroup(imagegroup)
        return base_dir / f"{self.bdrc_scan_id}-{imagegroup_suffix}"

    def upload_metadata(self, metadata: dict):
        """Add metadata to s3 at `base_dir`/info.json

        Args:
            metadata (dict): metadata to add
        """

        metadata_path = self.base_dir / "info.json"
        metadata_bytes = bytes(json.dumps(metadata), "utf-8")
        self.bucket.put_object(Key=str(metadata_path), Body=metadata_bytes)

    def upload_ocr_images(self, images_path: Path):
        """Save the ocr images to s3"""
        for local_imagegroup_dir in images_path.iterdir():
            for image_file in local_imagegroup_dir.iterdir():
                imagegroup = local_imagegroup_dir.name
                s3_imagegroup_dir = self.get_imagegroup_dir(
                    self.s3_ocr_images_dir, imagegroup
                )
                s3_image_path = s3_imagegroup_dir / image_file.name
                self.bucket.put_object(
                    Key=str(s3_image_path), Body=image_file.read_bytes()
                )

    def upload_ocr_outputs(self, ocr_output_path: Path):
        """Save the ocr output to s3

        Args:
            ocr_output_paths (Path): path to the ocr output
        """
        for local_imagegroup_dir in ocr_output_path.iterdir():
            for ocr_output_file in local_imagegroup_dir.iterdir():
                imagegroup = local_imagegroup_dir.name
                s3_imagegroup_dir = self.get_imagegroup_dir(
                    self.s3_ocr_outputs_dir, imagegroup
                )
                s3_ocr_output_path = s3_imagegroup_dir / ocr_output_file.name
                self.bucket.put_object(
                    Key=str(s3_ocr_output_path), Body=ocr_output_file.read_bytes()
                )

    def upload(self, ocr_images_path: Path, ocr_outputs_path: Path, metadata: dict):
        """Upload the ocr images, output and metadata to s3

        both ocr_images_path and ocr_outputs_path should have the same structure.
        e.g.: W0001/I0001/0001.jpg and W0001/I0001/0001.json

        Args:
            ocr_images_path (Path): path to the ocr images
            ocr_output_paths (Path): path to the ocr output
            metadata (dict): metadata to add
        """
        self.upload_metadata(metadata)
        self.upload_ocr_outputs(ocr_outputs_path)
        self.upload_ocr_images(ocr_images_path)
