#!/usr/bin/env python3
"""Setup script for Komorebi Workspace Indicator."""

from setuptools import setup, find_packages

if __name__ == "__main__":
    setup(
        name="komorebi-workspace-indicator",
        version="0.1.0",
        description="A Windows-only workspace indicator for Komorebi window manager",
        long_description=open("README.md").read(),
        long_description_content_type="text/markdown",
        author="Gary Calpo",
        packages=find_packages(),
        python_requires=">=3.8",
        install_requires=[
            "PyQt6>=6.4.0",
            "Pillow>=9.0.0",
            "psutil>=5.8.0",
            "pywin32>=305",
        ],
        extras_require={
            "dev": [
                "pytest>=7.0.0",
                "ruff>=0.1.0",
                "black>=23.0.0",
            ],
        },
        entry_points={
            "console_scripts": [
                "komorebi-indicator=src.main:main",
            ],
        },
    ) 