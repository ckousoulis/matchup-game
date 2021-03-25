"""A setuptools module for Matchup Game.
"""

from pathlib import Path
from setuptools import find_packages, setup

setup(
    name="matchup-game",
    version="1.0.0b1",
    license="MIT",
    description="CLI for matchup-based games",
    long_description=Path("README.rst").read_text(),
    author="Constantine Kousoulis",
    author_email="constantine@kousoulis.org",
    url="https://github.com/ckousoulis/matchup-game",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "matchup-game = matchup_game.__main__:main",
        ],
    },
    python_requires="~=3.8",
    install_requires=["pyyaml"],
    keywords="cli game",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Games/Entertainment",
    ],
)