import streamlit as st
from PIL import Image
import pytesseract
import mysql.connector
import pandas as pd
import re

# Configurar Tesseract
pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'

def extract_data_from_image(image):
    # Convertir imagen a texto usando OCR
    text = pytesseract.image_to_string(image)
    # Procesar texto para extraer precios y productos
    lines = text.split('\n')
    data = []
    for line in lines:
        match = re.match(r'(.+?)\s+(\d+,\d{2})', line)
        if match:
            product = match.group(1).strip()
            price = float(match.group(2).replace(',', '.'))
            data.append((product, price))
    return data

def insert_data_to_db(data):
    # Conexión a la base de datos MySQL
    conn = mysql.connector.connect(
        host='localhost',
        user='tu_usuario',  # Reemplaza con tu usuario de MySQL
        password='tu_contraseña',  # Reemplaza con tu contraseña de MySQL
        database='precios_supermercados'
    )
    cursor = conn.cursor()
    
    # Insertar datos en la tabla
    for item in data:
        cursor.execute("INSERT INTO productos (nombre, precio) VALUES (%s, %s)", item)
    
    conn.commit()
    cursor.close()
    conn.close()

def main():
    st.title("Comparador de Precios de Supermercados")
    st.write("Sube una foto de tu factura para extraer los precios y productos.")

    uploaded_file = st.file_uploader("Elige una imagen de tu factura", type=["jpg", "jpeg", "png"])
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption='Factura subida', use_column_width=True)

        data = extract_data_from_image(image)
        if data:
            df = pd.DataFrame(data, columns=['Producto', 'Precio'])
            st.write("Datos extraídos:")
            st.write(df)

            # Insertar datos en la base de datos
            insert_data_to_db(data)
            st.write("Datos almacenados en la base de datos.")
        else:
            st.write("No se encontraron datos en la imagen.")

if __name__ == "__main__":
    main()
