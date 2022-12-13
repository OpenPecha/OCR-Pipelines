import hashlib
import os
from pathlib import Path

import boto3
import botocore
from openpecha.core.pecha import OpenPechaFS

OCR_OUTPUT_BUCKET = "ocr.bdrc.io"
S3 = boto3.resource("s3")
S3_client = boto3.client("s3")
ocr_output_bucket = S3.Bucket(OCR_OUTPUT_BUCKET)

ORG_NAME = "Openpecha-data"

TOKEN = os.environ["GITHUB_TOKEN"] if "GITHUB_TOKEN" in os.environ else ""


def get_bdrc_scan_id_hash(bdrc_scan_id: str) -> str:
    return hashlib.md5(bdrc_scan_id.encode("utf-8")).hexdigest()[:2]


def get_s3_suffix_for_imagegroup(imagegroup: str) -> str:
    pre, rest = imagegroup[0], imagegroup[1:]
    if pre == "I" and rest.isdigit() and len(rest) == 4:
        return rest
    return imagegroup


def get_s3_path_prefix(bdrc_scan_id: str, imagegroup: str, service: str, batch: str):
    """Returns the s3 prefix for the given bdrc_scan_id and imagegroup

    the function can be inspired from
    https://github.com/buda-base/volume-manifest-tool/blob/f8b495d908b8de66ef78665f1375f9fed13f6b9c/manifestforwork.py#L94

    Args:
        bdrc_scan_id (str): bdrc scan id (eg: W22084)
        imagegroup (str): imagegroup (eg: I0886)
        service (str): service (eg: google-vision)
        batch_id (str): batch id

    Returns:
        str: s3 prefix (folder)
    """
    hash_ = get_bdrc_scan_id_hash(bdrc_scan_id)
    imagegroup_suffix = get_s3_suffix_for_imagegroup(imagegroup)

    return f"Works/{hash_}/{bdrc_scan_id}/{service}/{batch}/{bdrc_scan_id}-{imagegroup_suffix}"


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

    bdrc_scan_id = path.stem
    for img_group_dir in path.iterdir():
        img_group_id = img_group_dir.stem
        s3_path_prefix = get_s3_path_prefix(bdrc_scan_id, img_group_id, service, batch)
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
