import requests
import csv

def get_primary_location(name):
    search_url = "https://api.openalex.org/works?search="
    query_url = search_url + name

    response = requests.get(query_url)
    if response.status_code == 200:
        data = response.json()
        if data.get("results"):
            primary_location = data["results"][0]["primary_location"]
            if primary_location:
                landing_page_url = primary_location.get("landing_page_url")
                pdf_url = primary_location.get("pdf_url")
                # Check if either landing_page_url is a .pdf
                if landing_page_url and landing_page_url.endswith(".pdf"):
                    return landing_page_url
                # Check if there is a URL to a pdf
                elif pdf_url is not None and pdf_url != "null":
                    return pdf_url
                # If there is not a .pdf or a link to a .pdf, return the landing_page
                elif landing_page_url:
                    return landing_page_url
    return None


def add_primary_location_to_csv(csv_filename):
    with open(csv_filename, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        rows = list(reader)

    for row in rows:
        name = row["NAME"] 
        page_url = get_primary_location(name)
        if page_url:
            row["PRIMARY_LOCATION"] = page_url
            print(f"Searching in OpenAlex for {name}: {page_url}")
        else:
            row["PRIMARY_LOCATION"] = "None"
            print(f"Searching in OpenAlex for {name}: No primary location")

    new_columns = list(rows[0].keys())  
    if "PRIMARY_LOCATION" not in new_columns: 
        new_columns.append("PRIMARY_LOCATION")

    with open(csv_filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=new_columns)
        writer.writeheader()
        writer.writerows(rows)
