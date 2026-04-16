import os
import streamlit as st
import base64
from openai import OpenAI
import openai
from PIL import Image
import numpy as np
from streamlit_drawable_canvas import st_canvas

# Inicializar session_state
if 'analysis_done' not in st.session_state:
    st.session_state.analysis_done = False
if 'full_response' not in st.session_state:
    st.session_state.full_response = ""
if 'base64_image' not in st.session_state:
    st.session_state.base64_image = ""

def encode_image_to_base64(image_path):
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")
    except FileNotFoundError:
        return ""

# ---------------- UI ----------------
st.set_page_config(page_title='Tablero Inteligente')
st.title('Tablero Inteligente')

# ✅ Explicación + nuevas ideas
st.info("""
Cómo funciona:
1. Dibuja algo
2. La IA lo usará para crear una historia

Ideas para dibujar:
- Una casa
- Un monstruo
- Un animal
- Objetos
""")

with st.sidebar:
    st.subheader("Acerca de:")
    st.write("Dibuja y crea historias automáticamente.")

st.subheader("Dibuja en el panel y crea una historia")

# Canvas config
drawing_mode = "freedraw"
stroke_width = st.sidebar.slider('Ancho de línea', 1, 30, 5)
stroke_color = "#000000"
bg_color = "#FFFFFF"

canvas_result = st_canvas(
    fill_color="rgba(255, 165, 0, 0.3)",
    stroke_width=stroke_width,
    stroke_color=stroke_color,
    background_color=bg_color,
    height=300,
    width=400,
    drawing_mode=drawing_mode,
    key="canvas",
)

# API Key
ke = st.text_input('Ingresa tu Clave', type="password")
os.environ['OPENAI_API_KEY'] = ke
api_key = os.environ['OPENAI_API_KEY']

client = OpenAI(api_key=api_key)

# ---------------- CREAR HISTORIA DIRECTO ----------------
if st.button("✨ Crear historia"):

    if canvas_result.image_data is None:
        st.warning("Dibuja algo primero")
    elif not api_key:
        st.warning("Falta API key")
    else:
        with st.spinner("Creando historia..."):

            input_numpy_array = np.array(canvas_result.image_data)
            input_image = Image.fromarray(input_numpy_array.astype('uint8')).convert('RGBA')
            input_image.save('img.png')

            base64_image = encode_image_to_base64("img.png")

            prompt = """
            Observa la imagen y crea directamente una historia infantil.

            La historia debe:
            - Basarse en lo que ves en el dibujo
            - Tener inicio, desarrollo y final
            - Tener un personaje principal
            - Ser creativa y fácil de entender
            - Tener un tono divertido o mágico

            No expliques la imagen, solo escribe la historia.
            """

            try:
                response = openai.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": prompt},
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/png;base64,{base64_image}",
                                    },
                                },
                            ],
                        }
                    ],
                    max_tokens=500,
                )

                st.markdown("### 📖 Tu historia")
                st.write(response.choices[0].message.content)

            except Exception as e:
                st.error(f"Error: {e}")

# Warning
if not api_key:
    st.warning("Por favor ingresa tu API key.")
