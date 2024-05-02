from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="DataExtractorOEG",
    version="0.4.2",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "beautifulsoup4",
        "selenium",
        "requests",
        "pandas"
    ],
    entry_points={
        "console_scripts": [
            "DataExtractorOEG = doiExtractor:cli"
        ]
    },
    long_description= long_description,
    long_description_content_type="text/markdown"
)