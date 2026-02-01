"""
Setup script for wrds_data_pull package
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_file = Path(__file__).parent.parent / "SKILL.md"
long_description = readme_file.read_text() if readme_file.exists() else ""

setup(
    name="wrds_data_pull",
    version="1.0.0",
    author="Academic Research Team",
    description="Automated WRDS data extraction with pre-built query templates, merge logic, and validation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "pandas>=1.5.0",
        "numpy>=1.23.0",
        "wrds>=3.1.0",
        "scipy>=1.9.0",
        "pyarrow>=10.0.0",
    ],
    extras_require={
        "stata": ["pandas-stata>=0.1.0"],
        "stats": ["statsmodels>=0.13.0"],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Topic :: Office/Business :: Financial",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    keywords="finance research wrds compustat crsp econometrics panel-data",
)
