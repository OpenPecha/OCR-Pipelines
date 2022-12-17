import logging
from pathlib import Path
from typing import Iterator

from openpecha.buda import api as buda_api
from PIL import Image as PillowImage
from wand.image import Image as WandImage

from ocr_pipelines.exceptions import BdcrScanNotFound


class BDRCImageDownloader:
    def __init__(self, bdrc_scan_id: str, output_dir: Path) -> None:
        self.bdrc_scan_id = bdrc_scan_id
        self.output_dir = output_dir

    def get_img_groups(self):
        """
        Get the image groups from the bdrc scan id
        """
        res = buda_api.get_buda_scan_info(self.bdrc_scan_id)
        if not res:
            raise BdcrScanNotFound(f"Scan {self.bdrc_scan_id} not found")
        yield from res["image_groups"]

    def get_s3_img_list(self, img_group: str) -> Iterator[str]:
        """Returns image list with filename for the given `image_group`"""
        for img in buda_api.get_image_list_s3(self.bdrc_scan_id, img_group):
            yield img["filename"]

    def save_with_wand(self, bits, output_fn):
        try:
            with WandImage(blob=bits.getvalue()) as img:
                img.format = "png"
                img.save(filename=str(output_fn))
        except Exception:
            logging.exception(
                f"Error in saving: {output_fn} : origfilename: {output_fn.name}"
            )

    def save_img(self, bits, origfilename, imagegroup_output_dir):
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
        except Exception:
            if bits.getvalue():
                self.save_with_wand(bits, output_fn)
            else:
                logging.exception(f"Empty image: {output_fn}")
            return

        try:
            img.save(str(output_fn))
        except Exception:
            del img
            self.save_with_wand(bits, output_fn)

    def save_img_group(self, img_group, img_group_dir):
        s3_folder_prefix = buda_api.get_s3_folder_prefix(self.bdrc_scan_id, img_group)
        for img_fn in self.get_s3_img_list(img_group):
            img_path_s3 = s3_folder_prefix + "/" + img_fn
            img_bits = buda_api.gets3blob(img_path_s3)
            if img_bits:
                self.save_img(img_bits, img_fn, img_group_dir)

    def download(self):
        bdrc_scan_dir = self.output_dir / self.bdrc_scan_id
        bdrc_scan_dir.mkdir(exist_ok=True, parents=True)
        for img_group_id in self.get_img_groups():
            img_group_dir = bdrc_scan_dir / img_group_id
            img_group_dir.mkdir(exist_ok=True, parents=True)
            self.save_img_group(img_group_id, img_group_dir)

        return bdrc_scan_dir
