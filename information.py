import csv

total_publications = 0
publications_with_doi = 0

with open("dois.csv", "r", newline='', encoding='utf-8') as archivo_csv:

    csv_reader = csv.reader(archivo_csv)
    # Saltar la fila de encabezados
    next(csv_reader)
    
    for fila in csv_reader:
        total_publications += 1
        if fila[1]:  # Comprobar si hay DOI (índice 1)
            publications_with_doi += 1

porcentaje_doi = (publications_with_doi / total_publications) * 100 if total_publications != 0 else 0

print("Total de Publicaciones:", total_publications)
print("URLs con DOI:", publications_with_doi)
print("Porcentaje de Publicaciones con DOI: {:.2f}%".format(porcentaje_doi))