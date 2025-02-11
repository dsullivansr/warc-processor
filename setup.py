"""Setup script for warc-processor package."""

from setuptools import find_packages, setup

# Read version from version.py
with open('warc_processor/version.py', 'r', encoding='utf-8') as f:
    exec(f.read())

setup(
    name="warc-processor",
    version=__version__,
    description="A Python library for processing WARC files",
    author="Daniel Sullivan",
    packages=find_packages(),
    install_requires=[
        "warcio",
        "beautifulsoup4",
        "selectolax",
    ],
    extras_require={
        "dev": [
            "pytest",
            "pytest-cov",
        ],
    },
    python_requires=">=3.7",
    entry_points={
        "console_scripts": [
            "warc-processor=warc_processor_main:main",
        ],
    },
)
