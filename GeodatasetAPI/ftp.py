"""
FTP functionality for downloading GEO data files.
"""

import ftplib
import os
import gzip
import tarfile
import zipfile
from pathlib import Path
from typing import List, Optional, Union, BinaryIO
import logging
from urllib.parse import urlparse

from .utils import format_ftp_path, validate_accession
from .exceptions import GeoFTPError, GeoValidationError

logger = logging.getLogger(__name__)


class GeoFTPClient:
    """
    Client for downloading files from NCBI GEO FTP server.
    """

    FTP_BASE = "ftp.ncbi.nlm.nih.gov"

    def __init__(self, timeout: int = 30):
        """
        Initialize FTP client.

        Args:
            timeout: FTP timeout in seconds
        """
        self.timeout = timeout
        self.ftp = None

    def connect(self) -> None:
        """Connect to NCBI FTP server."""
        try:
            self.ftp = ftplib.FTP(self.FTP_BASE, timeout=self.timeout)
            self.ftp.login()
            logger.info(f"Connected to {self.FTP_BASE}")
        except ftplib.all_errors as e:
            raise GeoFTPError(f"Failed to connect to FTP server: {e}")

    def disconnect(self) -> None:
        """Disconnect from FTP server."""
        if self.ftp:
            try:
                self.ftp.quit()
                logger.info("Disconnected from FTP server")
            except ftplib.all_errors as e:
                logger.warning(f"Error disconnecting from FTP: {e}")
            finally:
                self.ftp = None

    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()

    def list_files(self, path: str) -> List[str]:
        """
        List files in FTP directory.

        Args:
            path: FTP directory path

        Returns:
            List of filenames
        """
        if not self.ftp:
            raise GeoFTPError("Not connected to FTP server")

        try:
            self.ftp.cwd(path)
            files = self.ftp.nlst()
            return files
        except ftplib.all_errors as e:
            raise GeoFTPError(f"Failed to list files in {path}: {e}")

    def download_file(self, ftp_path: str, local_path: Union[str, Path],
                     overwrite: bool = False) -> Path:
        """
        Download file from FTP server.

        Args:
            ftp_path: Path on FTP server
            local_path: Local destination path
            overwrite: Whether to overwrite existing file

        Returns:
            Path to downloaded file
        """
        if not self.ftp:
            raise GeoFTPError("Not connected to FTP server")

        local_path = Path(local_path)

        # Check if file exists
        if local_path.exists() and not overwrite:
            raise GeoFTPError(f"File already exists: {local_path}")

        # Create directory if it doesn't exist
        local_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(local_path, 'wb') as f:
                self.ftp.retrbinary(f"RETR {ftp_path}", f.write)
            logger.info(f"Downloaded {ftp_path} to {local_path}")
            return local_path
        except ftplib.all_errors as e:
            raise GeoFTPError(f"Failed to download {ftp_path}: {e}")

    def download_series_files(self, accession: str, local_dir: Union[str, Path],
                             file_types: List[str] = None) -> List[Path]:
        """
        Download all available files for a GEO Series.

        Args:
            accession: Series accession (e.g., GSE12345)
            local_dir: Local directory to save files
            file_types: Types of files to download ('soft', 'miniml', 'matrix', 'suppl')

        Returns:
            List of downloaded file paths
        """
        if file_types is None:
            file_types = ['soft', 'miniml', 'matrix']

        if not validate_accession(accession):
            raise GeoValidationError(f"Invalid accession: {accession}")

        downloaded_files = []

        try:
            # Get FTP path for series
            ftp_base_path = format_ftp_path(accession, 'series')

            # List files in series directory
            try:
                files = self.list_files(ftp_base_path)
            except GeoFTPError:
                # If series directory doesn't exist, try to find it
                logger.warning(f"Series directory {ftp_base_path} not found, trying to locate files...")
                # This is a fallback - in practice, you might need to search for the correct path
                return downloaded_files

            local_dir = Path(local_dir)
            local_dir.mkdir(parents=True, exist_ok=True)

            # Download specific file types
            for file_type in file_types:
                for ftp_file in files:
                    if self._matches_file_type(ftp_file, accession, file_type):
                        local_file = local_dir / Path(ftp_file).name
                        try:
                            self.download_file(ftp_file, local_file)
                            downloaded_files.append(local_file)
                        except GeoFTPError as e:
                            logger.warning(f"Failed to download {ftp_file}: {e}")

        except Exception as e:
            raise GeoFTPError(f"Failed to download series files: {e}")

        return downloaded_files

    def download_supplementary_files(self, accession: str,
                                   local_dir: Union[str, Path]) -> List[Path]:
        """
        Download supplementary files for a GEO record.

        Args:
            accession: GEO accession (GSE, GDS, GSM, GPL)
            local_dir: Local directory to save files

        Returns:
            List of downloaded file paths
        """
        if not validate_accession(accession):
            raise GeoValidationError(f"Invalid accession: {accession}")

        downloaded_files = []

        try:
            # Determine record type and get appropriate FTP path
            if accession.startswith('GSE'):
                ftp_base_path = format_ftp_path(accession, 'series') + 'suppl/'
            elif accession.startswith('GDS'):
                ftp_base_path = format_ftp_path(accession, 'dataset') + 'soft/'
            elif accession.startswith('GSM'):
                ftp_base_path = format_ftp_path(accession, 'sample') + 'suppl/'
            elif accession.startswith('GPL'):
                ftp_base_path = format_ftp_path(accession, 'platform') + 'suppl/'
            else:
                raise GeoValidationError(f"Unsupported accession type: {accession}")

            # List supplementary files
            try:
                files = self.list_files(ftp_base_path)
            except GeoFTPError:
                logger.warning(f"No supplementary files found for {accession}")
                return downloaded_files

            local_dir = Path(local_dir)
            local_dir.mkdir(parents=True, exist_ok=True)

            # Download all supplementary files
            for ftp_file in files:
                if ftp_file not in ['.', '..']:  # Skip directory entries
                    local_file = local_dir / Path(ftp_file).name
                    try:
                        self.download_file(ftp_file, local_file)
                        downloaded_files.append(local_file)
                    except GeoFTPError as e:
                        logger.warning(f"Failed to download {ftp_file}: {e}")

        except Exception as e:
            raise GeoFTPError(f"Failed to download supplementary files: {e}")

        return downloaded_files

    def _matches_file_type(self, filename: str, accession: str, file_type: str) -> bool:
        """
        Check if filename matches the requested file type.

        Args:
            filename: Name of file on FTP server
            accession: GEO accession
            file_type: Type of file ('soft', 'miniml', 'matrix')

        Returns:
            True if file matches type
        """
        filename_lower = filename.lower()
        accession_lower = accession.lower()

        if file_type == 'soft':
            return (filename_lower.endswith('.soft.gz') and
                   accession_lower in filename_lower)
        elif file_type == 'miniml':
            return (filename_lower.endswith('.xml.tgz') and
                   accession_lower in filename_lower)
        elif file_type == 'matrix':
            return (filename_lower.endswith('_series_matrix.txt.gz') and
                   accession_lower in filename_lower)
        elif file_type == 'suppl':
            return filename_lower.endswith(('.tar', '.gz', '.txt', '.cel.gz'))

        return False

    def extract_archive(self, archive_path: Union[str, Path],
                       extract_to: Union[str, Path] = None) -> Path:
        """
        Extract compressed archive file.

        Args:
            archive_path: Path to archive file
            extract_to: Directory to extract to (default: same as archive)

        Returns:
            Path to extraction directory
        """
        archive_path = Path(archive_path)

        if not archive_path.exists():
            raise GeoFTPError(f"Archive file not found: {archive_path}")

        if extract_to is None:
            extract_to = archive_path.parent
        else:
            extract_to = Path(extract_to)
            extract_to.mkdir(parents=True, exist_ok=True)

        try:
            if archive_path.suffix == '.gz':
                if archive_path.stem.endswith('.tar'):
                    # .tar.gz file
                    with tarfile.open(archive_path, 'r:gz') as tar:
                        tar.extractall(extract_to)
                else:
                    # .gz file
                    output_path = extract_to / archive_path.stem
                    with gzip.open(archive_path, 'rb') as f_in:
                        with open(output_path, 'wb') as f_out:
                            f_out.write(f_in.read())
            elif archive_path.suffix == '.tar':
                # .tar file
                with tarfile.open(archive_path, 'r') as tar:
                    tar.extractall(extract_to)
            elif archive_path.suffix == '.zip':
                # .zip file
                with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_to)
            else:
                raise GeoFTPError(f"Unsupported archive format: {archive_path.suffix}")

            logger.info(f"Extracted {archive_path} to {extract_to}")
            return extract_to

        except Exception as e:
            raise GeoFTPError(f"Failed to extract archive {archive_path}: {e}")


def download_geo_files(accession: str, local_dir: Union[str, Path] = ".",
                      file_types: List[str] = None,
                      extract_archives: bool = True) -> List[Path]:
    """
    Convenience function to download all files for a GEO accession.

    Args:
        accession: GEO accession number
        local_dir: Local directory to save files
        file_types: Types of files to download
        extract_archives: Whether to extract downloaded archives

    Returns:
        List of downloaded file paths
    """
    local_dir = Path(local_dir)
    all_files = []

    with GeoFTPClient() as ftp_client:
        # Download main files if it's a series
        if accession.startswith('GSE'):
            main_files = ftp_client.download_series_files(accession, local_dir, file_types)
            all_files.extend(main_files)

        # Download supplementary files
        suppl_files = ftp_client.download_supplementary_files(accession, local_dir)
        all_files.extend(suppl_files)

    # Extract archives if requested
    if extract_archives:
        extracted_dirs = []
        for file_path in all_files:
            if file_path.suffix in ['.tar', '.gz', '.zip']:
                try:
                    extract_dir = ftp_client.extract_archive(file_path)
                    extracted_dirs.append(extract_dir)
                except GeoFTPError as e:
                    logger.warning(f"Failed to extract {file_path}: {e}")

        return extracted_dirs if extracted_dirs else all_files

    return all_files
