"""
Data models for GEO records.
"""

from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import re
from .exceptions import GeoValidationError


class GeoRecord:
    """Base class for all GEO records."""

    def __init__(self, uid: str, accession: str, title: str = None,
                 summary: str = None, status: str = None, **kwargs):
        """
        Initialize a GEO record.

        Args:
            uid: Unique identifier
            accession: GEO accession number
            title: Record title
            summary: Record summary
            status: Record status
            **kwargs: Additional fields
        """
        self.uid = str(uid)
        self.accession = accession
        self.title = title
        self.summary = summary
        self.status = status
        self._raw_data = kwargs

    @property
    def id(self) -> str:
        """Alias for uid for compatibility."""
        return self.uid

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'uid': self.uid,
            'accession': self.accession,
            'title': self.title,
            'summary': self.summary,
            'status': self.status,
            **self._raw_data
        }


class GeoSeries(GeoRecord):
    """GEO Series record (GSE)."""

    def __init__(self, uid: str, accession: str, title: str = None,
                 summary: str = None, status: str = None,
                 organism: str = None, platform_count: int = None,
                 sample_count: int = None, pubmed_ids: List[str] = None,
                 submission_date: str = None, last_update: str = None,
                 **kwargs):
        """
        Initialize a GEO Series.

        Args:
            uid: Unique identifier
            accession: GEO accession number (GSE)
            title: Series title
            summary: Series summary
            status: Series status
            organism: Source organism
            platform_count: Number of platforms
            sample_count: Number of samples
            pubmed_ids: Associated PubMed IDs
            submission_date: Date of submission
            last_update: Last update date
            **kwargs: Additional fields
        """
        super().__init__(uid, accession, title, summary, status, **kwargs)

        self.organism = organism
        self.platform_count = int(platform_count) if platform_count else None
        self.sample_count = int(sample_count) if sample_count else None
        self.pubmed_ids = pubmed_ids or []
        self.submission_date = submission_date
        self.last_update = last_update

        # Validate accession format
        if not self.accession.startswith('GSE'):
            raise GeoValidationError(f"Invalid Series accession: {self.accession}")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = super().to_dict()
        data.update({
            'organism': self.organism,
            'platform_count': self.platform_count,
            'sample_count': self.sample_count,
            'pubmed_ids': self.pubmed_ids,
            'submission_date': self.submission_date,
            'last_update': self.last_update
        })
        return data


class GeoDataset(GeoRecord):
    """GEO Dataset record (GDS)."""

    def __init__(self, uid: str, accession: str, title: str = None,
                 summary: str = None, status: str = None,
                 platform: str = None, sample_count: int = None,
                 gene_count: int = None, pubmed_ids: List[str] = None,
                 **kwargs):
        """
        Initialize a GEO Dataset.

        Args:
            uid: Unique identifier
            accession: GEO accession number (GDS)
            title: Dataset title
            summary: Dataset summary
            status: Dataset status
            platform: Platform accession
            sample_count: Number of samples
            gene_count: Number of genes
            pubmed_ids: Associated PubMed IDs
            **kwargs: Additional fields
        """
        super().__init__(uid, accession, title, summary, status, **kwargs)

        self.platform = platform
        self.sample_count = int(sample_count) if sample_count else None
        self.gene_count = int(gene_count) if gene_count else None
        self.pubmed_ids = pubmed_ids or []

        # Validate accession format
        if not self.accession.startswith('GDS'):
            raise GeoValidationError(f"Invalid Dataset accession: {self.accession}")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = super().to_dict()
        data.update({
            'platform': self.platform,
            'sample_count': self.sample_count,
            'gene_count': self.gene_count,
            'pubmed_ids': self.pubmed_ids
        })
        return data


class GeoSample(GeoRecord):
    """GEO Sample record (GSM)."""

    def __init__(self, uid: str, accession: str, title: str = None,
                 summary: str = None, status: str = None,
                 organism: str = None, platform: str = None,
                 series: str = None, molecule: str = None,
                 characteristics: Dict[str, str] = None,
                 **kwargs):
        """
        Initialize a GEO Sample.

        Args:
            uid: Unique identifier
            accession: GEO accession number (GSM)
            title: Sample title
            summary: Sample summary
            status: Sample status
            organism: Source organism
            platform: Platform accession
            series: Parent series accession
            molecule: Molecule type
            characteristics: Sample characteristics
            **kwargs: Additional fields
        """
        super().__init__(uid, accession, title, summary, status, **kwargs)

        self.organism = organism
        self.platform = platform
        self.series = series
        self.molecule = molecule
        self.characteristics = characteristics or {}

        # Validate accession format
        if not self.accession.startswith('GSM'):
            raise GeoValidationError(f"Invalid Sample accession: {self.accession}")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = super().to_dict()
        data.update({
            'organism': self.organism,
            'platform': self.platform,
            'series': self.series,
            'molecule': self.molecule,
            'characteristics': self.characteristics
        })
        return data


class GeoPlatform(GeoRecord):
    """GEO Platform record (GPL)."""

    def __init__(self, uid: str, accession: str, title: str = None,
                 summary: str = None, status: str = None,
                 technology: str = None, manufacturer: str = None,
                 distribution: str = None, organism: str = None,
                 **kwargs):
        """
        Initialize a GEO Platform.

        Args:
            uid: Unique identifier
            accession: GEO accession number (GPL)
            title: Platform title
            summary: Platform summary
            status: Platform status
            technology: Technology type
            manufacturer: Manufacturer name
            distribution: Distribution type
            organism: Organism compatibility
            **kwargs: Additional fields
        """
        super().__init__(uid, accession, title, summary, status, **kwargs)

        self.technology = technology
        self.manufacturer = manufacturer
        self.distribution = distribution
        self.organism = organism

        # Validate accession format
        if not self.accession.startswith('GPL'):
            raise GeoValidationError(f"Invalid Platform accession: {self.accession}")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = super().to_dict()
        data.update({
            'technology': self.technology,
            'manufacturer': self.manufacturer,
            'distribution': self.distribution,
            'organism': self.organism
        })
        return data


# Factory function to create appropriate model from data
def create_geo_record(record_type: str, **data) -> GeoRecord:
    """
    Create appropriate GEO record based on accession prefix.

    Args:
        record_type: Type hint ('series', 'dataset', 'sample', 'platform')
        **data: Record data

    Returns:
        Appropriate GEO record instance
    """
    accession = data.get('accession', '')

    if accession.startswith('GSE'):
        return GeoSeries(**data)
    elif accession.startswith('GDS'):
        return GeoDataset(**data)
    elif accession.startswith('GSM'):
        return GeoSample(**data)
    elif accession.startswith('GPL'):
        return GeoPlatform(**data)
    else:
        # Default to base class
        return GeoRecord(**data)
