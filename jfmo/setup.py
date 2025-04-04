#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import re

with open("jfmo/__init__.py", "r") as f:
    version = re.search(r'__version__\s*=\s*"(.*?)"', f.read()).group(1)

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="jfmo",
    version=version,
    author="Your Name",
    author_email="your.email@example.com",
    description="Jellyfin Format Media Organizer",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/jellyfin-format-media-organizer",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Topic :: Multimedia :: Video",
        "Topic :: Utilities",
    ],
    python_requires=">=3.6",
    install_requires=[
        "transliterate>=1.10.0",
    ],
    entry_points={
        "console_scripts": [
            "jfmo=jfmo.__main__:main",
        ],
    },
)
