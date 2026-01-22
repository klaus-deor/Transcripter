"""Setup script for Transcripter."""

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
    # Filter out comments and empty lines
    requirements = [r.strip() for r in requirements if r.strip() and not r.startswith('#')]

setup(
    name="transcripter",
    version="1.0.0",
    author="Klaus Deor",
    author_email="",
    description="Audio transcription tool for Linux using Groq API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/klaus-deor/Transcripter",
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
    entry_points={
        'console_scripts': [
            'transcripter=transcripter.main:main',
        ],
    },
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
        "Operating System :: POSIX :: Linux",
    ],
    python_requires=">=3.8",
    keywords="transcription audio speech-to-text groq whisper",
)
