import boto3
import botocore
import hashlib
import os
import shutil

from openpecha.core.pecha import OpenPechaFS
from openpecha.github_utils import create_release, create_github_repo, create_local_repo, commit, get_github_repo, update_github_repo_visibility
from openpecha.utils import load_yaml

OCR_OUTPUT_BUCKET = "ocr.bdrc.io"
S3 = boto3.resource("s3")
S3_client = boto3.client("s3")
ocr_output_bucket = S3.Bucket(OCR_OUTPUT_BUCKET)

ORG_NAME = "Openpecha-data"

TOKEN = os.environ['GITHUB_TOKEN'] if 'GITHUB_TOKEN' in os.environ else ""


def get_s3_prefix_path(work_local_id, imagegroup):
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
    return f"{base_dir}/ocr_output_path/{work_local_id}-{suffix}"

def is_archived(key):
    try:
        S3_client.head_object(Bucket=OCR_OUTPUT_BUCKET, Key=key)
    except botocore.errorfactory.ClientError:
        return False
    return True

def save_to_s3(ocr_base_dir):

    work_id = ocr_base_dir.stem

    for img_group_dir in ocr_base_dir.iter_dir():
        img_group_id = img_group_dir.stem
        s3_path = get_s3_prefix_path(work_id, img_group_id)
        for ocr_output_file in img_group_dir.iter_dir():
            
            s3_output_path = f"{s3_path}/{ocr_output_file.name}"
            if is_archived(s3_output_path):
                continue
            ocr_output_bucket.put_object(Key=s3_output_path, Body=ocr_output_file.read_bytes())

def get_visibility(opf_path):
    meta = load_yaml((opf_path / f"{opf_path.stem}.opf/meta.yml"))
    if (meta["source_metadata"]["status"] != "http://purl.bdrc.io/admindata/StatusReleased"
        or meta["source_metadata"]["access"] != "http://purl.bdrc.io/admindata/AccessOpen"):
        return "private"
    return "public"


def publish_pecha(pecha_path, asset_path):
    asset_paths = []
    pecha = OpenPechaFS(pecha_path)
    pecha.publish()
    repo_name = pecha_path.name
    shutil.make_archive(asset_path, "zip", asset_path)
    asset_paths.append(f"{str(asset_path)}.zip")
    create_release(
        repo_name, prerelease=False, asset_paths=asset_paths, org=ORG_NAME, token=TOKEN
    )