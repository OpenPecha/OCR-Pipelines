class Error(Exception):
    """Base-class for all exceptions raised by the package"""


class ParserError(Error):
    """Base-class for parser errors."""


class OcrEngineError(Error):
    """Base-class for OCR engine errors."""


class OcrExecutorError(Error):
    """Base-class for OCR executor errors."""


class ImageDownloaderError(Error):
    """Base-class for image downloader errors."""


class PipelineError(Error):
    """Base-class for pipeline errors."""


class OCREngineNotSupported(OcrEngineError):
    """Specified OCR engine is not supported."""


class GoogleVisionEngineError(OcrEngineError):
    """Base-class for GoogleVisionEngine errors."""


class GoogleVisionCredentialsError(GoogleVisionEngineError):
    """Invalid credentials for Google Vision API."""


class BdcrScanNotFound(ImageDownloaderError):
    """A provided BDRC scan id is not found."""


class ImageGroupNotFound(ImageDownloaderError):
    """A provided bdrc imagegroup is not found."""


class DataProviderNotSupported(ParserError):
    pass


class RequestFailedError(Exception):
    pass
