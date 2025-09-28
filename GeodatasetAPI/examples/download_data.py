#!/usr/bin/env python3
"""
Data download example for GeoDataset API.

This example demonstrates how to:
1. Download SOFT files for a GEO Series
2. Download supplementary data files
3. Extract downloaded archives
"""

import sys
import os
from pathlib import Path

# Add the parent directory to the Python path to import geodataset
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from GeodatasetAPI import GeoClient, GeoFTPClient, download_geo_files, GeoDatasetError


def main():
    """Main function demonstrating data download functionality."""

    # Create download directory
    download_dir = Path("geo_downloads")
    download_dir.mkdir(exist_ok=True)

    try:
        # Method 1: Using the convenience function
        print("Method 1: Using convenience function...")
        accession = "GSE1000"

        print(f"Downloading files for {accession}...")
        downloaded_files = download_geo_files(
            accession,
            local_dir=download_dir / "method1",
            file_types=['soft', 'miniml'],
            extract_archives=True
        )

        print(f"Downloaded {len(downloaded_files)} files/directories:")
        for file_path in downloaded_files:
            print(f"  - {file_path}")

        # Method 2: Using FTP client directly
        print("\nMethod 2: Using FTP client directly...")
        with GeoFTPClient() as ftp_client:
            # Download supplementary files for a different series
            suppl_files = ftp_client.download_supplementary_files(
                "GSE2000",
                download_dir / "method2"
            )

            print(f"Downloaded {len(suppl_files)} supplementary files:")
            for file_path in suppl_files:
                print(f"  - {file_path}")

            # Extract any archives
            for file_path in suppl_files:
                if file_path.suffix in ['.tar', '.gz', '.zip']:
                    try:
                        extract_dir = ftp_client.extract_archive(file_path)
                        print(f"  Extracted to: {extract_dir}")
                    except GeoDatasetError as e:
                        print(f"  Failed to extract {file_path}: {e}")

        # Method 3: Search and download workflow
        print("\nMethod 3: Search and download workflow...")
        client = GeoClient(email="your.email@example.com")

        # Search for recent series
        search_results = client.search_series(
            "cancer AND published last 3 months[Filter]",
            retmax=3
        )

        if search_results['uids']:
            print(f"Found {len(search_results['uids'])} recent series")

            # Get details for the first result
            summaries = client.get_summary('gds', uids=search_results['uids'][:1])

            if summaries:
                series = summaries[0]
                print(f"Downloading data for: {series.accession}")

                # Download all available files
                downloaded_files = download_geo_files(
                    series.accession,
                    local_dir=download_dir / "workflow",
                    extract_archives=True
                )

                print(f"Downloaded {len(downloaded_files)} files for {series.accession}")

        print(f"\nAll downloads completed. Files saved to: {download_dir}")

    except GeoDatasetError as e:
        print(f"Error: {e}")
        return 1
    except KeyboardInterrupt:
        print("\nDownload interrupted by user")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
