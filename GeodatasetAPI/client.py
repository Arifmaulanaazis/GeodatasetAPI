"""
Main client for interacting with NCBI GEO database.
"""

import requests
from typing import Dict, List, Optional, Any, Union
import time
import logging
from urllib.parse import urlencode

from .utils import (
    parse_xml_response, extract_uids_from_search,
    build_search_url, build_summary_url, build_fetch_url, build_link_url,
    parse_date_range, validate_accession, format_ftp_path
)
from .models import GeoSeries, GeoDataset, GeoSample, GeoPlatform, GeoRecord, create_geo_record
from .exceptions import GeoAPIError, GeoParseError, GeoValidationError

logger = logging.getLogger(__name__)


class GeoClient:
    """
    Main client for accessing NCBI GEO database.

    This class provides methods to search, fetch, and download data from
    the NCBI GEO (Gene Expression Omnibus) database using the Entrez
    Programming Utilities (E-Utils).
    """

    BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

    def __init__(self, email: str = None, api_key: str = None,
                 rate_limit: float = 0.1):
        """
        Initialize the GEO client.

        Args:
            email: Email address for NCBI API (required for large requests)
            api_key: NCBI API key for higher rate limits
            rate_limit: Minimum seconds between requests (default: 0.1)
        """
        self.email = email
        self.api_key = api_key
        self.rate_limit = rate_limit
        self.last_request = 0.0
        self.session = requests.Session()

        # Set default headers
        self.session.headers.update({
            'User-Agent': f'GeoDatasetAPI/1.0 (email: {email or "not_provided"})'
        })

    def _make_request(self, url: str) -> str:
        """
        Make HTTP request with rate limiting and error handling.

        Args:
            url: Complete URL to request

        Returns:
            Response text

        Raises:
            GeoAPIError: If request fails
        """
        # Rate limiting
        now = time.time()
        time_since_last = now - self.last_request
        if time_since_last < self.rate_limit:
            time.sleep(self.rate_limit - time_since_last)

        self.last_request = time.time()

        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response.text

        except requests.RequestException as e:
            raise GeoAPIError(f"Request failed: {e}", response.status_code if hasattr(e, 'response') else None)

    def _add_api_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Add email and API key to parameters if available."""
        if self.email:
            params['email'] = self.email
        if self.api_key:
            params['api_key'] = self.api_key
        return params

    def search(self, db: str, term: str, retmax: int = 1000,
               usehistory: bool = True, **kwargs) -> Dict[str, Any]:
        """
        Search GEO database.

        Args:
            db: Database to search ('gds' or 'geoprofiles')
            term: Search term
            retmax: Maximum number of results
            usehistory: Whether to use history for pagination
            **kwargs: Additional search parameters

        Returns:
            Dictionary with search results including UIDs and WebEnv
        """
        params = self._add_api_params({
            'db': db,
            'term': term,
            'retmax': retmax,
            'usehistory': 'y' if usehistory else 'n',
            **kwargs
        })

        url = f"{self.BASE_URL}/esearch.fcgi?{urlencode(params)}"

        try:
            response_text = self._make_request(url)
            xml_dict = parse_xml_response(response_text)

            return {
                'uids': extract_uids_from_search(xml_dict),
                'count': int(xml_dict.get('Count', 0)),
                'query_key': xml_dict.get('QueryKey'),
                'web_env': xml_dict.get('WebEnv'),
                'translation_set': xml_dict.get('TranslationSet'),
                'raw_xml': response_text
            }

        except Exception as e:
            raise GeoAPIError(f"Search failed: {e}")

    def get_summary(self, db: str, uids: List[str] = None,
                   query_key: str = None, web_env: str = None,
                   version: str = "2.0") -> List[GeoRecord]:
        """
        Get summaries for GEO records.

        Args:
            db: Database name
            uids: List of UIDs to get summaries for
            query_key: Query key from previous search
            web_env: Web environment from previous search
            version: API version

        Returns:
            List of GEO record objects
        """
        if uids:
            id_param = ','.join(uids)
            params = self._add_api_params({
                'db': db,
                'id': id_param,
                'version': version
            })
        elif query_key and web_env:
            params = self._add_api_params({
                'db': db,
                'query_key': query_key,
                'WebEnv': web_env,
                'version': version
            })
        else:
            raise GeoValidationError("Either uids or query_key+web_env must be provided")

        url = f"{self.BASE_URL}/esummary.fcgi?{urlencode(params)}"

        try:
            response_text = self._make_request(url)
            xml_dict = parse_xml_response(response_text)

            records = []
            doc_sum_list = xml_dict.get('DocSum', [])

            if not isinstance(doc_sum_list, list):
                doc_sum_list = [doc_sum_list]

            for doc_sum in doc_sum_list:
                if not isinstance(doc_sum, dict):
                    continue

                # Extract basic info
                uid = doc_sum.get('Id', '')
                item_list = doc_sum.get('Item', [])

                # Parse items into a flat dictionary
                item_dict = {}
                if isinstance(item_list, list):
                    for item in item_list:
                        if isinstance(item, dict) and 'Name' in item and 'Value' in item:
                            item_dict[item['Name']] = item['Value']
                elif isinstance(item_list, dict):
                    item_dict = item_list

                # Create appropriate record type based on accession
                accession = item_dict.get('Accession', '')
                record = create_geo_record('', uid=uid, accession=accession, **item_dict)
                records.append(record)

            return records

        except Exception as e:
            raise GeoAPIError(f"Summary retrieval failed: {e}")

    def fetch(self, db: str, uids: List[str] = None,
              query_key: str = None, web_env: str = None,
              rettype: str = None, retmode: str = "text") -> str:
        """
        Fetch full records from GEO database.

        Args:
            db: Database name
            uids: List of UIDs to fetch
            query_key: Query key from previous search
            web_env: Web environment from previous search
            rettype: Return type
            retmode: Return mode ('text' or 'xml')

        Returns:
            Raw record data
        """
        if uids:
            id_param = ','.join(uids)
            params = self._add_api_params({
                'db': db,
                'id': id_param,
                'retmode': retmode
            })
            if rettype:
                params['rettype'] = rettype
        elif query_key and web_env:
            params = self._add_api_params({
                'db': db,
                'query_key': query_key,
                'WebEnv': web_env,
                'retmode': retmode
            })
            if rettype:
                params['rettype'] = rettype
        else:
            raise GeoValidationError("Either uids or query_key+web_env must be provided")

        url = f"{self.BASE_URL}/efetch.fcgi?{urlencode(params)}"

        try:
            return self._make_request(url)
        except Exception as e:
            raise GeoAPIError(f"Fetch failed: {e}")

    def link(self, dbfrom: str, db: str, uids: List[str] = None,
             query_key: str = None, web_env: str = None) -> List[Dict[str, Any]]:
        """
        Find linked records between databases.

        Args:
            dbfrom: Source database
            db: Target database
            uids: List of source UIDs
            query_key: Query key from previous search
            web_env: Web environment from previous search

        Returns:
            List of linked record information
        """
        if uids:
            id_param = ','.join(uids)
            params = self._add_api_params({
                'dbfrom': dbfrom,
                'db': db,
                'id': id_param
            })
        elif query_key and web_env:
            params = self._add_api_params({
                'dbfrom': dbfrom,
                'db': db,
                'query_key': query_key,
                'WebEnv': web_env
            })
        else:
            raise GeoValidationError("Either uids or query_key+web_env must be provided")

        url = f"{self.BASE_URL}/elink.fcgi?{urlencode(params)}"

        try:
            response_text = self._make_request(url)
            xml_dict = parse_xml_response(response_text)

            # Parse link results
            links = []
            link_set_list = xml_dict.get('LinkSet', [])

            if not isinstance(link_set_list, list):
                link_set_list = [link_set_list]

            for link_set in link_set_list:
                if not isinstance(link_set, dict):
                    continue

                link_info = {
                    'uid': link_set.get('Id', ''),
                    'links': []
                }

                link_list = link_set.get('Link', [])
                if not isinstance(link_list, list):
                    link_list = [link_list]

                for link in link_list:
                    if isinstance(link, dict) and 'Id' in link:
                        link_info['links'].append(link['Id'])

                links.append(link_info)

            return links

        except Exception as e:
            raise GeoAPIError(f"Link retrieval failed: {e}")

    def search_series(self, term: str, **kwargs) -> Dict[str, Any]:
        """Search GEO Series (GSE records)."""
        return self.search('gds', f"{term} AND GSE[ETYP]", **kwargs)

    def search_datasets(self, term: str, **kwargs) -> Dict[str, Any]:
        """Search GEO Datasets (GDS records)."""
        return self.search('gds', f"{term} AND GDS[ETYP]", **kwargs)

    def search_samples(self, term: str, **kwargs) -> Dict[str, Any]:
        """Search GEO Samples (GSM records)."""
        return self.search('gds', f"{term} AND GSM[ETYP]", **kwargs)

    def search_platforms(self, term: str, **kwargs) -> Dict[str, Any]:
        """Search GEO Platforms (GPL records)."""
        return self.search('gds', f"{term} AND GPL[ETYP]", **kwargs)

    def get_series_by_accession(self, accession: str) -> Optional[GeoSeries]:
        """Get a single Series by accession number."""
        if not validate_accession(accession):
            raise GeoValidationError(f"Invalid accession format: {accession}")

        search_results = self.search('gds', f"{accession}[ACCN]")
        if search_results['uids']:
            summaries = self.get_summary('gds', uids=search_results['uids'])
            for record in summaries:
                if isinstance(record, GeoSeries):
                    return record
        return None

    def get_dataset_by_accession(self, accession: str) -> Optional[GeoDataset]:
        """Get a single Dataset by accession number."""
        if not validate_accession(accession):
            raise GeoValidationError(f"Invalid accession format: {accession}")

        search_results = self.search('gds', f"{accession}[ACCN]")
        if search_results['uids']:
            summaries = self.get_summary('gds', uids=search_results['uids'])
            for record in summaries:
                if isinstance(record, GeoDataset):
                    return record
        return None

    def get_sample_by_accession(self, accession: str) -> Optional[GeoSample]:
        """Get a single Sample by accession number."""
        if not validate_accession(accession):
            raise GeoValidationError(f"Invalid accession format: {accession}")

        search_results = self.search('gds', f"{accession}[ACCN]")
        if search_results['uids']:
            summaries = self.get_summary('gds', uids=search_results['uids'])
            for record in summaries:
                if isinstance(record, GeoSample):
                    return record
        return None

    def get_platform_by_accession(self, accession: str) -> Optional[GeoPlatform]:
        """Get a single Platform by accession number."""
        if not validate_accession(accession):
            raise GeoValidationError(f"Invalid accession format: {accession}")

        search_results = self.search('gds', f"{accession}[ACCN]")
        if search_results['uids']:
            summaries = self.get_summary('gds', uids=search_results['uids'])
            for record in summaries:
                if isinstance(record, GeoPlatform):
                    return record
        return None
