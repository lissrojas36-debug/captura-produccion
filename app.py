import streamlit as st
from PIL import Image, ImageDraw
import numpy as np

st.set_page_config(page_title="Ajustar zonas", layout="wide")

st.title("🛠️ Ajustar zonas por campo")

archivo = st.file_uploader("Sube la foto", type=["jpg", "jpeg", "png"])

ZONAS_BASE = {
    "Fecha de elaboración": (400, 320, 837, 393),
    "Maquinista": (400, 371, 834, 430),
    "Máquina No.": (400, 429, 834, 481),
    "Carretilla": (400, 481, 834, 535),
    "Código de rollo": (395, 524, 900, 595),
    "Tipo de bolsa": (395, 578, 900, 636),
    "Tamaño": (395, 633, 900, 689),
    "Enfajillador": (395, 780, 900, 872),
    "Número de fajillas": (395, 870, 900, 926),
    "Empacador": (395, 1044, 900, 1100),
    "Número de bultos": (395, 1087, 900, 1151),
}

COLORES = ["red", "blue", "green", "orange", "purple", "brown", "cyan", "magenta", "lime", "navy", "black"]

if archivo:
    imagen = Image.open(archivo).convert("RGB")
    ancho, alto = imagen.size

    campo = st.selectbox("Selecciona el campo que quieres mover", list(ZONAS_BASE.keys()))

    x1b, y1b, x2b, y2b = ZONAS_BASE[campo]

    x1 = st.slider("x1 izquierda", 0, ancho, min(x1b, ancho))
    y1 = st.slider("y1 arriba", 0, alto, min(y1b, alto))
    x2 = st.slider("x2 derecha", 0, ancho, min(x2b, ancho))
    y2 = st.slider("y2 abajo", 0, alto, min(y2b, alto))

    copia = imagen.copy()
    draw = ImageDraw.Draw(copia)

    for i, (nombre, coords) in enumerate(ZONAS_BASE.items()):
        color = COLORES[i % len(COLORES)]
        cx1, cy1, cx2, cy2 = coords

        if nombre == campo:
            cx1, cy1, cx2, cy2 = x1, y1, x2, y2

        draw.rectangle((cx1, cy1, cx2, cy2), outline=color, width=5)
        draw.text((cx1, max(0, cy1 - 20)), nombre, fill=color)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Vista con zonas")
        st.image(copia, use_container_width=True)

    with col2:
        st.subheader("Recorte actual")
        if x2 > x1 and y2 > y1:
            recorte = imagen.crop((x1, y1, x2, y2))
            st.image(recorte, use_container_width=True)

            st.code(f'"{campo}": ({x1}, {y1}, {x2}, {y2}),')
