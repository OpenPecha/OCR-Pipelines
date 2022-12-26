from pathlib import Path
from typing import Union

from openpecha.core import ids
from openpecha.core.pecha import OpenPechaGitRepo
from openpecha.formatters.ocr.google_vision import (
    GoogleVisionBDRCFileProvider,
    GoogleVisionFormatter,
)
from openpecha.formatters.ocr.hocr import BDRCGBFileProvider, HOCRFormatter

from ocr_pipelines.config import ImportConfig, ReimportConfig
from ocr_pipelines.engines import GoogleVisionEngine
from ocr_pipelines.exceptions import DataProviderNotSupported, OCREngineNotSupported
from ocr_pipelines.metadata import Metadata

ConfigType = Union[ImportConfig, ReimportConfig]

PARSERS_REGISTER = {
    GoogleVisionEngine.__name__: GoogleVisionFormatter,
    "hocr": HOCRFormatter,
}

DATA_PROVIDER_REGISTER = {
    GoogleVisionEngine.__name__: GoogleVisionBDRCFileProvider,
    "hocr": BDRCGBFileProvider,
}


class OCRParser:
    def __init__(
        self,
        config: ConfigType,
        ocr_output_path: Path,
        output_path: Path,
        metadata: Metadata,
        pecha_id: str = None,
        parsers_register: dict = PARSERS_REGISTER,
        data_provider_register: dict = DATA_PROVIDER_REGISTER,
    ) -> None:
        self.config = config
        self.ocr_output_path = ocr_output_path
        self.output_path = output_path
        self.parsers_register = parsers_register
        self.data_provider_register = data_provider_register
        self.metadata = metadata
        self.pecha_id = pecha_id or ids.get_initial_pecha_id()

    @property
    def opf_path(self) -> Path:
        opf_path = self.output_path / self.pecha_id / f"{self.pecha_id}.opf"
        opf_path.mkdir(parents=True, exist_ok=True)
        return opf_path

    def get_ocr_import_info(self):
        return self.metadata.to_dict()

    def parse(self) -> OpenPechaGitRepo:
        try:
            formatter_class = self.parsers_register[self.config.ocr_engine]
        except Exception:
            raise OCREngineNotSupported(
                f"{self.config.ocr_engine} not supported. Please select from {self.parsers_register.keys()}"
            )
        try:
            data_provider_class = self.data_provider_register[self.config.ocr_engine]
        except Exception:
            raise DataProviderNotSupported(
                f"{self.config.ocr_engine} not supported. Please select from {self.data_provider_register.keys()}"
            )

        bdrc_scan_id = self.ocr_output_path.stem
        formatter = formatter_class(output_path=self.opf_path)
        data_provider = data_provider_class(
            bdrc_scan_id=bdrc_scan_id,
            ocr_import_info={},
            ocr_disk_path=self.ocr_output_path,
        )
        pecha = formatter.create_opf(
            data_provider=data_provider,
            pecha_id=self.pecha_id,
            ocr_import_info=self.get_ocr_import_info(),
        )
        pecha.__class__ = OpenPechaGitRepo
        pecha.storage = None
        pecha.meta.id = self.pecha_id
        pecha.save_meta()
        return pecha
