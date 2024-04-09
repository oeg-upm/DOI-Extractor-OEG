with open("dois.txt", "r+") as archivo:
    # Leer todas las líneas del archivo
    lineas = archivo.readlines()
    
    # Volver al inicio del archivo
    archivo.seek(0)
    
    # Iterar sobre las líneas y escribir solo las que no están en blanco
    for linea in lineas:
        if linea.strip():
            archivo.write(linea)
    
    # Truncar el archivo para eliminar cualquier contenido restante
    archivo.truncate()