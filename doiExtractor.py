from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import urllib.parse
import requests
import csv


# Function to extract the DOI
def extract_doi(url_pagina, csv_file, txt_file):
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
                    # Write the resulting DOI to the CSV file
                    csv_file.writerow([title, doi])
                    txt_file.write(doi + '\n')
                    doi_found = True
                else:
                    csv_file.writerow([title, " "])
                    doi_found = False
                    
        return doi_found  # Return if DOI is found or not
    else:
        print("Error loading the webpage:", response.status_code)
        return False


# Function to merge two CSV files
def merge_csv(csv1, csv2, existing_txt):
    existing_dois = set()

    # Collect DOIs from name-doi.csv
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
            csv_writer = csv.writer(existing_csv_file)
            with open(existing_txt, 'a', encoding='utf-8') as existing_txt_file:
                for row in reader:
                    doi = row[1]
                    if doi not in existing_dois:
                        csv_writer.writerow(row)
                        existing_txt_file.write(doi + '\n')


driver = webdriver.Chrome()

# URL of the page with the "Publicaciones" button clicked
url = "https://portalcientifico.upm.es/es/ipublic/entity/16247#14"

# URL to concatenate with the founded publications
url_docs = "https://portalcientifico.upm.es/es/ipublic/entity/16247"

driver.get(url)

with open("Outputs/name-doi.csv", "w", newline='', encoding='utf-8') as csv_file:
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(["NAME", "DOI"])

    with open("Outputs/dois.txt", "w") as txt_file:
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
                        doi_found = extract_doi(url_completa, csv_writer, txt_file)
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


# Merge the dois obtained with the existing from Papers.csv
csv1 = 'Outputs/name-doi.csv'
csv2 = 'ExistingPapers/name-doi-papers.csv'
existing_txt = 'Outputs/dois.txt'

merge_csv(csv1, csv2, existing_txt)
