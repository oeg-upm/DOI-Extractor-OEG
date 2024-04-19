from doiExtractor import search_papers, merge_csv, remove_duplicates
from openAlex import add_primary_location_to_csv, create_txt_with_dois
import argparse
import logging
import os

from doiExtractor import search_papers, merge_csv

logging.basicConfig(level=logging.INFO)

def main():
    parser = argparse.ArgumentParser(description="DOI Extractor Tool")
    parser.add_argument("--start", action="store_true", help="Start the extraction process")
    args = parser.parse_args()

    if args.start:
        # URL of the page with the "Publicaciones" button clicked
        url = "https://portalcientifico.upm.es/es/ipublic/entity/16247#14"
        # URL to concatenate with the founded publications
        url_docs = "https://portalcientifico.upm.es/es/ipublic/entity/16247"

        # Files to write the output
        csv_filename = "Outputs/name_doi.csv"
        txt_filename = "Outputs/dois.txt"

        # ExistingPapers
        papers = "ExistingPapers/name_doi_papers.csv"

        logging.info("DOI Extractor Tool started")
        logging.info(f"Search in: {url}, Output csv: {csv_filename}, Output txt: {txt_filename}")

        # Delete contents of the files
        if os.path.exists(csv_filename):
            open(csv_filename, 'w').close()
        if os.path.exists(txt_filename):
            open(txt_filename, 'w').close()

        # Extract dois from url
        search_papers(url, url_docs, csv_filename)

        # Merge them with the existing from the papers
        merge_csv(csv_filename, papers)

        # Check for duplicated dois after the merge
        remove_duplicates(csv_filename)

        # Add URLs from OpenAlex
        add_primary_location_to_csv(csv_filename)

        #After adding missing dois with OpenAlex, create the .txt file containing all the dois
        create_txt_with_dois(csv_filename, txt_filename)

        logging.info(f"Data saved to {csv_filename} and {txt_filename}")
    else:
        logging.info("Use --start flag to start the extraction process")


if __name__ == "__main__":
    main()
