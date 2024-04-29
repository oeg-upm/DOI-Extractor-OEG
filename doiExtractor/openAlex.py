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
                
                # Check if either landing_page_url or pdf_url ends with ".pdf"
                if landing_page_url and landing_page_url.endswith(".pdf"):
                    return landing_page_url, doi
                elif pdf_url is not None:
                    return pdf_url, doi
                elif landing_page_url:
                    return landing_page_url, doi
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
                
                # Check if either landing_page_url or pdf_url ends with ".pdf"
                if landing_page_url and landing_page_url.endswith(".pdf"):
                    return landing_page_url, doi
                elif pdf_url is not None:
                    return pdf_url, doi
                elif landing_page_url:
                    return landing_page_url, doi
    return None, None


def add_primary_location_to_csv(csv_filename):
    with open(csv_filename, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        rows = list(reader)

    for row in rows:
        name = row["NAME"]
        doi = row["DOI"] 

        # If doi is None, add the doi founded in OpenAlex
        if doi == "None":
            page_url = get_primary_location_by_title(name, doi, include_doi=True)
            if page_url:
                row["DOI"] = page_url[1]
                print(f"Searching in OpenAlex for DOI of {name}: {page_url[1]}")
        else:
            page_url = get_primary_location_by_doi(name, doi)
        
        if page_url is not None:
            row["PRIMARY_LOCATION"] = page_url[0]
            print(f"Searching in OpenAlex for {name} \nFounded link:{page_url[0]}")
        else:
            row["PRIMARY_LOCATION"] = "None"
            print(f"Searching in OpenAlex for {name}: No primary location")
        print("-----------------------------------------------------------------")

    new_columns = list(rows[0].keys())  
    if "PRIMARY_LOCATION" not in new_columns: 
        new_columns.append("PRIMARY_LOCATION")

    with open(csv_filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=new_columns)
        writer.writeheader()
        writer.writerows(rows)

