import logging


from src.config import BaseConfig

class Logger:
    
    def __init__(self, config: BaseConfig, log_file_path: str) -> None:
        self.config = config
        self.log_file_path = log_file_path
        if self.config.__class__.__name__ == "ImportConfig":
            self.logger = logging.getLogger()
            self.logger.setLevel(logging.INFO)
            fileHandler = logging.FileHandler(self.log_file_path)
            fileHandler.setLevel(logging.INFO)
            formatter = logging.Formatter("%(asctime)s, %(levelname)s: %(message)s")
            fileHandler.setFormatter(formatter)
            self.logger.addHandler(fileHandler)

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


    # def error(self, msg, extra=None):
    #     self.logger.error(msg, extra=extra)

    # def debug(self, msg, extra=None):
    #     self.logger.debug(msg, extra=extra)

    # def warning(self, work_id, extra=None):
    #     self.logger.warning(f'{work_id} OCR failed', extra=extra)