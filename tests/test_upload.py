import pytest

from ocr_pipelines.upload import (
    get_bdrc_scan_id_hash,
    get_s3_path_prefix,
    get_s3_suffix_for_imagegroup,
)


def test_get_bdrc_scan_id_hash():
    # arrange
    bdrc_scan_id = "W1KG12345"

    # act
    bdrc_scan_id_hash = get_bdrc_scan_id_hash(bdrc_scan_id)

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
    # act
    s3_suffix = get_s3_suffix_for_imagegroup(imagegroup)

    # assert
    assert s3_suffix == expected


def test_get_s3_path_prefix():
    # arrange
    bdrc_scan_id = "W1KG12345"
    imagegroup = "I1234"
    service = "google-vision"
    batch = "batch-1"

    # act
    s3_path_prefix = get_s3_path_prefix(bdrc_scan_id, imagegroup, service, batch)

    # assert
    assert s3_path_prefix == "Works/67/W1KG12345/google-vision/batch-1/W1KG12345-1234"
