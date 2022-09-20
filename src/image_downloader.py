import boto3
import botocore
import hashlib
import io
import logging
import os
import requests
import rdflib

from PIL import Image as PillowImage
from rdflib import URIRef
from rdflib.namespace import Namespace, NamespaceManager
from wand.image import Image as WandImage

from pathlib import Path

ARCHIVE_BUCKET = "archive.tbrc.org"
OCR_OUTPUT_BUCKET = "ocr.bdrc.io"
S3 = boto3.resource("s3")
S3_client = boto3.client("s3")
archive_bucket = S3.Bucket(ARCHIVE_BUCKET)
ocr_output_bucket = S3.Bucket(OCR_OUTPUT_BUCKET)

BDR = Namespace("http://purl.bdrc.io/resource/")
NSM = NamespaceManager(rdflib.Graph())
NSM.bind("bdr", BDR)

BATCH_PREFIX = "batch"
DEBUG = {"status": False}

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
        
    

    def get_value(self, json_node):
        if json_node["type"] == "literal":
            return json_node["value"]
        else:
            return NSM.qname(URIRef(json_node["value"]))

    def get_work_local_id(self, work):
        if ":" in work:
            return work.split(":")[-1], work
        else:
            return work, f"bdr:{work}"
    
    def get_volume_infos(self, work_prefix_url):
        """
        the input is something like bdr:W22084, the output is a list like:
        [
        {
            "vol_num": 1,
            "volume_prefix_url": "bdr:V22084_I0886",
            "imagegroup": "I0886"
        },
        ...
        ]
        """
        r = requests.get(
            f"http://purl.bdrc.io/query/table/volumesForWork?R_RES={work_prefix_url}&format=json&pageSize=500"
        )
        if r.status_code != 200:
            logger.error(
                f"Volume Info Error: No info found for Work {work_prefix_url}: status code: {r.status_code}"
            )
            return
        # the result of the query is already in ascending volume order
        res = r.json()
        for b in res["results"]["bindings"]:
            volume_prefix_url = NSM.qname(URIRef(b["volid"]["value"]))
            yield {
                "vol_num": self.get_value(b["volnum"]),
                "volume_prefix_url": volume_prefix_url,
                "imagegroup": volume_prefix_url[4:],
            }
        
    def get_s3_image_list(self, volume_prefix_url):
        """
        returns the content of the dimension.json file for a volume ID, accessible at:
        https://iiifpres.bdrc.io/il/v:bdr:V22084_I0888 for volume ID bdr:V22084_I0888
        """
        r = requests.get(f"https://iiifpres.bdrc.io/il/v:{volume_prefix_url}")
        if r.status_code != 200:
            logger.error(
                f"Volume Images list Error: No images found for volume {volume_prefix_url}: status code: {r.status_code}"
            )
            return {}
        return r.json()
    
    def get_s3_prefix_path(self, work_local_id, imagegroup, service_id=None, batch_id=None, data_types=None):
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
        if service_id is not None:
            batch_dir = f"{base_dir}/{service_id}/{batch_id}"
            paths = {BATCH_PREFIX: batch_dir}
            for dt in data_types:
                paths[dt] = f"{batch_dir}/{dt}/{work_local_id}-{suffix}"
            return paths
        return f"{base_dir}/images/{work_local_id}-{suffix}"
    
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
    
    def _binarize(self, img, th=127):
        return img.convert("L").point(lambda x: 255 if x > th else 0, mode='1')
    
    def save_file(self, bits, origfilename, imagegroup_output_dir, binarize=False):
        """
        uses pillow to interpret the bits as an image and save as a format
        that is appropriate for Google Vision (png instead of tiff for instance).
        This may also apply some automatic treatment
        """
        imagegroup_output_dir.mkdir(exist_ok=True, parents=True)
        output_fn = imagegroup_output_dir / origfilename
        if Path(origfilename).suffix in [".tif", ".tiff", ".TIF"]:
            output_fn = imagegroup_output_dir / f'{origfilename.split(".")[0]}.png'
        if output_fn.is_file():
            return
        try:
            img = PillowImage.open(bits)
            if binarize:
                img = self._binarize(img)
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
    
    def save_images_for_vol(self, volume_prefix_url, work_local_id, imagegroup, images_base_dir, binarize=False):
        """
        this function gets the list of images of a volume and download all the images from s3.
        The output directory is output_base_dir/work_local_id/imagegroup
        """
        s3prefix = self.get_s3_prefix_path(work_local_id, imagegroup)
        for imageinfo in self.get_s3_image_list(volume_prefix_url):
            # if DEBUG['status'] and not imageinfo['filename'].split('.')[0] == 'I1KG35630002': continue
            imagegroup_output_dir = images_base_dir / work_local_id / imagegroup
            if self.image_exists_locally(imageinfo["filename"], imagegroup_output_dir):
                continue
            s3path = s3prefix + "/" + imageinfo["filename"]
            if DEBUG["status"]:
                print(f'\t- downloading {imageinfo["filename"]}')
            filebits = self.get_s3_bits(s3path, archive_bucket)
            if filebits:
                self.save_file(filebits, imageinfo["filename"], imagegroup_output_dir, binarize=binarize)

    def download_images(self):
        work_local_id, work = self.get_work_local_id(self.work_id)
        for vol_info in self.get_volume_infos(work):
            imagegroup = vol_info["imagegroup"]
            print(f"[INFO] Downloading {imagegroup} images ....")
            self.save_images_for_vol(
                volume_prefix_url=vol_info["volume_prefix_url"],
                work_local_id=work_local_id,
                imagegroup=imagegroup,
                images_base_dir=self.output_dir,
                binarize=False
            )


if __name__ == "__main__":
    image_downloader = BDRCImageDownloader(work_id="W20571", output_dir=Path('./data'))
    image_downloader.download_images()