from pathlib import Path

import pytest

from ocr_pipelines.upload import BdrcS3Uploader


def test_get_frist_two_chars_hash():
    # arrange
    bdrc_scan_id = "W1KG12345"
    service = "google-vision"
    batch = "batch-1"
    uploader = BdrcS3Uploader(bdrc_scan_id, service, batch)

    # act
    bdrc_scan_id_hash = uploader._BdrcS3Uploader__get_first_two_chars_hash(bdrc_scan_id)  # type: ignore

    # assert
    assert bdrc_scan_id_hash == "67"


@pytest.mark.parametrize(
    "imagegroup, expected",
    [
        ("I1234", "1234"),
        ("I12345", "I12345"),
        ("I1PD95878", "I1PD95878"),
    ],
)
def test_get_s3_suffix_for_imagegroup(imagegroup, expected):
    # arrange
    bdrc_scan_id = "W1KG12345"
    service = "google-vision"
    batch = "batch-1"
    uploader = BdrcS3Uploader(bdrc_scan_id, service, batch)

    # act
    s3_suffix = uploader._BdrcS3Uploader__get_s3_suffix_for_imagegroup(imagegroup)  # type: ignore

    # assert
    assert s3_suffix == expected


def test_base_dir():
    # arrange
    bdrc_scan_id = "W1KG12345"
    service = "google-vision"
    batch = "batch-1"
    uploader = BdrcS3Uploader(bdrc_scan_id, service, batch)

    # act
    base_dir = uploader.base_dir

    # assert
    assert base_dir == Path("Works/67/W1KG12345/google-vision/batch-1")


def test_imagegroup_dir():
    # arrange
    bdrc_scan_id = "W1KG12345"
    service = "google-vision"
    batch = "batch-1"
    imagegroup = "I1234"
    uploader = BdrcS3Uploader(bdrc_scan_id, service, batch)

    # act
    imagegroup_dir = uploader.get_imagegroup_dir(imagegroup)

    # assert
    assert imagegroup_dir == Path(
        "Works/67/W1KG12345/google-vision/batch-1/W1KG12345-1234"
    )
