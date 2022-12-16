from pathlib import Path
from unittest import mock

import pytest

from ocr_pipelines.exceptions import FailedToAssignBatchError
from ocr_pipelines.upload import BdrcS3Uploader


@pytest.fixture(scope="module")
def uploader():
    bdrc_scan_id = "W1KG12345"
    service = "google-vision"
    return BdrcS3Uploader(bdrc_scan_id, service)


def test_get_frist_two_chars_hash(uploader):
    # arrange
    bdrc_scan_id = "W1KG12345"

    # act
    bdrc_scan_id_hash = uploader._BdrcS3Uploader__get_first_two_chars_hash(bdrc_scan_id)

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
def test_get_s3_suffix_for_imagegroup(uploader, imagegroup, expected):
    # act
    s3_suffix = uploader._BdrcS3Uploader__get_s3_suffix_for_imagegroup(imagegroup)

    # assert
    assert s3_suffix == expected


def test_s3_dir_exists_False(uploader):
    # arrange
    uploader.client.list_objects_v2 = mock.MagicMock(return_value={"KeyCount": 0})

    # act
    dir_exits = uploader._BdrcS3Uploader__s3_dir_exists(Path("fake-path"))

    # assert
    assert not dir_exits
    assert uploader.client.list_objects_v2.call_count == 1
    assert uploader.client.list_objects_v2.call_args == mock.call(
        Bucket=uploader.bucket_name, Prefix="fake-path", MaxKeys=1
    )


def test_s3_dir_exists_True(uploader):
    # arrange
    uploader.client.list_objects_v2 = mock.MagicMock(return_value={"KeyCount": 1})

    # act
    dir_exits = uploader._BdrcS3Uploader__s3_dir_exists(Path("fake-path"))

    # assert
    assert dir_exits
    assert uploader.client.list_objects_v2.call_count == 1
    assert uploader.client.list_objects_v2.call_args == mock.call(
        Bucket=uploader.bucket_name, Prefix="fake-path", MaxKeys=1
    )


def test_get_available_batch_id(uploader):
    # arrange
    uploader._BdrcS3Uploader__s3_dir_exists = mock.MagicMock(return_value=False)

    # act
    batch_id = uploader._BdrcS3Uploader__get_available_batch_id()

    # assert
    assert batch_id
    assert batch_id.startswith("batch-")
    assert len(batch_id) == 10
    assert uploader._BdrcS3Uploader__s3_dir_exists.call_count == 1
    assert uploader._BdrcS3Uploader__s3_dir_exists.call_args == mock.call(
        Path(f"Works/67/W1KG12345/google-vision/{batch_id}")
    )


def test_get_available_batch_id_cannot_find_id(uploader):
    # arrange
    uploader._BdrcS3Uploader__s3_dir_exists = mock.MagicMock(return_value=True)

    # act
    with pytest.raises(FailedToAssignBatchError):
        uploader._BdrcS3Uploader__get_available_batch_id(n_iter=1)


def test_base_dir():
    # arrange
    bdrc_scan_id = "W1KG12345"
    service = "google-vision"
    uploader = BdrcS3Uploader(bdrc_scan_id, service)

    # act
    base_dir = uploader.base_dir

    # assert
    assert base_dir == Path("Works/67/W1KG12345")


def test_service_dir():
    # arrange
    bdrc_scan_id = "W1KG12345"
    service = "google-vision"
    uploader = BdrcS3Uploader(bdrc_scan_id, service)

    # act
    service_dir = uploader.service_dir

    # assert
    assert service_dir == Path("Works/67/W1KG12345/google-vision")


def test_batch_dir():
    # arrange
    bdrc_scan_id = "W1KG12345"
    service = "google-vision"
    uploader = BdrcS3Uploader(bdrc_scan_id, service)
    uploader._batch = "batch-1"

    # act
    batch_dir = uploader.batch_dir

    # assert
    assert batch_dir == Path("Works/67/W1KG12345/google-vision/batch-1")


def test_imagegroup_dir():
    # arrange
    bdrc_scan_id = "W1KG12345"
    service = "google-vision"
    imagegroup = "I1234"
    uploader = BdrcS3Uploader(bdrc_scan_id, service)
    uploader._batch = "batch-1"

    # act
    imagegroup_dir = uploader.get_imagegroup_dir(imagegroup)

    # assert
    assert imagegroup_dir == Path(
        "Works/67/W1KG12345/google-vision/batch-1/W1KG12345-1234"
    )


@pytest.fixture(scope="function")
def bdrc_scan_ocr_output_dir(tmp_path):
    bdrc_scan_id = "W1KG12345"
    imagegroup = "I1234"
    bdrc_scan_ocr_output_dir = tmp_path / bdrc_scan_id
    local_imagegroup_dir = bdrc_scan_ocr_output_dir / imagegroup
    local_imagegroup_dir.mkdir(parents=True, exist_ok=True)
    ocr_output_fn = local_imagegroup_dir / "ocr_output.json"
    ocr_output_fn.write_bytes(b"{}")
    return bdrc_scan_ocr_output_dir


def test_upload_ocr_outputs(uploader, bdrc_scan_ocr_output_dir):
    # arrange
    uploader._batch = "batch-1"
    uploader.bucket = mock.MagicMock()

    # act
    uploader.upload_ocr_outputs(bdrc_scan_ocr_output_dir)

    # assert
    assert uploader.bucket.put_object.call_count == 1


def test_upload_metadata(uploader):
    # arrange
    uploader._batch = "batch-1"
    uploader.bucket = mock.MagicMock()
    fake_metadata = {"fake": "metadata"}

    # act
    uploader.upload_metadata(fake_metadata)

    # assert
    assert uploader.bucket.put_object.call_count == 1


def test_upload(uploader, bdrc_scan_ocr_output_dir):
    # arrange
    uploader._batch = "batch-1"
    uploader.bucket = mock.MagicMock()
    fake_metadata = {"fake": "metadata"}

    # act
    uploader.upload(bdrc_scan_ocr_output_dir, fake_metadata)

    # assert
    assert uploader.bucket.put_object.call_count == 2
