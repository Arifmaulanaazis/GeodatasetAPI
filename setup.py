"""
Setup script for GeoDataset API package.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

# Read requirements from requirements.txt if it exists
requirements = []
requirements_path = this_directory / "requirements.txt"
if requirements_path.exists():
    requirements = requirements_path.read_text(encoding="utf-8").splitlines()

setup(
    name="GeodatasetAPI",
    version="1.0.0",
    author="Arif Maulana Azis",
    author_email="titandigitalsoft@gmail.com",
    description="A Python library for accessing NCBI GEO datasets programmatically",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Arifmaulanaazis/GeodatasetAPI",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.25.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=22.0",
            "flake8>=4.0",
            "mypy>=0.950",
        ],
    },
    entry_points={
        "console_scripts": [
            "geodataset-search=geodataset.examples.basic_search:main",
            "geodataset-download=geodataset.examples.download_data:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
