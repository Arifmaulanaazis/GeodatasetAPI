"""
GeoDataset API - A Python library for accessing NCBI GEO datasets programmatically.

This library provides a clean interface to the NCBI GEO (Gene Expression Omnibus)
database using the Entrez Programming Utilities (E-Utils).

Main classes:
    - GeoClient: Main client for interacting with GEO database
    - GeoFTPClient: Client for downloading files from NCBI FTP
    - GeoSeries: Model for GEO Series records
    - GeoDataset: Model for GEO Dataset records
    - GeoSample: Model for GEO Sample records
    - GeoPlatform: Model for GEO Platform records
"""

__version__ = "1.0.0"
__author__ = "Arif Maulana Azis"

from .client import GeoClient
from .ftp import GeoFTPClient, download_geo_files
from .models import GeoSeries, GeoDataset, GeoSample, GeoPlatform, create_geo_record
from .exceptions import GeoDatasetError, GeoAPIError, GeoFTPError, GeoValidationError
from .utils import validate_accession, format_ftp_path

__all__ = [
    "GeoClient",
    "GeoFTPClient",
    "download_geo_files",
    "GeoSeries",
    "GeoDataset",
    "GeoSample",
    "GeoPlatform",
    "create_geo_record",
    "validate_accession",
    "format_ftp_path",
    "GeoDatasetError",
    "GeoAPIError",
    "GeoFTPError",
    "GeoValidationError"
]
