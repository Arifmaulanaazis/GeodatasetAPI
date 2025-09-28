#!/usr/bin/env python3
"""
Comprehensive test script for GeoDataset API.
"""

from GeodatasetAPI import GeoClient, validate_accession, format_ftp_path
from GeodatasetAPI.models import GeoSeries, GeoDataset, GeoSample, GeoPlatform

def test_validation():
    """Test validation functions."""
    print("Testing validation functions...")

    # Test valid accessions
    assert validate_accession("GSE12345")
    assert validate_accession("GDS1234")
    assert validate_accession("GSM123")
    assert validate_accession("GPL96")

    # Test invalid accessions
    assert not validate_accession("invalid")
    assert not validate_accession("12345")
    assert not validate_accession("GSE")
    assert not validate_accession("")

    print("+ Validation functions work correctly")

def test_ftp_paths():
    """Test FTP path formatting."""
    print("Testing FTP path formatting...")

    # Test series path
    series_path = format_ftp_path("GSE12345", "series")
    assert "GSE12nnn" in series_path
    assert "GSE12345" in series_path
    assert series_path.startswith("/geo/series/")

    # Test platform path
    platform_path = format_ftp_path("GPL96", "platform")
    assert "GPLnnn" in platform_path
    assert "GPL96" in platform_path
    assert platform_path.startswith("/geo/platforms/")

    # Test dataset path
    dataset_path = format_ftp_path("GDS1234", "dataset")
    assert "GDS1nnn" in dataset_path
    assert "GDS1234" in dataset_path
    assert dataset_path.startswith("/geo/datasets/")

    # Test sample path
    sample_path = format_ftp_path("GSM123", "sample")
    assert "GSMnnn" in sample_path
    assert "GSM123" in sample_path
    assert sample_path.startswith("/geo/samples/")

    print("+ FTP path formatting works correctly")

def test_models():
    """Test data model creation."""
    print("Testing model creation...")

    # Test GeoSeries
    series = GeoSeries("123", "GSE123", "Test Series", "Test summary",
                      organism="Homo sapiens", platform_count=2, sample_count=20)
    assert series.accession == "GSE123"
    assert series.uid == "123"
    assert series.title == "Test Series"
    assert series.organism == "Homo sapiens"
    assert series.platform_count == 2
    assert series.sample_count == 20

    # Test GeoDataset
    dataset = GeoDataset("456", "GDS456", "Test Dataset", "Dataset summary",
                        platform="GPL96", sample_count=15, gene_count=20000)
    assert dataset.accession == "GDS456"
    assert dataset.platform == "GPL96"
    assert dataset.sample_count == 15
    assert dataset.gene_count == 20000

    # Test GeoSample
    sample = GeoSample("789", "GSM789", "Test Sample", "Sample summary",
                      organism="Homo sapiens", platform="GPL96", series="GSE123",
                      molecule="total RNA")
    assert sample.accession == "GSM789"
    assert sample.organism == "Homo sapiens"
    assert sample.platform == "GPL96"
    assert sample.series == "GSE123"
    assert sample.molecule == "total RNA"

    # Test GeoPlatform
    platform = GeoPlatform("101", "GPL101", "Test Platform", "Platform summary",
                          technology="in situ oligonucleotide", manufacturer="Affymetrix")
    assert platform.accession == "GPL101"
    assert platform.technology == "in situ oligonucleotide"
    assert platform.manufacturer == "Affymetrix"

    print("+ Model creation works correctly")

def test_client():
    """Test client initialization."""
    print("Testing client initialization...")

    # Test basic client
    client = GeoClient(email="test@example.com")
    assert client.email == "test@example.com"
    assert client.rate_limit == 0.1

    # Test client with API key
    client_with_key = GeoClient(email="test@example.com", api_key="test-key", rate_limit=0.05)
    assert client_with_key.email == "test@example.com"
    assert client_with_key.api_key == "test-key"
    assert client_with_key.rate_limit == 0.05

    print("+ Client initialization works correctly")

def test_xml_parsing():
    """Test XML parsing utilities."""
    print("Testing XML parsing...")

    from GeodatasetAPI.utils import parse_xml_response, extract_uids_from_search

    # Test XML parsing with sample data
    sample_xml = """<?xml version="1.0"?>
    <eSearchResult>
        <Count>2</Count>
        <IdList>
            <Id>200012345</Id>
            <Id>200012346</Id>
        </IdList>
        <QueryKey>1</QueryKey>
        <WebEnv>NCID_01_1234567890</WebEnv>
    </eSearchResult>"""

    parsed = parse_xml_response(sample_xml)
    assert parsed['Count'] == '2'

    uids = extract_uids_from_search(parsed)
    assert uids == ['200012345', '200012346']

    print("+ XML parsing works correctly")

def main():
    """Run all tests."""
    print("Running comprehensive GeoDataset API tests...\n")

    try:
        test_validation()
        test_ftp_paths()
        test_models()
        test_client()
        test_xml_parsing()

        print("\n*** ALL TESTS PASSED! ***")
        print("The GeoDataset API is ready for publication!")
        return True

    except Exception as e:
        print(f"\nERROR: TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
