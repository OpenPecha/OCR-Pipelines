import hashlib
from pathlib import Path

import boto3


class BdrcS3Uploader:
    """Uploads the ocr output to s3"""

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

    def get_imagegroup_dir(self, imagegroup: str) -> Path:
        imagegroup_suffix = self.__get_s3_suffix_for_imagegroup(imagegroup)
        return self.base_dir / f"{self.bdrc_scan_id}-{imagegroup_suffix}"

    def upload(self, ocr_output_path: Path):
        """Save the ocr output to s3

        Args:
            ocr_output_paths (Path): path to the ocr output
        """
        for local_imagegroup_dir in ocr_output_path.iterdir():
            for ocr_output_file in local_imagegroup_dir.iterdir():
                imagegroup = local_imagegroup_dir.name
                s3_imagegroup_dir = self.get_imagegroup_dir(imagegroup)
                s3_ocr_output_path = s3_imagegroup_dir / ocr_output_file.name
                self.bucket.put_object(
                    Key=str(s3_ocr_output_path), Body=ocr_output_file.read_bytes()
                )
