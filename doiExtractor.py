from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

# Inicializar el navegador (por ejemplo, Chrome)
driver = webdriver.Chrome()

# URL de la página con el botón "Publicaciones"
url = "https://portalcientifico.upm.es/es/ipublic/entity/16247#14"

# Cargar la página
driver.get(url)

try:
    # Esperar a que el botón "Publicaciones" esté presente y sea clickeable
    boton_publicaciones = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Publicaciones')]"))
    )

    # Hacer clic en el botón "Publicaciones"
    boton_publicaciones.click()

    # Obtener el contenido HTML de la página después de hacer clic
    html_doc_despues_clic = driver.page_source
    
    # Parsear el HTML con Beautiful Soup
    soup_despues_clic = BeautifulSoup(html_doc_despues_clic, 'html.parser')

    # Encontrar todos los enlaces <a>
    enlaces = soup_despues_clic.find_all('a')

    # Iterar sobre los enlaces
    for enlace in enlaces:
        # Obtener la URL del enlace
        url_enlace = enlace.get('href')
        print(url_enlace)

        # Si la URL del enlace está presente y es diferente a la página actual
        if url_enlace and url_enlace != driver.current_url:
            # Realizar la solicitud GET a la URL del enlace
            driver.get(url_enlace)

            # Obtener el contenido HTML de la página del enlace
            html_doc_enlace = driver.page_source

            # Parsear el HTML del enlace con Beautiful Soup
            soup_enlace = BeautifulSoup(html_doc_enlace, 'html.parser')

            # Encontrar todos los elementos <p> con la clase "card-text"
            card_texts = soup_enlace.find_all('p', class_='card-text')

            # Iterar sobre los elementos encontrados
            for card_text in card_texts:
                # Buscar el texto que contiene "doi:"
                doi_text = card_text.find('strong', string='doi:')
                if doi_text:
                    # Extraer el DOI
                    doi = doi_text.find_next_sibling(string=True).strip()
                    print("DOI:", doi)

finally:
    # Cerrar el navegador al finalizar
    driver.quit()
