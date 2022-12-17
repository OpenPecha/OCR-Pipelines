from pathlib import Path
from unittest import mock

import pytest

from ocr_pipelines.exceptions import BdcrScanNotFound
from ocr_pipelines.image_downloader import BDRCImageDownloader


@mock.patch("ocr_pipelines.image_downloader.buda_api.get_buda_scan_info")
def test_get_imagegroups_for_valid_bdrc_scan_id(mock_get_buda_scan_info):
    # arrange
    bdrc_scan_id = "valid-bdrc-scan-id"
    mock_get_buda_scan_info.return_value = {"image_groups": {"I00KG09835": {}}}
    imgdownloader = BDRCImageDownloader(
        bdrc_scan_id=bdrc_scan_id, output_dir=Path("/tmp")
    )

    # act
    images_group = list(imgdownloader.get_img_groups())

    # assert
    assert images_group == [("I00KG09835", "I00KG09835")]


@mock.patch("ocr_pipelines.image_downloader.buda_api.get_buda_scan_info")
def test_get_img_groups_for_invalid_bdrc_scan_id(mock_get_buda_scan_info):
    # arrange
    bdrc_scan_id = "fake-bdrc-scan-id"
    mock_get_buda_scan_info.return_value = None
    image_downloader = BDRCImageDownloader(
        bdrc_scan_id=bdrc_scan_id, output_dir=Path("/tmp")
    )

    # act and assert
    with pytest.raises(BdcrScanNotFound):
        list(image_downloader.get_img_groups())
