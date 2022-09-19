import logging


from src.config import BaseConfig

class Logger:
    
    def __init__(self, log_file_path: str) -> None:
        self.log_file_path = log_file_path
        self.format = "%(asctime)s, %(levelname)s: %(message)s"
        self.formatter = logging.Formatter(self.format)
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)
        self.fileHandler = logging.FileHandler(self.log_file_path)
        self.fileHandler.setLevel(logging.INFO)
        self.fileHandler.setFormatter(self.formatter)
        self.logger.addHandler(self.fileHandler)


    def ocr_status(self, work_id, is_completed, extra=None):
        if is_completed:
            self.logger.info(f'{work_id} OCR successfully completed', extra=extra)
        else:
            self.logger.warning(f"{work_id} OCR failed", extra=extra)

    def opf_publish_status(self, work_id, is_published, extra=None):
        if is_published:
            self.logger.info(f'{work_id} OPF successfully published ', extra=extra)
        else:
            self.logger.warning(f"{work_id} OPF failed to publish", extra=extra)
    
    def opf_reimport_status(self, pecha_id, is_reimported, extra=None):
        if is_reimported:
            self.logger.info(f"{pecha_id} reimported successfully", extra=extra)
        else:
            self.logger.warning(f"{pecha_id} reimport failed", extra=extra)