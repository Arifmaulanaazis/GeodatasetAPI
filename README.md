# GeoDataset API

A comprehensive Python library for accessing and downloading data from the NCBI GEO (Gene Expression Omnibus) database programmatically.

## Features

- **Easy-to-use API**: Simple interface to NCBI's Entrez Programming Utilities (E-Utils)
- **Comprehensive search**: Search across Series, Datasets, Samples, and Platforms
- **Data models**: Structured data models for different GEO record types
- **FTP downloads**: Built-in FTP client for downloading raw data files
- **Batch processing**: Handle large result sets efficiently
- **Error handling**: Robust error handling with custom exceptions
- **Rate limiting**: Built-in rate limiting to respect NCBI's usage guidelines

## Installation

```bash
git clone https://github.com/Arifmaulanaazis/GeodatasetAPI.git
cd GeodatasetAPI
pip install .
```

## Quick Start

```python
from geodataset import GeoClient

# Initialize client (provide your email for NCBI)
client = GeoClient(email="your.email@example.com")

# Search for breast cancer related series
results = client.search_series("breast cancer", retmax=10)

# Get detailed information
if results['uids']:
    summaries = client.get_summary('gds', uids=results['uids'])

    for record in summaries:
        print(f"{record.accession}: {record.title}")
        print(f"Organism: {record.organism}")
        print(f"Samples: {record.sample_count}")
        print()
```

## Main Components

### GeoClient

The main client for interacting with NCBI GEO database.

```python
from geodataset import GeoClient

client = GeoClient(email="your.email@example.com", api_key="your-api-key")
```

**Key Methods:**

- `search(db, term, **kwargs)` - Search database with term
- `get_summary(db, uids=None, query_key=None, web_env=None)` - Get record summaries
- `fetch(db, uids=None, query_key=None, web_env=None)` - Fetch full records
- `link(dbfrom, db, uids=None, query_key=None, web_env=None)` - Find linked records
- `search_series(term, **kwargs)` - Search Series (GSE records)
- `search_datasets(term, **kwargs)` - Search Datasets (GDS records)
- `search_samples(term, **kwargs)` - Search Samples (GSM records)
- `search_platforms(term, **kwargs)` - Search Platforms (GPL records)

### GeoFTPClient

Client for downloading files from NCBI FTP server.

```python
from geodataset import GeoFTPClient, download_geo_files

# Using context manager
with GeoFTPClient() as ftp_client:
    files = ftp_client.download_series_files("GSE12345", "./downloads")

# Or use convenience function
files = download_geo_files("GSE12345", "./downloads", extract_archives=True)
```

### Data Models

Structured models for GEO records:

```python
from geodataset import GeoSeries, GeoDataset, GeoSample, GeoPlatform

# Models are automatically created when fetching summaries
summaries = client.get_summary('gds', uids=['200012345'])

for record in summaries:
    if isinstance(record, GeoSeries):
        print(f"Series: {record.accession}")
        print(f"Title: {record.title}")
        print(f"Organism: {record.organism}")
        print(f"Sample count: {record.sample_count}")
```

## Examples

### Basic Search

```python
from geodataset import GeoClient

client = GeoClient(email="your.email@example.com")

# Search for Series
results = client.search_series("breast cancer AND microarray", retmax=20)

print(f"Found {results['count']} results")

# Get summaries
if results['uids']:
    summaries = client.get_summary('gds', uids=results['uids'])

    for record in summaries:
        print(f"- {record.accession}: {record.title}")
```

### Advanced Search

```python
# Search with date range
date_query = "2023/01/01:2023/12/31[PDAT]"
results = client.search_series(f"cancer AND {date_query}")

# Search by organism and platform
results = client.search('gds',
    'Homo sapiens[ORGN] AND GPL96[ACCN] AND GSE[ETYP]',
    retmax=100
)
```

### Downloading Data

```python
from geodataset import download_geo_files

# Download all files for a Series
files = download_geo_files(
    "GSE12345",
    local_dir="./data",
    file_types=['soft', 'miniml', 'matrix'],
    extract_archives=True
)

print(f"Downloaded {len(files)} files")
```

### Finding Linked Records

```python
# Get PubMed IDs linked to GEO Series
linked = client.link('gds', 'pubmed', uids=['200012345'])

for link_info in linked:
    print(f"UID {link_info['uid']} has {len(link_info['links'])} PubMed links")
```

## Search Syntax

The library supports NCBI's Entrez search syntax:

### Field Tags
- `[All Fields]` - Search all fields
- `[ORGN]` - Organism
- `[ACCN]` - Accession number
- `[ETYP]` - Entry type (GSE, GDS, GSM, GPL)
- `[PDAT]` - Publication date (YYYY/MM/DD)
- `[Filter]` - Predefined filters

### Boolean Operators
- `AND` - Both terms required
- `OR` - Either term required
- `NOT` - Exclude term

### Examples

```python
# Recent publications
"published last 3 months[Filter]"

# Date range
"2020/01/01:2023/12/31[PDAT]"

# Organism and entry type
"Homo sapiens[ORGN] AND GSE[ETYP]"

# Exclude cell lines
"tissue AND NOT cell line"

# Platform specific
"GPL96[ACCN] AND GSE[ETYP]"
```

## Error Handling

```python
from geodataset import GeoClient, GeoAPIError, GeoFTPError, GeoValidationError

client = GeoClient(email="your.email@example.com")

try:
    results = client.search_series("invalid query")
except GeoAPIError as e:
    print(f"API Error: {e}")
except GeoValidationError as e:
    print(f"Validation Error: {e}")
```

## FTP Downloads

### File Types Available

- **SOFT files**: Standard data format
- **MINiML files**: XML format
- **Series Matrix**: Tabular format with expression values
- **Supplementary files**: Raw data files (CEL, TXT, etc.)

### FTP Directory Structure

```
/geo/
├── series/GSEnnn/GSE12345/          # Series data
├── datasets/GDSnnn/GDS1234/         # Dataset data
├── platforms/GPLnnn/GPL123/         # Platform data
└── samples/GSMnnn/GSM12345/         # Sample data
```

## Rate Limiting

The library includes built-in rate limiting to respect NCBI's usage guidelines:

```python
# Default: 0.1 seconds between requests
client = GeoClient(email="your.email@example.com")

# Custom rate limit
client = GeoClient(email="your.email@example.com", rate_limit=0.3)

# Higher rate limits available with API key
client = GeoClient(
    email="your.email@example.com",
    api_key="your-ncbi-api-key",
    rate_limit=0.05
)
```

## Best Practices

1. **Always provide your email**: Required for NCBI API usage
2. **Use API keys**: Get higher rate limits (apply at NCBI)
3. **Respect rate limits**: Don't overwhelm the servers
4. **Handle errors gracefully**: Network issues can occur
5. **Batch large requests**: Use query_key and WebEnv for pagination
6. **Validate accessions**: Use `validate_accession()` before searching

## API Reference

### GeoClient

#### Methods

##### `search(db, term, retmax=1000, usehistory=True, **kwargs)`

Search the specified database.

**Parameters:**
- `db` (str): Database name ('gds' or 'geoprofiles')
- `term` (str): Search term
- `retmax` (int): Maximum results to return
- `usehistory` (bool): Use history for pagination

**Returns:** Dictionary with 'uids', 'count', 'query_key', 'web_env'

##### `get_summary(db, uids=None, query_key=None, web_env=None, version="2.0")`

Get detailed summaries for records.

**Returns:** List of GeoRecord objects

##### `fetch(db, uids=None, query_key=None, web_env=None, rettype=None, retmode="text")`

Fetch full record data.

**Returns:** Raw record data as string

### GeoFTPClient

#### Methods

##### `download_series_files(accession, local_dir, file_types=None)`

Download all available files for a Series.

##### `download_supplementary_files(accession, local_dir)`

Download supplementary files.

##### `extract_archive(archive_path, extract_to=None)`

Extract compressed archive files.

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## Citation

If you use this library in your research, please cite:

```
GeoDataset API: A Python library for accessing NCBI GEO datasets
https://github.com/Arifmaulanaazis/GeodatasetAPI
```

## Support

For issues and questions:
- Create an issue on GitHub
- Email: titandigitalsoft@gmail.com

## Changelog

### v1.0.0
- Initial release
- Full E-Utils API support
- FTP download functionality
- Comprehensive data models
- Example scripts included
