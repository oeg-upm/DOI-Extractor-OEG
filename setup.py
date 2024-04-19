from setuptools import setup, find_packages

setup(
    name="DataExtractorOEG",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "beautifulsoup4",
        "selenium",
        "requests",
        "pandas"
    ],
    entry_points={
        "console_scripts": [
            "DataExtractorOEG = main:main"
        ]
    },
)