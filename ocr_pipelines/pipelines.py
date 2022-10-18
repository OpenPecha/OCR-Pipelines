import tempfile
from pathlib import Path

from openpecha.core.pecha import OpenPechaFS
from openpecha.utils import download_pecha_assets

from ocr_pipelines.config import ImportConfig, ReimportConfig
from ocr_pipelines.executor import OCRExecutor
from ocr_pipelines.image_downloader import BDRCImageDownloader
from ocr_pipelines.parser import OCRParser
from ocr_pipelines.update_pecha import update_pecha
from ocr_pipelines.upload import save_to_s3


def import_pipeline(bdrc_scan_id: str, config: ImportConfig):
    """Pipeline for importing ocred pecha to opf

    Args:
        bdrc_scan_id (str): bdrc scan id
        config (ImportConfig): import config object
    """

    downloader = BDRCImageDownloader(
        bdrc_scan_id=bdrc_scan_id, output_dir=config.img_download_base_dir
    )
    images_download_dir = downloader.download_images()

    ocr_executor = OCRExecutor(config=config, image_download_dir=images_download_dir)
    ocr_output_path = ocr_executor.run()

    with tempfile.TemporaryDirectory() as tmpdirname:
        ocr_parser = OCRParser(
            config=config, ocr_output_path=ocr_output_path, opf_dir=tmpdirname
        )
        pecha = ocr_parser.parse()

        save_to_s3(asset_base_dir=ocr_output_path, asset_name="ocr_output")
        pecha.publish(asset_path=ocr_output_path, asset_name="ocr_output")


def reimport_pipeline(pecha_id: str, config: ReimportConfig):
    """Pipeline to reimport ocr pecha to opf incase of update in opf parser

    Args:
        pecha_id (str): pecha id
        config (ReimportConfig): Reimport config object
    """

    ocr_output_path = download_pecha_assets(
        pecha_id, asset_type="ocr_output", download_dir=config.ocr_output_base_dir
    )

    with tempfile.TemporaryDirectory() as tmpdirname:

        ocr_parser = OCRParser(
            config=config,
            ocr_output_path=ocr_output_path,
            opf_dir=tmpdirname,
            pecha_id=pecha_id,
        )
        new_pecha = ocr_parser.parse()

        old_pecha = OpenPechaFS(pecha_id=pecha_id)

        updated_pecha = update_pecha(old_pecha, new_pecha)
        updated_pecha.publish(asset_path=ocr_output_path, asset_name="ocr_output")


if __name__ == "__main__":
    bdrc_scan_id = "W8LS68000"
    config = ImportConfig(ocr_engine="google_vision", model_type="builtin/weekly")
    img_download_dir = Path("./data/images/")
    ocr_output_base_dir = Path("./data/ocr_outputs")
    import_pipeline(
        bdrc_scan_id=bdrc_scan_id,
        config=config,
    )
