
import tempfile
from pathlib import Path


from openpecha.core.pecha import OpenPechaFS
from openpecha.utils import download_pecha_assets

from ocr_pipelines.config import ImportConfig, ReimportConfig
from ocr_pipelines.executor import OCRExecutor
from ocr_pipelines.image_downloader import BDRCImageDownloader
from ocr_pipelines.parser import OCRParser
from ocr_pipelines.upload import save_to_s3
from ocr_pipelines.update_pecha import update_pecha



def import_pipeline(work_id: str, config: ImportConfig):

    downloader = BDRCImageDownloader(work_id=work_id, output_dir=config.img_download_base_dir)
    images_download_dir = downloader.download_images()

    ocr_executor = OCRExecutor(config=config, image_download_dir=images_download_dir)
    ocr_output_path = ocr_executor.run()

    with tempfile.TemporaryDirectory() as tmpdirname:
        opf_dir = Path(tmpdirname)
        ocr_parser = OCRParser(config=config, ocr_output_path=ocr_output_path, opf_dir=opf_dir)
        pecha = ocr_parser.parse()
        
        save_to_s3(asset_base_dir=ocr_output_path, asset_name="ocr_output")
        pecha.publish(asset_path=ocr_output_path, asset_name="ocr_output")


def reimport_pipeline(pecha_id: str, config: ReimportConfig):
    
    ocr_output_path = download_pecha_assets(pecha_id, asset_name='ocr_output')

    with tempfile.TemporaryDirectory() as tmpdirname:
        opf_dir = Path(tmpdirname)
    
        ocr_parser = OCRParser(config=config, ocr_output_path=ocr_output_path, opf_dir=opf_dir, pecha_id=pecha_id)
        new_pecha = ocr_parser.parse(ocr_output_path)
        
        old_pecha = OpenPechaFS(pecha_id=pecha_id)
        
        updated_pecha = update_pecha(old_pecha, new_pecha)
        updated_pecha.publish(asset_path=ocr_output_path, asset_name="ocr_output")



if __name__ == "__main__":
    work_id = "W8LS68000"
    config = ImportConfig(ocr_engine="google_vision", model_type="builtin/weekly")
    img_download_dir = Path('./data/images/')
    ocr_output_base_dir = Path('./data/ocr_outputs')
    import_pipeline(work_id = work_id, config=config, img_download_dir=img_download_dir, ocr_output_base_dir=ocr_output_base_dir)