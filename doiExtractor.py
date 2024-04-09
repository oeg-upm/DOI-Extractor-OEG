from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import urllib.parse
import requests
import csv


# Función para extraer los DOI
def extraer_doi(url_pagina, archivo_csv):
    # Realizar la solicitud GET a la URL
    response = requests.get(url_pagina)

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
                # Escribir la URL y el DOI en el archivo CSV
                archivo_csv.writerow([url_pagina, doi])
    else:
        print("Error al cargar la página:", response.status_code)

    
driver = webdriver.Chrome()

# URL de la página con el botón "Publicaciones"
url = "https://portalcientifico.upm.es/es/ipublic/entity/16247#14"

# URL para concatenar las publicaciones encontradas
url_docs = "https://portalcientifico.upm.es/es/ipublic/entity/16247"

# Cargar la página
driver.get(url)

with open("dois.csv", "w", newline='', encoding='utf-8') as archivo_csv:

    csv_writer = csv.writer(archivo_csv)
    csv_writer.writerow(["URL", "DOI"])

    try:
        
        # Esperar a que el botón "Publicaciones" esté presente y sea clickeable
        boton_publicaciones = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Publicaciones')]"))
        )

        # Hacer clic en el botón "Publicaciones"
        boton_publicaciones.click()

        # Esperar a que la página cargue después de hacer clic en el botón
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "style-rfTitle"))
        )
        while True:
            # Obtener el contenido HTML de la página después de hacer clic
            html_doc_despues_clic = driver.page_source

            # Parsear el HTML con Beautiful Soup
            soup_despues_clic = BeautifulSoup(html_doc_despues_clic, 'html.parser')

            # Buscar y extraer DOI en la página actual
            spans_rfTitle = soup_despues_clic.find_all("span", class_="style-rfTitle")
            for span in spans_rfTitle:
                enlaces = span.find_all("a")
                for enlace in enlaces:
                    fragmento_enlace = enlace["href"]
                    url_completa = urllib.parse.urljoin(url_docs, fragmento_enlace)
                    extraer_doi(url_completa, csv_writer)

            # Buscar y hacer clic en el botón "Siguiente"
            boton_siguiente = driver.find_element(By.XPATH, "//a[contains(text(), 'Siguiente')]")
            if not boton_siguiente.is_enabled():
                break  # Salir del bucle si no hay más páginas
            boton_siguiente.click()

    except Exception as e:
        print("Ocurrió un error:", e)
    finally:
        driver.quit()
