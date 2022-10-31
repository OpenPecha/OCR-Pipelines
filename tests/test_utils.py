from unittest import mock

import pytest

from ocr_pipelines.exceptions import RequestFailedError
from ocr_pipelines.utils import requests_get_json


@mock.patch("ocr_pipelines.utils.requests.get")
def test_requests_get_json(mock_get):
    url = "https://fake-url"
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {"foo": "bar"}

    res = requests_get_json(url)

    assert isinstance(res, dict)
    assert res["foo"] == "bar"


@mock.patch("ocr_pipelines.utils.requests.get")
def test_requests_get_json_error(mock_get):
    url = "https://fake-url"
    mock_get.return_value.status_code = 404

    with pytest.raises(RequestFailedError):
        requests_get_json(url)
