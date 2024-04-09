import requests
from bs4 import BeautifulSoup

# URL de la página web
url = "https://portalcientifico.upm.es/es/ipublic/item/4013521"

# Realizar la solicitud GET a la URL
response = requests.get(url)

# Verificar si la solicitud fue exitosa (código de estado 200)
if response.status_code == 200:
    # Extraer el contenido HTML de la respuesta
    html_doc = response.text

    # Parsear el HTML con Beautiful Soup
    soup = BeautifulSoup(html_doc, 'html.parser')

    # Encontrar todos los elementos <p> con la clase "card-text"
    card_texts = soup.find_all('p', class_='card-text')

    # Iterar sobre los elementos encontrados
    for card_text in card_texts:
        # Buscar el texto que contiene "doi:"
        doi_text = card_text.find('strong', string='doi:')
        if doi_text:
            # Extraer el DOI
            doi = doi_text.find_next_sibling(string=True).strip()
            print("DOI:", doi)
else:
    print("Error al cargar la página:", response.status_code)
