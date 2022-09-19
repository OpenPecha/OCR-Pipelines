from pathlib import Path

from src.config import ImportConfig
from src.logger import Logger

def test_ocr_status_logger():
    valid_work_id = "W0001"
    invalid_work_id = "W0002"
    ocr_complete_log_msg = f"{valid_work_id} OCR successfully completed"
    ocr_failed_log_msg = f"{invalid_work_id} OCR failed"
    log_file_path = Path('./tests/data/ocr_worked.log')

    logger = Logger(log_file_path=log_file_path)
    logger.ocr_status(work_id=valid_work_id, is_completed=True)
    logger.ocr_status(work_id=invalid_work_id, is_completed=False)
    log_lines = log_file_path.read_text(encoding='utf-8').splitlines()
    

    assert ocr_complete_log_msg in log_lines[0]
    assert ocr_failed_log_msg in log_lines[1]

    log_file_path.unlink()


def test_opf_published_status_logger():
    valid_work_id = "W0001"
    invalid_work_id = "W0002"
    opf_published_log_msg = f"{valid_work_id} OPF successfully published"
    opf_published_failed_log_msg = f"{invalid_work_id} OPF failed to publish"
    log_file_path = Path('./tests/data/opf_publish.log')

    logger = Logger(log_file_path=log_file_path)
    logger.opf_publish_status(work_id=valid_work_id, is_published=True)
    logger.opf_publish_status(work_id=invalid_work_id, is_published=False)
    log_lines = log_file_path.read_text(encoding='utf-8').splitlines()
    

    assert opf_published_log_msg in log_lines[0]
    assert opf_published_failed_log_msg in log_lines[1]

    log_file_path.unlink()


def test_opf_reimport_status_logger():
    valid_work_id = "W0001"
    invalid_work_id = "W0002"
    opf_reimport_log_msg = f"{valid_work_id} reimported successfully"
    opf_reimport_failed_log_msg = f"{invalid_work_id} reimport failed"
    log_file_path = Path('./tests/data/reimport_opf.log')

    logger = Logger(log_file_path=log_file_path)
    logger.opf_reimport_status(pecha_id=valid_work_id, is_reimported=True)
    logger.opf_reimport_status(pecha_id=invalid_work_id, is_reimported=False)
    log_lines = log_file_path.read_text(encoding='utf-8').splitlines()
    

    assert opf_reimport_log_msg in log_lines[0]
    assert opf_reimport_failed_log_msg in log_lines[1]

    log_file_path.unlink()