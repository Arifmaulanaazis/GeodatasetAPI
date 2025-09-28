"""
Custom exceptions for the GeoDataset API.
"""


class GeoDatasetError(Exception):
    """Base exception for GeoDataset API errors."""
    pass


class GeoAPIError(GeoDatasetError):
    """Exception raised for API-related errors."""

    def __init__(self, message, status_code=None, response_text=None):
        super().__init__(message)
        self.status_code = status_code
        self.response_text = response_text


class GeoFTPError(GeoDatasetError):
    """Exception raised for FTP-related errors."""

    def __init__(self, message, ftp_code=None):
        super().__init__(message)
        self.ftp_code = ftp_code


class GeoParseError(GeoDatasetError):
    """Exception raised for XML/JSON parsing errors."""

    def __init__(self, message, data=None):
        super().__init__(message)
        self.data = data


class GeoValidationError(GeoDatasetError):
    """Exception raised for data validation errors."""

    def __init__(self, message, field=None, value=None):
        super().__init__(message)
        self.field = field
        self.value = value
