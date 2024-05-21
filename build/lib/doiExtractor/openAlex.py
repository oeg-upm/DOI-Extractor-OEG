import requests
import csv
from urllib.parse import urlparse

def get_primary_location_by_doi(name, doi):
    search_url = "https://api.openalex.org/works/https://doi.org/"
    query_url = search_url + doi
    response = requests.get(query_url)
    if response.status_code == 200:
        data = response.json()
        if data.get("id"):
            primary_location = data.get("primary_location")
            if primary_location:
                landing_page_url = primary_location.get("landing_page_url")
                pdf_url = primary_location.get("pdf_url")
                
                # Check both URLs for 'application/pdf' content type
                if landing_page_url:
                    checked_landing_page_url = check_pdf(landing_page_url)
                    if checked_landing_page_url:
                        print(f"Found PDF for {doi}: {checked_landing_page_url}")
                        return checked_landing_page_url, doi

                if pdf_url:
                    checked_pdf_url = check_pdf(pdf_url)
                    if checked_pdf_url:
                        print(f"Found PDF for {doi}: {checked_pdf_url}")
                        return checked_pdf_url, doi
                    
                else: 
                    print(f"No PDF found for {doi}")
                    return None ,doi
    else:
        return get_primary_location_by_title(name, doi)



def get_primary_location_by_title(name, doi, include_doi=False):
    search_url = "https://api.openalex.org/works?filter=title.search:"
    query_url = search_url + name
    response = requests.get(query_url)
    if response.status_code == 200:
        data = response.json()
        if data.get("results"):
            primary_location = data["results"][0]["primary_location"]
            if primary_location:
                landing_page_url = primary_location.get("landing_page_url")
                pdf_url = primary_location.get("pdf_url")

                #If doi is not in the csv, search for it in OpenAlex
                if include_doi:
                    doi_full = data["results"][0].get("doi")
                    if doi_full is not None:
                        parsed_url = urlparse(doi_full) if doi_full else None
                        if parsed_url.path:
                            doi = parsed_url.path.strip("/")  # Extract the DOI number from the DOI URL
                        else:
                            doi = None
                    else:
                        doi = None
                else:
                    doi = None
                
                # Check both URLs for 'application/pdf' content type
                if landing_page_url:
                    checked_landing_page_url = check_pdf(landing_page_url)
                    if checked_landing_page_url:
                        print(f"Found PDF for {name}: {checked_landing_page_url}")
                        return checked_landing_page_url, doi

                if pdf_url:
                    checked_pdf_url = check_pdf(pdf_url)
                    if checked_pdf_url:
                        print(f"Found PDF for {name}: {checked_pdf_url}")
                        return checked_pdf_url, doi
                     
                print(f"No PDF found for {name}")
                return None ,doi
    return None, None


def add_primary_location_to_csv(csv_filename):
    with open(csv_filename, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        rows = list(reader)

    for row in rows:
        name = row["title"]
        doi = row["doi"] 

        # If doi is None, add the doi founded in OpenAlex
        if doi == "":
            page_url = get_primary_location_by_title(name, doi, include_doi=True)
            if page_url[1] is not None:
                row["doi"] = page_url[1]
        else:
            page_url = get_primary_location_by_doi(name, doi)
        
        if page_url and page_url[0] is not None:
            row["primary_location"] = page_url[0]
        else:
            row["primary_location"] = ""
            if doi:
                print(f"No primary location for {doi}")
            else:
                if name:
                    print(f"No primary location for {name}")  
        print("-----------------------------------------------------------------")

    new_columns = list(rows[0].keys())  
    if "primary_location" not in new_columns: 
        new_columns.append("primary_location")

    with open(csv_filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, quoting=csv.QUOTE_ALL, fieldnames=new_columns)
        writer.writeheader()
        writer.writerows(rows)


def check_pdf(url):
        try:
            response = requests.head(url, allow_redirects=True)
            response.raise_for_status()
            content_type = response.headers.get('Content-Type')
            if content_type == 'application/pdf':
                return url
        except requests.exceptions.RequestException as e:
            print(f"Error checking URL {url}: {e}")
        return None