import os
import streamlit as st
import base64
from openai import OpenAI
import openai
from PIL import Image
import numpy as np
from streamlit_drawable_canvas import st_canvas

# ---------------- SESSION STATE ----------------
if 'base64_image' not in st.session_state:
    st.session_state.base64_image = ""

def encode_image_to_base64(image_path):
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")
    except FileNotFoundError:
        return ""

# ---------------- UI ----------------
st.set_page_config(page_title='Historias creativas con imagenes')
st.title('Historias creativas con imagenes')

st.info("""
Cómo funciona:
1. Dibuja algo
2. La IA lo convertirá en una historia

Ideas para dibujar:
- Una casa
- Un monstruo
- Un animal
- Objetos
""")

with st.sidebar:
    st.subheader("Configuración")
    stroke_width = st.slider('Ancho de línea', 1, 30, 5)

st.subheader("Dibuja en el panel y crea una historia")

# -------- TIPO DE HISTORIA --------
story_type = st.selectbox(
    "Tipo de historia:",
    ["Aventura", "Fantasía", "Comedia", "Misterio", "Suspenso", "Educativa"]
)

# -------- CANVAS --------
canvas_result = st_canvas(
    fill_color="rgba(255, 165, 0, 0.3)",
    stroke_width=stroke_width,
    stroke_color="#000000",
    background_color="#FFFFFF",
    height=300,
    width=400,
    drawing_mode="freedraw",
    key="canvas",
)

# -------- API --------
ke = st.text_input('Ingresa tu Clave', type="password")
os.environ['OPENAI_API_KEY'] = ke
api_key = os.environ['OPENAI_API_KEY']

client = OpenAI(api_key=api_key)

# -------- BOTÓN PRINCIPAL --------
if st.button("✨ Crear historia"):

    if canvas_result.image_data is None:
        st.warning("Dibuja algo primero")
    elif not api_key:
        st.warning("Falta API key")
    else:
        with st.spinner("Creando historia..."):

            # Convertir imagen
            img_array = np.array(canvas_result.image_data)
            img = Image.fromarray(img_array.astype('uint8')).convert('RGBA')
            img.save("img.png")

            base64_image = encode_image_to_base64("img.png")

            # -------- PROMPT FINAL --------
            prompt = f"""
            Observa la imagen y crea una historia infantil de tipo {story_type}.

            La historia debe:
            - Basarse en lo que ves en el dibujo
            - Tener inicio, desarrollo y final
            - Tener un personaje principal
            - Ser creativa y fácil de entender
            - Adaptarse al estilo {story_type}

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

# -------- WARNING --------
if not api_key:
    st.warning("Por favor ingresa tu API key.")
