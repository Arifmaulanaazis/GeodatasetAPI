"""
Utility functions for the GeoDataset API.
"""

import xml.etree.ElementTree as ET
from typing import Dict, List, Optional, Any
import re
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
import logging
from .exceptions import GeoParseError, GeoValidationError

logger = logging.getLogger(__name__)


def parse_xml_response(xml_text: str) -> Dict[str, Any]:
    """
    Parse XML response from NCBI E-Utils.

    Args:
        xml_text: Raw XML response text

    Returns:
        Dictionary representation of the XML

    Raises:
        GeoParseError: If XML parsing fails
    """
    try:
        root = ET.fromstring(xml_text)

        def xml_to_dict(element):
            """Convert XML element to dictionary."""
            if len(element) == 0:
                return element.text or ""

            result = {}
            for child in element:
                if child.tag in result:
                    # Handle multiple elements with same tag
                    if not isinstance(result[child.tag], list):
                        result[child.tag] = [result[child.tag]]
                    result[child.tag].append(xml_to_dict(child))
                else:
                    result[child.tag] = xml_to_dict(child)
            return result

        return xml_to_dict(root)

    except ET.ParseError as e:
        raise GeoParseError(f"Failed to parse XML response: {e}", xml_text)


def extract_uids_from_search(xml_dict: Dict[str, Any]) -> List[str]:
    """
    Extract UIDs from eSearch response.

    Args:
        xml_dict: Parsed XML response from eSearch

    Returns:
        List of UIDs as strings
    """
    id_list = xml_dict.get('IdList', {})
    if isinstance(id_list.get('Id'), list):
        return [str(uid) for uid in id_list['Id']]
    elif id_list.get('Id'):
        return [str(id_list['Id'])]
    return []


def build_search_url(base_url: str, db: str, term: str, **kwargs) -> str:
    """
    Build eSearch URL with proper parameters.

    Args:
        base_url: Base E-Utils URL
        db: Database name (e.g., 'gds', 'geoprofiles')
        term: Search term
        **kwargs: Additional parameters

    Returns:
        Complete URL for eSearch
    """
    params = {
        'db': db,
        'term': term,
        'retmax': kwargs.get('retmax', 1000),
        'usehistory': kwargs.get('usehistory', 'y')
    }

    # Add optional parameters
    for key, value in kwargs.items():
        if key not in ['retmax', 'usehistory']:
            params[key] = value

    return f"{base_url}/esearch.fcgi?{urlencode(params)}"


def build_summary_url(base_url: str, db: str, **kwargs) -> str:
    """
    Build eSummary URL with proper parameters.

    Args:
        base_url: Base E-Utils URL
        db: Database name
        **kwargs: Parameters like query_key, WebEnv, id, etc.

    Returns:
        Complete URL for eSummary
    """
    params = {'db': db, 'version': '2.0'}

    # Add query parameters
    for key, value in kwargs.items():
        params[key] = value

    return f"{base_url}/esummary.fcgi?{urlencode(params)}"


def build_fetch_url(base_url: str, db: str, **kwargs) -> str:
    """
    Build eFetch URL with proper parameters.

    Args:
        base_url: Base E-Utils URL
        db: Database name
        **kwargs: Parameters like query_key, WebEnv, id, etc.

    Returns:
        Complete URL for eFetch
    """
    params = {'db': db}

    # Add query parameters
    for key, value in kwargs.items():
        params[key] = value

    return f"{base_url}/efetch.fcgi?{urlencode(params)}"


def build_link_url(base_url: str, dbfrom: str, db: str, **kwargs) -> str:
    """
    Build eLink URL with proper parameters.

    Args:
        base_url: Base E-Utils URL
        dbfrom: Source database
        db: Target database
        **kwargs: Additional parameters

    Returns:
        Complete URL for eLink
    """
    params = {'dbfrom': dbfrom, 'db': db}

    # Add query parameters
    for key, value in kwargs.items():
        params[key] = value

    return f"{base_url}/elink.fcgi?{urlencode(params)}"


def parse_date_range(date_range: str) -> tuple:
    """
    Parse date range string in format YYYY/MM/DD:YYYY/MM/DD.

    Args:
        date_range: Date range string

    Returns:
        Tuple of (start_date, end_date)
    """
    try:
        start, end = date_range.split(':')
        return start.strip(), end.strip()
    except ValueError:
        raise GeoValidationError("Invalid date range format. Use 'YYYY/MM/DD:YYYY/MM/DD'")


def validate_accession(accession: str) -> bool:
    """
    Validate GEO accession format.

    Args:
        accession: GEO accession (e.g., GSE12345, GPL123, GSM123)

    Returns:
        True if valid format
    """
    # GSE/GDS/GPL/GSM followed by digits
    pattern = r'^G(PL|SE|DS|SM)\d+$'
    return bool(re.match(pattern, accession.upper()))


def format_ftp_path(accession: str, data_type: str = 'series') -> str:
    """
    Generate FTP path for GEO data.

    Args:
        accession: GEO accession
        data_type: Type of data ('series', 'platform', 'sample', 'dataset')

    Returns:
        FTP path
    """
    accession = accession.upper()

    if not validate_accession(accession):
        raise GeoValidationError(f"Invalid accession format: {accession}")

    prefix = accession[:3]  # GSE, GPL, etc.
    number = accession[3:]  # The number part

    # Create the 'nnn' pattern
    if len(number) >= 3:
        nnn_pattern = number[:-3] + 'nnn'
    else:
        nnn_pattern = 'nnn'

    if data_type == 'series' and prefix == 'GSE':
        return f"/geo/series/GSE{nnn_pattern}/GSE{number}/"
    elif data_type == 'platform' and prefix == 'GPL':
        return f"/geo/platforms/GPL{nnn_pattern}/GPL{number}/"
    elif data_type == 'sample' and prefix == 'GSM':
        return f"/geo/samples/GSM{nnn_pattern}/GSM{number}/"
    elif data_type == 'dataset' and prefix == 'GDS':
        return f"/geo/datasets/GDS{nnn_pattern}/GDS{number}/"
    else:
        raise GeoValidationError(f"Unsupported combination: {prefix} with {data_type}")
