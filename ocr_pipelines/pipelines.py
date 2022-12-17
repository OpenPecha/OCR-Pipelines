import tempfile

from openpecha.core.pecha import OpenPechaFS
from openpecha.utils import download_pecha_assets

from ocr_pipelines.config import ImportConfig, ReimportConfig
from ocr_pipelines.executor import OCRExecutor
from ocr_pipelines.image_downloader import BDRCImageDownloader
from ocr_pipelines.metadata import Metadata
from ocr_pipelines.parser import OCRParser
from ocr_pipelines.update_pecha import update_pecha
from ocr_pipelines.upload import BdrcS3Uploader


def import_pipeline(bdrc_scan_id: str, config: ImportConfig, metadata: Metadata):
    """Pipeline for importing ocred pecha to opf

    Args:
        bdrc_scan_id (str): bdrc scan id
        config (ImportConfig): import config object
    """

    downloader = BDRCImageDownloader(
        bdrc_scan_id=bdrc_scan_id, output_dir=config.images_path
    )
    saved_images_dir = downloader.download()

    ocr_executor = OCRExecutor(config=config, image_download_dir=saved_images_dir)
    ocr_output_path = ocr_executor.run()

    with tempfile.TemporaryDirectory() as tmpdirname:
        ocr_parser = OCRParser(
            config=config, ocr_output_path=ocr_output_path, opf_dir=tmpdirname
        )
        pecha = ocr_parser.parse()

        uploader = BdrcS3Uploader(bdrc_scan_id=bdrc_scan_id, service=config.ocr_engine)
        uploader.upload(
            ocr_images_path=saved_images_dir,
            ocr_outputs_path=ocr_output_path,
            metadata=metadata.to_dict(),
        )

        pecha.publish(asset_path=ocr_output_path, asset_name="ocr_output")


def reimport_pipeline(pecha_id: str, config: ReimportConfig):
    """Pipeline to reimport ocr pecha to opf incase of update in opf parser

    Args:
        pecha_id (str): pecha id
        config (ReimportConfig): Reimport config object
    """

    ocr_output_path = download_pecha_assets(
        pecha_id, asset_type="ocr_output", download_dir=config.ocr_outputs_path
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
