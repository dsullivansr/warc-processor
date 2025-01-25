"""Setup script for warc-processor package."""

from setuptools import find_packages, setup

setup(
    name="warc-processor",
    version="0.1.1",
    description="A Python library for processing WARC files",
    author="Daniel Sullivan",
    packages=find_packages(),
    install_requires=[
        "warcio",
        "beautifulsoup4",
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
