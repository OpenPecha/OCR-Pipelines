
import tempfile
from pathlib import Path


from openpecha.core.pecha import OpenPechaFS
from openpecha.utils import download_pecha, download_pecha_asset

from .config import ImportConfig, ReimportConfig
from .executor import OCRExecutor
from .image_downloader import BDRCImageDownloader
from .logger import Logger
from .parser import OCRParser
from .upload import save_to_s3, publish_pecha
from .update_pecha import update_pecha



def import_pipeline(work_id: str, config: ImportConfig, img_download_dir: Path, ocr_base_dir:Path):

    downloader = BDRCImageDownloader(work_id=work_id, output_dir=img_download_dir)
    images_base_dir = downloader.download_images()
    
    ocr_executor = OCRExecutor(images_base_dir=images_base_dir, config=config, ocr_base_dir=ocr_base_dir)
    ocr_output_path = ocr_executor.run()

    with tempfile.TemporaryDirectory() as tmpdirname:
        opf_dir = Path(tmpdirname)
        ocr_parser = OCRParser(config=config, ocr_output_path=ocr_output_path, opf_dir=opf_dir)
        pecha_path = ocr_parser.parse()
        
        save_to_s3(asset_base_dir=ocr_output_path, asset_name="ocr_output")
        publish_pecha(pecha_path=pecha_path, asset_path=ocr_output_path, asset_name="ocr_output")


def reimport_pipeline(pecha_id: str, config: ReimportConfig):
    
    ocr_output_path = download_pecha_asset(pecha_id, asset_name='ocr_output')

    with tempfile.TemporaryDirectory() as tmpdirname:
        opf_dir = Path(tmpdirname)
    
        ocr_parser = OCRParser(config=config, ocr_output_path=ocr_output_path, opf_dir=opf_dir, pecha_id=pecha_id)
        pecha_path = ocr_parser.parse(ocr_output_path)
        
        old_pecha = download_pecha(pecha_id)
        new_pecha = OpenPechaFS(pecha_path)
        
        updated_pecha = update_pecha(pecha_id, old_pecha, new_pecha.opf_path)
        
        publish_pecha(pecha_path=updated_pecha, asset_path=ocr_output_path, asset_name="ocr_output")