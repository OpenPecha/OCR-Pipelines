import boto3
import botocore
import hashlib
import os

from pathlib import Path
from openpecha.core.pecha import OpenPechaFS

OCR_OUTPUT_BUCKET = "ocr.bdrc.io"
S3 = boto3.resource("s3")
S3_client = boto3.client("s3")
ocr_output_bucket = S3.Bucket(OCR_OUTPUT_BUCKET)

ORG_NAME = "Openpecha-data"

TOKEN = os.environ['GITHUB_TOKEN'] if 'GITHUB_TOKEN' in os.environ else ""


def get_s3_prefix_path(work_local_id:str, imagegroup:str, asset_name:str):
    """
    the input is like W22084, I0886. The output is an s3 prefix ("folder"), the function
    can be inspired from
    https://github.com/buda-base/volume-manifest-tool/blob/f8b495d908b8de66ef78665f1375f9fed13f6b9c/manifestforwork.py#L94
    which is documented
    """
    md5 = hashlib.md5(str.encode(work_local_id))
    two = md5.hexdigest()[:2]

    pre, rest = imagegroup[0], imagegroup[1:]
    if pre == "I" and rest.isdigit() and len(rest) == 4:
        suffix = rest
    else:
        suffix = imagegroup

    base_dir = f"Works/{two}/{work_local_id}"
    return f"{base_dir}/{asset_name}/{work_local_id}-{suffix}"

def is_archived(key):
    try:
        S3_client.head_object(Bucket=OCR_OUTPUT_BUCKET, Key=key)
    except botocore.errorfactory.ClientError:
        return False
    return True

def save_to_s3(asset_base_dir:Path, asset_name:str="ocr_output"):

    work_id = asset_base_dir.stem

    for img_group_dir in asset_base_dir.iter_dir():
        img_group_id = img_group_dir.stem
        s3_path = get_s3_prefix_path(work_id, img_group_id, asset_name)
        for ocr_output_file in img_group_dir.iter_dir():
            s3_output_path = f"{s3_path}/{ocr_output_file.name}"
            if is_archived(s3_output_path):
                continue
            ocr_output_bucket.put_object(Key=s3_output_path, Body=ocr_output_file.read_bytes())


if __name__ == "__main__":
    pecha_path = Path.home() / "esukhia/data/opf/I1AF6985A"
    asset_path = Path.home() / "esukhia/data/ocr_output/WA00KG0614"
    pecha_id = pecha_path.stem
    pecha = OpenPechaFS(pecha_id=pecha_id, path=pecha_path)
    pecha.publish(asset_path=asset_path, asset_name="ocr_output")