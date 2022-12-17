from pathlib import Path
from unittest import mock

import pytest

from ocr_pipelines.exceptions import BdcrScanNotFound
from ocr_pipelines.image_downloader import BDRCImageDownloader


@pytest.mark.skip(reason="required interent connection")
def test_download(tmp_path):
    # arrange
    bdrc_scan_id = "W1KG12429"
    downloader = BDRCImageDownloader(
        bdrc_scan_id=bdrc_scan_id, output_dir=Path(tmp_path)
    )

    # act
    output_path = downloader.download()

    # assert
    assert output_path.is_dir()


def test_download_unittest(tmp_path):
    # arrange
    bdrc_scan_id = "W1KG12429"
    downloader = BDRCImageDownloader(
        bdrc_scan_id=bdrc_scan_id, output_dir=Path(tmp_path)
    )

    # mocks
    downloader.save_img_group = mock.MagicMock()  # type: ignore
    downloader.get_img_groups = mock.MagicMock(  # type: ignore
        return_value=["I00KG09835"]
    )

    # act
    output_path = downloader.download()

    # assert
    img_group_dir = output_path / "I00KG09835"
    assert output_path.is_dir()
    assert img_group_dir.is_dir()
    assert downloader.get_img_groups.call_count == 1
    assert downloader.save_img_group.call_count == 1
    assert downloader.save_img_group.call_args == mock.call("I00KG09835", img_group_dir)


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
    assert images_group == ["I00KG09835"]


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


@mock.patch("ocr_pipelines.image_downloader.buda_api.gets3blob")
@mock.patch("ocr_pipelines.image_downloader.buda_api.get_s3_folder_prefix")
def test_save_img_group(mock_get_s3_folder_prefix, mock_gets3blob):
    # arrange
    bdrc_scan_id = "W1KG12429"
    img_group = "I00KG09835"
    img_fn = "I00KG098350001.tif"
    downloader = BDRCImageDownloader(bdrc_scan_id=bdrc_scan_id, output_dir=Path("/tmp"))

    # mocks
    mock_gets3blob.return_value = b"fake-image-content"
    mock_get_s3_folder_prefix.return_value = f"{bdrc_scan_id}/{img_group}"
    downloader.get_s3_img_list = mock.MagicMock(return_value=[img_fn])  # type: ignore
    downloader.save_img = mock.MagicMock()  # type: ignore

    # act
    downloader.save_img_group(img_group, Path("/tmp"))

    # assert
    downloader.get_s3_img_list.assert_called_once_with(img_group)
    downloader.save_img.assert_called_once_with(
        b"fake-image-content", "I00KG098350001.tif", Path("/tmp")
    )
    mock_gets3blob.assert_called_once_with(f"{bdrc_scan_id}/{img_group}/{img_fn}")


@mock.patch("ocr_pipelines.image_downloader.buda_api.get_image_list_s3")
def test_get_s3_img_list(mock_get_image_list_s3):
    # arrange
    bdrc_scan_id = "W1KG12429"
    img_group = "I00KG09835"
    img_fn = "I00KG098350001.tif"
    downloader = BDRCImageDownloader(bdrc_scan_id=bdrc_scan_id, output_dir=Path("/tmp"))
    # mocks
    mock_get_image_list_s3.return_value = [{"filename": img_fn}]

    # act
    images = list(downloader.get_s3_img_list(img_group))

    assert images == [img_fn]
    mock_get_image_list_s3.assert_called_once_with(bdrc_scan_id, img_group)


def test_save_img(tmp_path):
    # arrange
    bdrc_scan_id = "W1KG12429"
    img_group_dir = Path(tmp_path) / bdrc_scan_id / "I00KG09835"
    img_group_dir.mkdir(parents=True)
    img_fn = "I00KG098350001.tif"

    img_path = Path("tests/data/images/tiff_image.tif")
    img_fp = img_path.open("rb")

    output_dir = Path(tmp_path)
    downloader = BDRCImageDownloader(bdrc_scan_id="W1KG124", output_dir=output_dir)

    # act
    downloader.save_img(img_fp, img_fn, img_group_dir)  # type: ignore

    # assert
    saved_img_path = img_group_dir / f"{Path(img_fn).stem}.png"
    assert saved_img_path.is_file()
