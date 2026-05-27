import streamlit as st
import pandas as pd
from PIL import Image
from io import BytesIO
from streamlit_cropper import st_cropper
import easyocr
import numpy as np

st.set_page_config(page_title="Recortar, calibrar y escanear", layout="wide")

st.title("📋 Recortar hoja, calibrar campos y escanear")

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

@st.cache_resource
def cargar_ocr():
    return easyocr.Reader(["es"], gpu=False)

reader = cargar_ocr()

if "recorte_general" not in st.session_state:
    st.session_state.recorte_general = None

if "zonas" not in st.session_state:
    st.session_state.zonas = {}

archivo = st.file_uploader("Sube la foto", type=["jpg", "jpeg", "png"])

def leer_zona(img, coords):
    x1, y1, x2, y2 = coords
    zona = img[y1:y2, x1:x2]
    resultado = reader.readtext(zona, detail=0, paragraph=True)
    return " ".join(resultado).strip()

if archivo:
    imagen = Image.open(archivo).convert("RGB")

    st.subheader("1️⃣ Recorta solo la hoja/formato")

    box_general = st_cropper(
        imagen,
        realtime_update=True,
        box_color="#FF0000",
        aspect_ratio=None,
        return_type="box",
        key="recorte_general_box"
    )

    if box_general:
        gx1 = int(box_general["left"])
        gy1 = int(box_general["top"])
        gx2 = int(box_general["left"] + box_general["width"])
        gy2 = int(box_general["top"] + box_general["height"])

        recorte_general = imagen.crop((gx1, gy1, gx2, gy2))

        st.image(recorte_general, caption="Hoja recortada", use_container_width=True)

        if st.button("✅ Usar este recorte"):
            st.session_state.recorte_general = recorte_general
            st.session_state.zonas = {}
            st.success("Recorte general guardado. Ahora calibra los campos.")

if st.session_state.recorte_general is not None:
    st.subheader("2️⃣ Calibra las zonas dentro del recorte")

    recorte_general = st.session_state.recorte_general

    campo = st.selectbox("Selecciona el campo", campos)

    box_campo = st_cropper(
        recorte_general,
        realtime_update=True,
        box_color="#00AAFF",
        aspect_ratio=None,
        return_type="box",
        key=f"campo_{campo}"
    )

    if box_campo:
        x1 = int(box_campo["left"])
        y1 = int(box_campo["top"])
        x2 = int(box_campo["left"] + box_campo["width"])
        y2 = int(box_campo["top"] + box_campo["height"])

        recorte_campo = recorte_general.crop((x1, y1, x2, y2))
        st.image(recorte_campo, caption=f"Recorte de {campo}", use_container_width=True)

        if st.button("💾 Guardar zona"):
            st.session_state.zonas[campo] = (x1, y1, x2, y2)
            st.success(f"Zona guardada: {campo}")

    st.subheader("Zonas guardadas")
    st.write(st.session_state.zonas)

    if st.button("🔍 Escanear zonas guardadas"):
        img = np.array(recorte_general)

        datos = {}
        for campo in campos:
            if campo in st.session_state.zonas:
                datos[campo] = leer_zona(img, st.session_state.zonas[campo])
            else:
                datos[campo] = ""

        st.subheader("3️⃣ Datos detectados")

        for campo in campos:
            datos[campo] = st.text_input(campo, datos[campo])

        df = pd.DataFrame([datos])
        st.dataframe(df, use_container_width=True)

        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Produccion")

        output.seek(0)

        st.download_button(
            "⬇ Descargar Excel",
            data=output,
            file_name="captura_produccion.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
