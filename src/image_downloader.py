from typing import Callable
import boto3
import botocore
import hashlib
import io
import logging
import requests
import rdflib

from PIL import Image as PillowImage
from pathlib import Path
from rdflib import URIRef
from rdflib.namespace import Namespace, NamespaceManager
from wand.image import Image as WandImage

from src.exceptions import ImageGroupNotFound

ARCHIVE_BUCKET = "archive.tbrc.org"
S3 = boto3.resource("s3")
archive_bucket = S3.Bucket(ARCHIVE_BUCKET)

BATCH_PREFIX = "batch"
DEBUG = {"status": False}


BDR = Namespace("http://purl.bdrc.io/resource/")
NSM = NamespaceManager(rdflib.Graph())
NSM.bind("bdr", BDR)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s, %(levelname)s: %(message)s")
file_handler = logging.FileHandler("bdrc_ocr.log")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)




class BDRCImageDownloader:

    def __init__(self, work_id : str, output_dir: Path) -> None:
        self.work_id = work_id
        self.output_dir = output_dir

    
    def get_image_groups(self):
        image_groups = {}
        try:
            r = requests.get(
                f"http://purl.bdrc.io/query/table/volumesForWork?R_RES=bdr:{self.work_id}&format=json&pageSize=500"
            )
        except Exception:
            raise ImageGroupNotFound(f"Volume Info Error: No info found for Work {self.work_id}: status code: {r.status_code}")
        res = r.json()
        for b in res["results"]["bindings"]:
            image_group_url = NSM.qname(URIRef(b["volid"]["value"]))
            image_group_id = image_group_url[4:]
            image_groups[image_group_id] = image_group_url
        return image_groups
    
    def get_s3_prefix_path(self, image_group_id, service_id=None, batch_id=None, data_types=None):
        """
        the input is like W22084, I0886. The output is an s3 prefix ("folder"), the function
        can be inspired from
        https://github.com/buda-base/volume-manifest-tool/blob/f8b495d908b8de66ef78665f1375f9fed13f6b9c/manifestforwork.py#L94
        which is documented
        """
        md5 = hashlib.md5(str.encode(self.work_id))
        two = md5.hexdigest()[:2]

        pre, rest = image_group_id[0], image_group_id[1:]
        if pre == "I" and rest.isdigit() and len(rest) == 4:
            suffix = rest
        else:
            suffix = image_group_id

        base_dir = f"Works/{two}/{self.work_id}"
        if service_id is not None:
            batch_dir = f"{base_dir}/{service_id}/{batch_id}"
            paths = {BATCH_PREFIX: batch_dir}
            for dt in data_types:
                paths[dt] = f"{batch_dir}/{dt}/{self.work_id}-{suffix}"
            return paths
        return f"{base_dir}/images/{self.work_id}-{suffix}"
    
    def get_s3_image_list(self, image_group_url):
        """
        returns the content of the dimension.json file for a volume ID, accessible at:
        https://iiifpres.bdrc.io/il/v:bdr:V22084_I0888 for volume ID bdr:V22084_I0888
        """
        r = requests.get(f"https://iiifpres.bdrc.io/il/v:{image_group_url}")
        if r.status_code != 200:
            logger.error(
                f"Volume Images list Error: No images found for volume {image_group_url}: status code: {r.status_code}"
            )
            return {}
        return r.json()
    
    def image_exists_locally(self, origfilename, imagegroup_output_dir):
        if origfilename.endswith(".tif"):
            output_fn = imagegroup_output_dir / f'{origfilename.split(".")[0]}.png'
            if output_fn.is_file():
                return True
        else:
            output_fn = imagegroup_output_dir / origfilename
            if output_fn.is_file():
                return True
        return False
    
    def get_s3_bits(self, s3path, bucket):
        """
        get the s3 binary data in memory
        """
        f = io.BytesIO()
        try:
            bucket.download_fileobj(s3path, f)
            return f
        except botocore.exceptions.ClientError as e:
            if e.response["Error"]["Code"] == "404":
                logger.exception(f"The object does not exist, {s3path}")
            else:
                raise
        return
    
    def save_with_wand(self, bits, output_fn):
        try:
            with WandImage(blob=bits.getvalue()) as img:
                img.format = "png"
                img.save(filename=str(output_fn))
        except Exception as e:
            logger.exception(
                f"Error in saving: {output_fn} : origfilename: {output_fn.name}"
            )
    
    def save_file(self, bits, origfilename, imagegroup_output_dir):
        """
        uses pillow to interpret the bits as an image and save as a format
        that is appropriate for Google Vision (png instead of tiff for instance).
        This may also apply some automatic treatment
        """
        output_fn = imagegroup_output_dir / origfilename
        if Path(origfilename).suffix in [".tif", ".tiff", ".TIF"]:
            output_fn = imagegroup_output_dir / f'{origfilename.split(".")[0]}.png'
        if output_fn.is_file():
            return
        try:
            img = PillowImage.open(bits)
        except Exception as e:
            if bits.getvalue():
                self.save_with_wand(bits, output_fn)
            else:
                logger.exception(f"Empty image: {output_fn}")
            return

        try:
            img.save(str(output_fn))
        except:
            del img
            self.save_with_wand(bits, output_fn)

    def save_image_group(self, image_group_id, image_group_url, img_group_dir):
        s3_prefix = self.get_s3_prefix_path(image_group_id)
        for imageinfo in self.get_s3_image_list(image_group_url):
            if self.image_exists_locally(imageinfo["filename"], img_group_dir):
                continue
            s3path = s3_prefix + "/" + imageinfo["filename"]
            if DEBUG["status"]:
                print(f'\t- downloading {imageinfo["filename"]}')
            filebits = self.get_s3_bits(s3path, archive_bucket)
            if filebits:
                self.save_file(filebits, imageinfo["filename"], img_group_dir)

    
    def download_images(self):
        (self.output_dir / self.work_id).mkdir(exist_ok=True, parents=True)
        image_output_dir = (self.output_dir / self.work_id)
        image_groups = self.get_image_groups()
        for img_group_id, img_group_url in image_groups.items():
            (image_output_dir / img_group_id).mkdir(exist_ok=True, parents=True)
            img_group_dir = (image_output_dir / img_group_id)
            self.save_image_group(img_group_id, img_group_url, img_group_dir)

        return image_output_dir

        