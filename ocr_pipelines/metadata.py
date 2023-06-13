from datetime import datetime, timezone

from ocr_pipelines.config import ImportConfig


class Metadata:
    """Metadata for the OCR pipeline.

    Args:
        config (ImportConfig): The config used to run the OCR pipeline.
        ocr_pipeline_verison (str): The version of the OCR pipeline.
        sponsor (str): The sponsor of the OCR pipeline.
        sponsor_consent (bool, optional): Whether the sponsor has given consent to
            to use the OCR output on OpenPecha and BDRC. Defaults to False.
        **kwargs: Additional metadata to be added to the metadata.
    """

    def __init__(
        self,
        pipeline_config: ImportConfig,
        sponsor: str,
        sponsor_consent: bool = False,
        timestamp: str = None,
        batch_id: str = None,
        **kwargs,
    ):
        self.timestamp = timestamp or datetime.now(timezone.utc).isoformat()
        self.pipeline_config = pipeline_config
        self.sponsor = sponsor
        self.sponsor_consent = sponsor_consent
        self.batch_id = batch_id
        self.kwargs = kwargs

        for k, v in kwargs.items():
            setattr(self, k, v)

    def to_dict(self):
        return {
            "timestamp": self.timestamp,
            "batch_id": self.batch_id,
            "ocr_engine": self.pipeline_config.ocr_engine,
            "ocr_model_type": self.pipeline_config.model_type,
            "ocr_lang_hint": self.pipeline_config.lang_hint,
            "software_id": f"ocr-pipelines@v{self.pipeline_config.version}",
            "sponsor": self.sponsor,
            "sponsor_consent": self.sponsor_consent,
            **self.kwargs,
        }

    @classmethod
    def from_dict(cls, metadata_dict: dict) -> "Metadata":
        """Deserialize the metadata from a dictionary."""
        metadata_dict = metadata_dict.copy()
        metadata_dict["pipeline_config"] = ImportConfig(
            ocr_engine=metadata_dict["ocr_engine"],
            model_type=metadata_dict["ocr_model_type"],
            lang_hint=metadata_dict["ocr_lang_hint"],
        )
        del metadata_dict["ocr_engine"]
        del metadata_dict["ocr_model_type"]
        del metadata_dict["ocr_lang_hint"]
        return cls(**metadata_dict)
