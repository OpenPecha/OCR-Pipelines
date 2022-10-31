from pathlib import Path
from unittest import mock

import pytest

from ocr_pipelines.exceptions import BdcrScanNotFound, RequestFailedError
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

    images_group = list(imgdownloader.get_img_groups())

    assert images_group == [("I00KG09835", "bdr:I00KG09835")]


@mock.patch("ocr_pipelines.image_downloader.requests_get_json")
def test_get_img_groups_incorret_url(mock_get_json):
    bdrc_scan_id = "fake-bdrc-scan-id"
    mock_get_json.side_effect = RequestFailedError("Request failed")
    image_downloader = BDRCImageDownloader(
        bdrc_scan_id=bdrc_scan_id, output_dir=Path(".")
    )

    with pytest.raises(BdcrScanNotFound):
        list(image_downloader.get_img_groups())


@mock.patch("ocr_pipelines.image_downloader.requests_get_json")
def test_get_img_groups_empty_results(mock_get_json):
    bdrc_scan_id = "fake-bdrc-scan-id"

    mock_get_json.return_value = {"results": {"bindings": []}}
    image_downloader = BDRCImageDownloader(
        bdrc_scan_id=bdrc_scan_id, output_dir=Path(".")
    )

    with pytest.raises(BdcrScanNotFound):
        list(image_downloader.get_img_groups())
