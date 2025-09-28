#!/usr/bin/env python3
"""
Advanced queries example for GeoDataset API.

This example demonstrates:
1. Complex search queries with multiple criteria
2. Using date ranges and filters
3. Finding linked records between databases
4. Batch processing of results
"""

import sys
import os
from pathlib import Path
from datetime import datetime, timedelta

# Add the parent directory to the Python path to import geodataset
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from GeodatasetAPI import GeoClient, GeoDatasetError


def main():
    """Main function demonstrating advanced query functionality."""

    client = GeoClient(email="your.email@example.com")

    try:
        # Example 1: Complex search with multiple criteria
        print("Example 1: Complex search for human breast cancer microarray data...")

        # Build complex query
        query_parts = [
            "breast cancer[All Fields]",
            "Homo sapiens[ORGN]",  # Human samples
            "microarray[All Fields]",  # Microarray technology
            "GSE[ETYP]",  # Only Series records
            "published last 6 months[Filter]"  # Recent publications
        ]

        complex_query = " AND ".join(query_parts)
        print(f"Search query: {complex_query}")

        search_results = client.search('gds', complex_query, retmax=20)

        print(f"Found {search_results['count']} results")

        if search_results['uids']:
            # Get detailed information
            summaries = client.get_summary('gds', uids=search_results['uids'])

            print("\nTop results:")
            for i, record in enumerate(summaries[:5], 1):
                print(f"{i}. {record.accession}")
                print(f"   Title: {record.title}")
                print(f"   Organism: {getattr(record, 'organism', 'N/A')}")
                print(f"   Samples: {getattr(record, 'sample_count', 'N/A')}")
                print(f"   Platforms: {getattr(record, 'platform_count', 'N/A')}")
                print()

        # Example 2: Search by date range
        print("\nExample 2: Search by date range...")

        # Calculate date range (last 30 days)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)

        date_query = f"{start_date.strftime('%Y/%m/%d')}:{end_date.strftime('%Y/%m/%d')}[PDAT]"
        date_search = f"cancer[All Fields] AND {date_query}"

        date_results = client.search('gds', date_search, retmax=10)
        print(f"Found {date_results['count']} cancer-related records from the last 30 days")

        # Example 3: Find linked PubMed IDs
        print("\nExample 3: Finding linked PubMed IDs...")

        if search_results['uids']:
            # Get PubMed links for the first few series
            linked_records = client.link('gds', 'pubmed', uids=search_results['uids'][:3])

            for link_info in linked_records:
                if link_info['links']:
                    print(f"Series UID {link_info['uid']} has {len(link_info['links'])} linked PubMed IDs:")
                    print(f"  PubMed IDs: {', '.join(link_info['links'][:5])}")
                    if len(link_info['links']) > 5:
                        print(f"  ... and {len(link_info['links']) - 5} more")
                    print()

        # Example 4: Batch processing - get full records
        print("\nExample 4: Batch processing with full records...")

        if search_results['uids']:
            # Fetch full record data for the first result
            full_data = client.fetch('gds', uids=search_results['uids'][:1], retmode='text')

            print("Full record data (first 500 characters):")
            print(full_data[:500])
            print("...")

            # You could parse this data further or save it to a file
            with open("sample_full_record.txt", "w", encoding="utf-8") as f:
                f.write(full_data)
            print("Full record saved to sample_full_record.txt")

        # Example 5: Platform-specific search
        print("\nExample 5: Platform-specific search...")

        # Search for data from a specific platform (Affymetrix HG-U133A)
        platform_search = client.search('gds',
                                      'GPL96[ACCN] AND GSE[ETYP]',
                                      retmax=5)

        print(f"Found {platform_search['count']} Series using platform GPL96")

        if platform_search['uids']:
            platform_summaries = client.get_summary('gds', uids=platform_search['uids'])

            for record in platform_summaries:
                print(f"- {record.accession}: {record.title}")

        # Example 6: Search with organism and sample type filters
        print("\nExample 6: Organism and sample type filters...")

        # Search for human tissue samples (not cell lines)
        tissue_query = (
            '("Homo sapiens"[ORGN] AND '
            '("tissue"[All Fields] OR "biopsy"[All Fields]) AND '
            'NOT "cell line"[All Fields] AND '
            'GSE[ETYP] AND '
            'published last year[Filter])'
        )

        tissue_results = client.search('gds', tissue_query, retmax=5)
        print(f"Found {tissue_results['count']} human tissue sample series from the last year")

        if tissue_results['uids']:
            tissue_summaries = client.get_summary('gds', uids=tissue_results['uids'])

            for record in tissue_summaries:
                print(f"- {record.accession}: {record.title}")

    except GeoDatasetError as e:
        print(f"Error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
