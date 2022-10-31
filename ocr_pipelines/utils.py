import requests

from ocr_pipelines.exceptions import RequestFailedError


def requests_get_json(url):
    r = requests.get(url)
    if r.status_code != 200:
        raise RequestFailedError()
    return r.json()
