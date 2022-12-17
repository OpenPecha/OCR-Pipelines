from pathlib import Path
from unittest import mock

import pytest

from ocr_pipelines.exceptions import BdcrScanNotFound
from ocr_pipelines.image_downloader import BDRCImageDownloader


def test_download(tmp_path):
    # arrange
    bdrc_scan_id = "W1KG12429"
    downloader = BDRCImageDownloader(
        bdrc_scan_id=bdrc_scan_id, output_dir=Path(tmp_path)
    )

    # mocks
    downloader.save_img_group = mock.MagicMock()  # type: ignore
    downloader.get_img_groups = mock.MagicMock(  # type: ignore
        return_value=[("I00KG09835", "I00KG09835")]
    )

    # act
    output_path = downloader.download()

    # assert
    img_group_dir = output_path / "I00KG09835"
    assert output_path.is_dir()
    assert img_group_dir.is_dir()
    assert downloader.get_img_groups.call_count == 1
    assert downloader.save_img_group.call_count == 1
    assert downloader.save_img_group.call_args == mock.call(
        "I00KG09835", "I00KG09835", img_group_dir
    )


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
