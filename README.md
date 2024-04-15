# DOI-Extractor-OEG

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://opensource.org/licenses/MIT)

## Description

DOI-Extractor-OEG is a tool for extracting all paper's name and DOI from OEG publications.

They are extracted from two main resources:

1) https://portalcientifico.upm.es/es/ipublic/entity/16247 , corresponding to all papers from OEG.

2) ExistingPapers/ Papers.csv with already extracted data from some OEG papers.

<br>
The resulting information is placed in Outputs folder, which include:

- A dois.txt containing all the dois from the two resources

- A name-doi.csv, containing the title and the doi of every paper found

## Project Structure
```
DOI-Extractor-OEG
├───ExistingPapers
|   ├───name_doi_papers.csv
|   └───Papers.csv
├───Outputs
|   ├───dois.csv
|   └───name_doi.csv
├───.gitignore
├───doiExtractor.py
├───LICENSE.txt
├───main.py
├───README.MD
└───setup.py
```

```doiExtractor.py``` - Contains the functions to extract data from the NBA website

## Installation

1. Clone the repository:
```git clone https://github.com/ptorija/DOI-Extractor-OEG.git```

2. Change to the NbaSeasonStats directory:
```cd DOI-Extractor-OEG```

3. Create a virtual environment:
```python -m venv .env```

4. Activate the virtual environment:
```source .env/bin/activate``` (Linux) or ```.env\Scripts\activate``` (Windows)

5. Install the package dependencies (Selenium, Matplotlib, Pandas):
```pip install -e .```

## Usage
The tool can be used from the command line with the following argument:
- ```--start``` - To start the doi extraction 

The script will execute and extract DOIs from the specified webpage and then merge them with the ones from ExistingPapers.

### Example
- ```DataExtractorOEG --start```