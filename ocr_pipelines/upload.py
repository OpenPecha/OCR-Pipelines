import hashlib
from pathlib import Path

import boto3
import botocore
from openpecha.core.pecha import OpenPechaFS

OCR_OUTPUT_BUCKET = "ocr.bdrc.io"
S3 = boto3.resource("s3")
S3_client = boto3.client("s3")
ocr_output_bucket = S3.Bucket(OCR_OUTPUT_BUCKET)


class BdrcS3Uploader:
    """Uploads the ocr output to s3"""

    def __init__(self, bdrc_scan_id: str, service: str, batch: str):
        self.bdrc_scan_id = bdrc_scan_id
        self.service = service
        self.batch = batch

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


def is_archived(key):
    try:
        S3_client.head_object(Bucket=OCR_OUTPUT_BUCKET, Key=key)
    except botocore.errorfactory.ClientError:
        return False
    return True


def save_to_s3(path: Path, service: str, batch: str) -> None:
    """Saves the ocr output to s3

    Args:
        path (Path): path to the bdrc scan ocr output
        service (str): service (eg: google-vision)
        batch_id (str): batch id
    """

    for img_group_dir in path.iterdir():
        # s3_path_prefix = get_s3_path_prefix(bdrc_scan_id, img_group_id, service, batch)
        s3_path_prefix = ""
        for ocr_output_file in img_group_dir.iterdir():
            s3_output_path = f"{s3_path_prefix}/{ocr_output_file.name}"
            if is_archived(s3_output_path):
                continue
            ocr_output_bucket.put_object(
                Key=s3_output_path, Body=ocr_output_file.read_bytes()
            )


if __name__ == "__main__":
    pecha_path = Path.home() / "esukhia/data/opf/I1AF6985A"
    asset_path = Path.home() / "esukhia/data/ocr_output/WA00KG0614"
    pecha_id = pecha_path.stem
    pecha = OpenPechaFS(pecha_id=pecha_id, path=pecha_path)
    pecha.publish(asset_path=asset_path, asset_name="ocr_output")
