import pkg_resources
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import urllib.parse
import requests
import csv
import os

# Function to extract the DOI
def extract_doi(url_pagina, csv_file):
    response = requests.get(url_pagina)

    if response.status_code == 200:
        # Extract HTML content of the page
        html_doc = response.text

        # Parse the HTML with Beautiful Soup
        soup = BeautifulSoup(html_doc, 'html.parser')

        # Find the publication's title in the class "card-title"
        title = soup.find('h2', class_='card-title')
        if title:
            title = title.text.strip()
        else:
            print("No title found")

        # Find all <p> elements in the class "card-text"
        card_texts = soup.find_all('p', class_='card-text')

        doi_found = False  # Flag to indicate if DOI is found
        # Iterate over the found elements
        for card_text in card_texts:
            # Search for "doi:"
            doi_text = card_text.find('strong', string='doi:')
            if doi_text:
                # Check if there is text after "doi:"
                next_sibling = doi_text.find_next_sibling(string=True)
                if next_sibling and next_sibling.strip():
                    # Extract DOI
                    doi = next_sibling.strip()
                    if doi.startswith('https://doi.org/'):
                        doi = doi[len('https://doi.org/'):]  # Remove "https://doi.org/" from the beginning if present
                    # Write the resulting DOI to the CSV file
                    csv_file.writerow([title, doi])
                    doi_found = True
                else:
                    csv_file.writerow([title, ""])
                    doi_found = False
                    
        return doi_found  # Return if DOI is found or not
    else:
        print("Error loading the webpage:", response.status_code)
        return False


# Function to search for papers in the webpage
def search_papers(url, url_docs, csv_filename):

    driver = webdriver.Chrome()
    driver.get(url)

    with open(csv_filename, "w", newline='', encoding='utf-8') as csv_file:
        csv_writer = csv.writer(csv_file, quoting=csv.QUOTE_ALL)
        csv_writer.writerow(["title", "doi"])

        total_publications = 0
        publications_with_doi = 0

        try:
            # Wait until "Publicaciones" button is clickable
            boton_publicaciones = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Publicaciones')]"))
            )

            # Click on "Publicaciones" button
            boton_publicaciones.click()

            # Wait for the webpage to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "style-rfTitle"))
            )

            while True:
                # Extract HTML content of the page after the click
                html_doc_despues_clic = driver.page_source

                # Parse the HTML with Beautiful Soup
                soup_despues_clic = BeautifulSoup(html_doc_despues_clic, 'html.parser')

                # Extract DOI
                spans_rfTitle = soup_despues_clic.find_all("span", class_="style-rfTitle")
                for span in spans_rfTitle:
                    enlaces = span.find_all("a")
                    for enlace in enlaces:
                        fragmento_enlace = enlace["href"]
                        url_completa = urllib.parse.urljoin(url_docs, fragmento_enlace)
                        doi_found = extract_doi(url_completa, csv_writer)
                        total_publications += 1
                        if doi_found:
                            publications_with_doi += 1

                # Go to the next page clicking on "Siguiente"
                boton_siguiente = driver.find_element(By.XPATH, "//a[contains(text(), 'Siguiente')]")
                if not boton_siguiente.is_enabled():
                    break  # End if there are no more pages
                boton_siguiente.click()

        except Exception as e:
            print("An error occurred:", e)
        finally:
            driver.quit()

        # Calculate the percentage of publications with DOI
        doi_percentage = (publications_with_doi / total_publications) * 100 if total_publications != 0 else 0

        print("Total de Publicaciones:", total_publications)
        print("URLs con DOI:", publications_with_doi)
        print("Porcentaje de Publicaciones con DOI: {:.2f}%".format(doi_percentage))


def remove_duplicates(csv_file):
    df = pd.read_csv(csv_file, quoting=csv.QUOTE_ALL)
    
    # Drop duplicate rows based on the specified column
    df.drop_duplicates(subset=['title'], keep='first', inplace=True)
    
    # Write the modified DataFrame back to the CSV file
    df.to_csv(csv_file, index=False, quoting=csv.QUOTE_ALL)


# Function to merge two CSV files
def merge_csv(csv1, csv2):
    existing_dois = set()

    # Collect DOIs from results.csv
    with open(csv1, 'r', newline='', encoding='utf-8') as existing_file:
        reader = csv.reader(existing_file)
        next(reader)  # Skip header row
        for row in reader:
            doi = row[1]
            existing_dois.add(doi)

    with open(csv2, 'r', newline='', encoding='utf-8') as papers_file:
        reader = csv.reader(papers_file)
        next(reader)  # Skip header row
        with open(csv1, 'a', newline='', encoding='utf-8') as existing_csv_file:
            csv_writer = csv.writer(existing_csv_file, quoting=csv.QUOTE_ALL)
            for row in reader:
                doi = row[1]
                if doi not in existing_dois:
                    csv_writer.writerow(row)


def create_txt(csv_filename, txt_filename):
    print("\nCreating the .txt with the .pdf or doi\n")
    with open(csv_filename, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        with open(txt_filename, mode='w', encoding='utf-8') as output_file:
            for row in reader:
                name = row.get("title")
                doi = row.get("doi")
                primary_location = row.get("primary_location")
                if primary_location != "":
                    try:
                        response = requests.head(primary_location, allow_redirects=True)
                        final_url = response.url
                        parsed_url = urllib.parse.urlparse(final_url)
                        if parsed_url.path.endswith('.pdf'):
                            output_file.write(primary_location + "\n")
                            print(f"Found pdf for {name}: {primary_location}")
                            print("-----------------------------------------------------------------")
                            continue
                        else:
                            if doi != "" and doi.startswith('10'):
                                output_file.write(doi + "\n")
                                print(f"No pdf found for {name}, wrote DOI instead: {doi}")
                            else:
                                print(f"No pdf or DOI found for {name}")
                    except requests.RequestException:
                        pass
                elif doi != "" and doi.startswith('10'):
                    output_file.write(doi + "\n")
                    print(f"No pdf found for {name}, wrote DOI instead: {doi}")
                else:
                    print(f"No pdf or DOI found for {name}")
                print("-----------------------------------------------------------------")


def csv_to_json(csv_file, json_file):
    df = pd.read_csv(csv_file)
    df.to_json(json_file, orient='records', indent=4)


def find_file_by_name(path, name):
    package_path = pkg_resources.resource_filename(__name__, '')
    for root, dirs, files in os.walk(package_path):
        if name in files:
            print(f"Found existing papers")
            return os.path.join(root, name)