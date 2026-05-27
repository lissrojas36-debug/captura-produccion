import streamlit as st
from PIL import Image
import numpy as np

st.set_page_config(page_title="Calibrador de zonas", layout="wide")
st.title("🛠️ Calibrador de zonas del formato")

archivo = st.file_uploader("Sube la foto del formato", type=["jpg", "jpeg", "png"])

if archivo:
    imagen = Image.open(archivo)
    img = np.array(imagen)
    alto, ancho = img.shape[:2]

    st.write(f"Tamaño de imagen: {ancho} x {alto}")

    campos = [
        "Fecha de elaboración",
        "Maquinista",
        "Máquina No.",
        "Carretilla",
        "Código de rollo",
        "Tipo de bolsa",
        "Tamaño",
        "Enfajillador",
        "Número de fajillas",
        "Empacador",
        "Número de bultos",
    ]

    campo = st.selectbox("Selecciona el campo a calibrar", campos)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Imagen completa")
        st.image(imagen, use_container_width=True)

    with col2:
        st.subheader("Ajusta coordenadas")

        x1 = st.slider("x1 izquierda", 0, ancho, int(ancho * 0.45))
        y1 = st.slider("y1 arriba", 0, alto, int(alto * 0.20))
        x2 = st.slider("x2 derecha", 0, ancho, int(ancho * 0.95))
        y2 = st.slider("y2 abajo", 0, alto, int(alto * 0.30))

        if x2 > x1 and y2 > y1:
            recorte = img[y1:y2, x1:x2]
            st.subheader("Recorte")
            st.image(recorte, use_container_width=True)

            st.code(
                f'"{campo}": leer_zona(img, {x1}, {y1}, {x2}, {y2}),'
            )
