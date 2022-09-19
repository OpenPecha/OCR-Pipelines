from pathlib import Path

from src.config import ImportConfig
from src.logger import Logger

def test_ocr_status_logger():
    valid_work_id = "W0001"
    invalid_work_id = "W0002"
    import_config = ImportConfig(ocr_engine='google_ocr')
    ocr_complete_log_msg = f"{valid_work_id} OCR successfully completed"
    ocr_failed_log_msg = f"{invalid_work_id} OCR failed"
    log_file_path = Path('./tests/data/ocr_worked.log')

    logger = Logger(config=import_config, log_file_path=log_file_path)
    logger.ocr_status(work_id=valid_work_id, is_completed=True)
    logger.ocr_status(work_id=invalid_work_id, is_completed=False)
    log_lines = log_file_path.read_text(encoding='utf-8').splitlines()
    

    assert logger.config == import_config
    assert ocr_complete_log_msg in log_lines[0]
    assert ocr_failed_log_msg in log_lines[1]

    log_file_path.unlink()

