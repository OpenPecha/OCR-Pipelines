from pathlib import Path
from unittest import mock

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
    ocr_images_imagegroup_dir = uploader.get_imagegroup_dir(
        uploader.s3_ocr_images_dir, imagegroup
    )
    ocr_outputs_imagegroup_dir = uploader.get_imagegroup_dir(
        uploader.s3_ocr_outputs_dir, imagegroup
    )

    # assert
    assert ocr_images_imagegroup_dir == Path(
        "Works/67/W1KG12345/google-vision/batch-1/images/W1KG12345-1234"
    )
    assert ocr_outputs_imagegroup_dir == Path(
        "Works/67/W1KG12345/google-vision/batch-1/output/W1KG12345-1234"
    )


@pytest.fixture(scope="module")
def uploader():
    bdrc_scan_id = "W1KG12345"
    service = "google-vision"
    batch = "batch-1"
    return BdrcS3Uploader(bdrc_scan_id, service, batch)


@pytest.fixture(scope="function")
def ocr_images_or_outputs_dir(tmp_path):
    bdrc_scan_id = "W1KG12345"
    imagegroup = "I1234"
    bdrc_scan_ocr_output_dir = tmp_path / bdrc_scan_id
    local_imagegroup_dir = bdrc_scan_ocr_output_dir / imagegroup
    local_imagegroup_dir.mkdir(parents=True, exist_ok=True)
    ocr_output_fn = local_imagegroup_dir / "ocr_output.json"
    ocr_output_fn.write_bytes(b"{}")
    return bdrc_scan_ocr_output_dir


def test_upload_ocr_images(uploader, ocr_images_or_outputs_dir):
    # arrange
    ocr_images_dir = ocr_images_or_outputs_dir
    uploader.bucket.put_object = mock.MagicMock()

    # act
    uploader.upload_ocr_images(ocr_images_dir)

    # assert
    assert uploader.bucket.put_object.call_count == 1
    assert uploader.bucket.put_object.call_args == mock.call(
        Key="Works/67/W1KG12345/google-vision/batch-1/images/W1KG12345-1234/ocr_output.json",
        Body=b"{}",
    )


def test_upload_ocr_outputs(uploader, ocr_images_or_outputs_dir):
    # arrange
    ocr_outputs_dir = ocr_images_or_outputs_dir
    uploader.bucket = mock.MagicMock()

    # act
    uploader.upload_ocr_outputs(ocr_outputs_dir)

    # assert
    assert uploader.bucket.put_object.call_count == 1


def test_upload_metadata(uploader):
    # arrange
    uploader.bucket = mock.MagicMock()
    fake_metadata = {"fake": "metadata"}

    # act
    uploader.upload_metadata(fake_metadata)

    # assert
    assert uploader.bucket.put_object.call_count == 1


def test_upload(uploader, ocr_images_or_outputs_dir):
    # arrange
    ocr_images_dir = ocr_images_or_outputs_dir
    ocr_outputs_dir = ocr_images_or_outputs_dir
    uploader.upload_ocr_images = mock.MagicMock()
    uploader.upload_ocr_outputs = mock.MagicMock()
    uploader.upload_metadata = mock.MagicMock()

    fake_metadata = {"fake": "metadata"}

    # act
    uploader.upload(
        ocr_images_path=ocr_images_dir,
        ocr_outputs_path=ocr_outputs_dir,
        metadata=fake_metadata,
    )

    # assert
    assert uploader.upload_ocr_images.call_count == 1
    assert uploader.upload_ocr_outputs.call_count == 1
    assert uploader.upload_metadata.call_count == 1
