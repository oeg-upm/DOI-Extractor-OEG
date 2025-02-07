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
            title = "No title found"

        # Find all <p> elements in the class "card-text"
        card_texts = soup.find_all('p', class_='card-text')

        doi_found = False  # Flag to indicate if DOI is found
        # Iterate over the found elements
        for card_text in card_texts:
            # Search for <strong> with text "DOI:"
            doi_label = card_text.find('strong', string='DOI:')
            if doi_label:
                # The DOI is plain text after the <strong> element
                doi = doi_label.next_sibling.strip()
                if doi.startswith('https://doi.org/'):
                    doi = doi[len('https://doi.org/'):]  # Remove "https://doi.org/" from the beginning if present
                # Write the resulting DOI to the CSV file
                csv_file.writerow([title, doi])
                doi_found = True
                break  # Exit the loop since we found the DOI

        if not doi_found:
            csv_file.writerow([title, "No DOI found"])
        
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
        total_publications, publications_with_doi = 0, 0
        try:
            boton_publicaciones = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, "//span[@title='Publicaciones']"))
            )
            boton_publicaciones.click()
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "style-rfTitle"))
            )
            while True:
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                spans_rfTitle = soup.find_all("span", class_="style-rfTitle")
                for span in spans_rfTitle:
                    for enlace in span.find_all("a"):
                        url_completa = urllib.parse.urljoin(url_docs, enlace["href"])
                        doi_found = extract_doi(url_completa, csv_writer)
                        total_publications += 1
                        if doi_found:
                            publications_with_doi += 1
                print(f"Processed page. Total: {total_publications}, With DOI: {publications_with_doi}")
                try:
                    boton_siguiente = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Siguiente')]"))
                    )
                    if 'disabled' in boton_siguiente.get_attribute('class'):
                        print("'Siguiente' button is disabled. No more pages.")
                        break
                    boton_siguiente.click()
                    print("Navigating to next page...")
                except:
                    print("No more pages or 'Siguiente' button not found.")
                    break
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            driver.quit()
            print("WebDriver closed.")
        doi_percentage = (publications_with_doi / total_publications) * 100 if total_publications else 0
        print(f"Total Publications: {total_publications}, With DOI: {publications_with_doi}, DOI Percentage: {doi_percentage:.2f}%")
        

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


def find_file_by_name(name):
    package_path = pkg_resources.resource_filename(__name__, '')
    for root, dirs, files in os.walk(package_path):
        if name in files:
            print(f"Found existing papers")
            return os.path.join(root, name)