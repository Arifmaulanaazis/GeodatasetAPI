#!/usr/bin/env python3
"""
Simple test script to verify the GeoDataset API package works correctly.
"""

import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from GeodatasetAPI import GeoClient, GeoDatasetError, validate_accession
    from GeodatasetAPI.models import GeoSeries, GeoDataset, GeoSample, GeoPlatform
    from GeodatasetAPI.utils import format_ftp_path

    print("+ Successfully imported all modules")

    # Test validation functions
    assert validate_accession("GSE12345")
    assert validate_accession("GDS1234")
    assert validate_accession("GSM123")
    assert validate_accession("GPL96")
    assert not validate_accession("invalid")
    assert not validate_accession("12345")
    print("+ Accession validation works correctly")

    # Test FTP path formatting
    series_path = format_ftp_path("GSE12345", "series")
    assert "GSE12nnn" in series_path
    assert "GSE12345" in series_path
    print("+ FTP path formatting works correctly")

    # Test model creation
    series = GeoSeries("123", "GSE123", "Test Series", "Test summary")
    assert series.accession == "GSE123"
    assert series.uid == "123"
    print("+ Model creation works correctly")

    # Test client initialization (without making actual API calls)
    client = GeoClient(email="test@example.com")
    assert client.email == "test@example.com"
    print("+ Client initialization works correctly")

    print("\n*** All tests passed! The GeoDataset API package is working correctly. ***")
    print("\nYou can now use the library with:")
    print("  from geodataset import GeoClient")
    print("  client = GeoClient(email='your.email@example.com')")
    print("  results = client.search_series('your search term')")

except ImportError as e:
    print(f"ERROR: Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"ERROR: Test failed: {e}")
    sys.exit(1)
