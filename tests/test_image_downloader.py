from pathlib import Path
from unittest import mock

from ocr_pipelines.image_downloader import BDRCImageDownloader


@mock.patch("ocr_pipelines.image_downloader.requests_get_json")
def test_get_imagegroups(mock_get_json):
    bdrc_scan_id = "fake-bdrc-scan-id"
    output_dir = Path("/tmp")
    mock_get_json.return_value = {
        "results": {
            "bindings": [
                {
                    "volid": {
                        "value": "http://purl.bdrc.io/resource/I00KG09835",
                    },
                }
            ]
        }
    }

    imgdownloader = BDRCImageDownloader(
        bdrc_scan_id=bdrc_scan_id, output_dir=output_dir
    )

    images_group = list(imgdownloader.get_imggroups())

    assert images_group == [("I00KG09835", "bdr:I00KG09835")]
