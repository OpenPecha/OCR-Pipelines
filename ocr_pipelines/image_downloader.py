import io
import logging
from pathlib import Path
from typing import Iterator, Union

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

    def save_with_wand(self, bits, output_fn) -> bool:
        try:
            with WandImage(blob=bits.getvalue()) as img:
                img.format = "png"
                img.save(filename=str(output_fn))
                return True
        except Exception:
            logging.exception(
                f"Error in saving: {output_fn} : origfilename: {output_fn.name}"
            )
            return False

    def save_img_with_pillow(self, fp: io.BytesIO, fn: Path) -> bool:
        """
        uses pillow to interpret the bits as an image and save as a format
        that is appropriate for Google Vision (png instead of tiff for instance).
        """
        try:
            img = PillowImage.open(fp)
            img.save(str(fn))
        except Exception:
            logging.exception(f"Error in saving: {fn}")
            return False

        return True

    def save_img(self, fp: io.BytesIO, fn: Union[str, Path], img_group_dir: Path):
        """Save the image in .png format to `img_groupdir/fn

        Google Vision API does not support bdrc tiff images.

        Args:
            fp (io.BytesIO): image bits
            fn (str): filename
            img_group_dir (Path): directory to save the image
        """
        output_fn = img_group_dir / fn
        fn = Path(fn)
        if fn.suffix in [".tif", ".tiff", ".TIF"]:
            output_fn = img_group_dir / f"{fn.stem}.png"

        saved = self.save_img_with_pillow(fp, output_fn)
        if not saved:
            self.save_with_wand(fp, output_fn)

    def save_img_group(self, img_group, img_group_dir):
        s3_folder_prefix = buda_api.get_s3_folder_prefix(self.bdrc_scan_id, img_group)
        for img_fn in self.get_s3_img_list(img_group):
            img_path_s3 = Path(s3_folder_prefix) / img_fn
            img_bits = buda_api.gets3blob(str(img_path_s3))
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
