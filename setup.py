"""Setup script for Deor Transcripter."""

import sys
from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text() if readme_file.exists() else ""

# Read requirements
requirements_file = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_file.exists():
    requirements = requirements_file.read_text().splitlines()
    # Filter out comments, empty lines, and platform-specific optional deps
    requirements = [
        r.strip() for r in requirements
        if r.strip() and not r.startswith('#') and not r.startswith('# ')
    ]

# Platform-specific dependencies
extras_require = {
    'linux-gtk': [
        'python-xlib>=0.33',
    ],
    'windows': [
        'win10toast>=0.9',
    ],
}

# Determine entry points based on platform
entry_points = {
    'console_scripts': [
        'transcripter=transcripter.main:main',  # Linux GTK version
        'transcripter-cross=transcripter.main_cross:main',  # Cross-platform version
    ],
}

setup(
    name="deor-transcripter",
    version="1.0.0",
    author="Klaus Deor",
    author_email="",
    description="Cross-platform audio transcription tool with AI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/klaus-deor/Deor-Transcripter",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        'transcripter': [
            'gui/icons/*.png',
        ],
        '': [
            'config/*.toml',
        ],
    },
    install_requires=requirements,
    extras_require=extras_require,
    entry_points=entry_points,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Multimedia :: Sound/Audio :: Speech",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ],
    python_requires=">=3.8",
    keywords="transcription audio speech-to-text groq whisper cross-platform",
)
