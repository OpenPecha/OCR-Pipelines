import tempfile

from pathlib import Path

from ocr_pipelines.image_downloader import BDRCImageDownloader

def mock_get_image_groups():
    return {'I0001': 'wwww.google.com'}


class MockDownloader:

    def __init__(self, work_id: str, output_dir : Path()) -> None:
        pass

    def download_images():
        return Path.home()

def test_image_downloader():
    work_id = "W0001"
    
    with tempfile.TemporaryDirectory() as tmpdirname:
        output_dir = Path(tmpdirname)
        image_downloader = BDRCImageDownloader(work_id=work_id, output_dir=output_dir)

        image_output_path = image_downloader.download_images()

        assert isinstance(image_output_path, Path)