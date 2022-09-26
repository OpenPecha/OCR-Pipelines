
from git import Repo
from pathlib import Path


from openpecha.blupdate import update_pecha
from openpecha.core.pecha import OpenPechaFS
from openpecha.utils import download_pecha, download_pecha_asset

from .config import ImportConfig, ReimportConfig
from .executor import OCRExecutor
from .image_downloader import BDRCImageDownloader
from .logger import Logger
from .parser import OCRParser
from .upload import save_to_s3, publish_pecha



def import_pipeline(work_id: str, config: ImportConfig, img_download_dir: Path):
    ocred_work_logger = Logger(config)
    published_pecha_logger = Logger(config)

    downloader = BDRCImageDownloader(work_id=work_id, output_dir=img_download_dir)
    images_path = downloader.download_images()
    
    ocr_executor = OCRExecutor(images_path, config)
    ocr_output_path = ocr_executor.run()
    
    ocr_parser = OCRParser(ocr_output_path, config)
    pecha_path = ocr_parser.parse()
    
    save_to_s3(ocr_output_path, ocred_work_logger)
    publish_pecha(pecha_path, ocr_output_path)


def reimport_pipeline(pecha_id: str, config: ReimportConfig):
    updated_pecha_logger = Logger(config)
    
    ocr_output_path = download_pecha_asset(pecha_id, asset_name='ocr_output')
    
    ocr_parser = OCRParser(config)
    pecha_path = ocr_parser.parse(ocr_output_path)
    
    old_pecha = download_pecha(pecha_id)
    new_pecha = OpenPechaFS(pecha_path)
    
    updated_pecha = update_pecha(old_pecha, new_pecha)
    
    publish_pecha(updated_pecha, updated_pecha_logger)