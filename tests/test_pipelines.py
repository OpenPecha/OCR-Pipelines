import pytest

from ocr_pipelines.config import ImportConfig
from ocr_pipelines.pipelines import import_pipeline


def get_credentials():
    # import json
    # from pathlib import Path

    # credentials_path = Path.home() / ".gcloud" / "service_account_key.json"
    # return json.load(credentials_path.open())
    return {}


@pytest.mark.skip(reason="This test requires a Google Cloud account")
def test_import_pipeline():
    config = ImportConfig(
        ocr_engine="GoogleVisionEngine",
        model_type="builtin/stable",
        credentials=get_credentials(),
    )
    bdrc_scan_id = "W1KG12429"

    import_pipeline(bdrc_scan_id, config)
