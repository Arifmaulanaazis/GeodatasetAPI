#!/usr/bin/env python3
"""
Basic search example for GeoDataset API.

This example demonstrates how to:
1. Search for GEO Series related to a specific topic
2. Get detailed information about the results
3. Filter and display relevant information
"""

import sys
import os
from pathlib import Path

# Add the parent directory to the Python path to import geodataset
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from GeodatasetAPI import GeoClient, GeoDatasetError


def main():
    """Main function demonstrating basic search functionality."""

    # Initialize the client
    # In a real application, you should provide your email address
    client = GeoClient(email="your.email@example.com")

    try:
        # Example 1: Search for Series related to breast cancer
        print("Searching for breast cancer related Series...")
        search_results = client.search_series("breast cancer", retmax=10)

        print(f"Found {search_results['count']} results")
        print(f"Retrieved {len(search_results['uids'])} UIDs")

        if search_results['uids']:
            # Get detailed summaries for the first few results
            summaries = client.get_summary('gds', uids=search_results['uids'][:5])

            print("\nFirst 5 results:")
            for i, record in enumerate(summaries, 1):
                print(f"{i}. {record.accession}: {record.title}")
                if hasattr(record, 'organism') and record.organism:
                    print(f"   Organism: {record.organism}")
                if hasattr(record, 'platform_count') and record.platform_count:
                    print(f"   Platforms: {record.platform_count}")
                if hasattr(record, 'sample_count') and record.sample_count:
                    print(f"   Samples: {record.sample_count}")
                print()

        # Example 2: Search for datasets by organism
        print("Searching for human datasets...")
        human_results = client.search_datasets("Homo sapiens[ORGN]", retmax=5)

        if human_results['uids']:
            datasets = client.get_summary('gds', uids=human_results['uids'])

            print("Human datasets:")
            for record in datasets:
                if record.accession.startswith('GDS'):
                    print(f"- {record.accession}: {record.title}")
                    if hasattr(record, 'platform') and record.platform:
                        print(f"  Platform: {record.platform}")
                    print()

        # Example 3: Get a specific series by accession
        print("Getting specific series by accession...")
        series = client.get_series_by_accession("GSE1000")
        if series:
            print(f"Series {series.accession}:")
            print(f"Title: {series.title}")
            print(f"Organism: {series.organism}")
            print(f"Summary: {series.summary[:200]}...")
        else:
            print("Series GSE1000 not found")

    except GeoDatasetError as e:
        print(f"Error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
