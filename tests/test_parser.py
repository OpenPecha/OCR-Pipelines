from src.config import BaseConfig
from src.parser import OCRParser

def test_ocr_parser():
    config = BaseConfig(formatter_type="google_vision")
    ocr_output_path = "./tests/data/google_vision/ocr_output/"
    opf_dir = "./tests/data/google_vision/opfs/"
    pecha_id = "I123456"

    parser = OCRParser(config=config, ocr_output_path=ocr_output_path, opf_dir=opf_dir, pecha_id=pecha_id)

    assert parser.config == config
    assert parser.ocr_output_path == ocr_output_path
    assert parser.opf_dir == opf_dir
    assert parser.pecha_id == pecha_id


# def test_google_parser():
#     config = BaseConfig(formatter_type="google_vision")
#     ocr_output_path = "./tests/data/google_vision/ocr_output/"
#     opf_dir = "./tests/data/google_vision/opfs/"
#     pecha_id = "I123456"


#     parser = OCRParser(config=config, ocr_output_path=ocr_output_path, opf_dir=opf_dir, pecha_id=pecha_id)
#     opf_path = parser.parse()
    
#     assert opf_path == f"{opf_dir}/{pecha_id}" 