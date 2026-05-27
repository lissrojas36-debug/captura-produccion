import streamlit as st
from PIL import Image
from streamlit_cropper import st_cropper

st.set_page_config(page_title="Calibrar zonas", layout="wide")

st.title("🛠️ Calibrar zonas con cuadro movible")

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

archivo = st.file_uploader("Sube la foto", type=["jpg", "jpeg", "png"])

if "zonas" not in st.session_state:
    st.session_state.zonas = {}

if archivo:
    imagen = Image.open(archivo).convert("RGB")

    campo = st.selectbox("Selecciona el campo", campos)

    st.write("Mueve el cuadro sobre el dato escrito y guarda la zona.")

    box = st_cropper(
        imagen,
        realtime_update=True,
        box_color="#FF0000",
        aspect_ratio=None,
        return_type="box",
        key=campo
    )

    if box:
        x1 = int(box["left"])
        y1 = int(box["top"])
        x2 = int(box["left"] + box["width"])
        y2 = int(box["top"] + box["height"])

        recorte = imagen.crop((x1, y1, x2, y2))
        st.image(recorte, caption=f"Recorte de {campo}", use_container_width=True)

        if st.button("Guardar zona"):
            st.session_state.zonas[campo] = (x1, y1, x2, y2)
            st.success(f"Zona guardada: {campo}")

    st.subheader("Zonas guardadas")

    for nombre, coords in st.session_state.zonas.items():
        st.code(f'"{nombre}": leer_zona(img, {coords[0]}, {coords[1]}, {coords[2]}, {coords[3]}),')
