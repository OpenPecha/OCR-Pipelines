import requests
from google.oauth2.service_account import Credentials

from ocr_pipelines.exceptions import RequestFailedError


def requests_get_json(url):
    r = requests.get(url)
    if r.status_code != 200:
        raise RequestFailedError()
    return r.json()


def check_google_server_account_key_format(credentials_dict: dict) -> bool:
    try:
        Credentials.from_service_account_info(credentials_dict)
    except ValueError:
        return False
    return True
