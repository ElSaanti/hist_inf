import os
import streamlit as st
import base64
from openai import OpenAI
import openai
from PIL import Image
import numpy as np
from streamlit_drawable_canvas import st_canvas

Expert=" "
profile_imgenh=" "

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
        return "Error: La imagen no se encontró."

# ---------------- UI ----------------
st.set_page_config(page_title='Tablero Inteligente')
st.title('Tablero Inteligente')

# ✅ (1) Explicación + ideas
st.info("""
Cómo funciona:
1. Dibuja algo (personaje, objeto, escena)
2. La IA lo interpretará
3. Luego podrás convertirlo en una historia infantil

Ideas para dibujar:
- Un dragón 🐉
- Un robot 🤖
- Una casa mágica 🏠
- Un monstruo divertido 👾
""")

with st.sidebar:
    st.subheader("Acerca de:")
    st.write("Esta app interpreta dibujos y crea historias.")

st.subheader("Dibuja el boceto en el panel y presiona analizar")

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

analyze_button = st.button("Analiza la imagen")

# ---------------- ANÁLISIS ----------------
if canvas_result.image_data is not None and api_key and analyze_button:

    with st.spinner("Analizando..."):
        input_numpy_array = np.array(canvas_result.image_data)
        input_image = Image.fromarray(input_numpy_array.astype('uint8')).convert('RGBA')
        input_image.save('img.png')

        base64_image = encode_image_to_base64("img.png")
        st.session_state.base64_image = base64_image

        # ✅ (2) Prompt mejorado
        prompt_text = """
        Describe en español lo que ves en la imagen de forma clara.

        Incluye:
        - Qué es el objeto o personaje
        - Estilo del dibujo (infantil, simple, boceto, etc.)
        - Posible contexto o situación

        Sé breve pero descriptivo.
        """

        try:
            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt_text},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{base64_image}",
                                },
                            },
                        ],
                    }
                ],
                max_tokens=300,
            )

            full_response = response.choices[0].message.content

            # ✅ (5) Mostrar mejor el análisis
            st.markdown("### 🧠 Interpretación del dibujo")
            st.success(full_response)

            st.session_state.full_response = full_response
            st.session_state.analysis_done = True

        except Exception as e:
            st.error(f"Error: {e}")

# ---------------- HISTORIA ----------------
if st.session_state.analysis_done:
    st.divider()
    st.subheader("📚 Crear historia")

    # ✅ (4) Tipo de historia
    story_type = st.selectbox(
        "Tipo de historia:",
        ["Aventura", "Fantasía", "Comedia", "Misterio", "Educativa"]
    )

    if st.button("✨ Crear historia infantil"):
        with st.spinner("Creando historia..."):

            # ✅ (3) Prompt mejorado
            story_prompt = f"""
            Crea una historia infantil de tipo {story_type} basada en:

            {st.session_state.full_response}

            Debe:
            - Tener inicio, desarrollo y final
            - Tener un personaje principal claro
            - Ser creativa y fácil de entender
            - Tener tono divertido o mágico

            Opcional: incluye una enseñanza al final.
            """

            story_response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": story_prompt}],
                max_tokens=500,
            )

            st.markdown("### 📖 Tu historia")
            st.write(story_response.choices[0].message.content)

    # ✅ (6) Regenerar historia
    if st.button("🔄 Generar otra versión"):
        st.session_state.analysis_done = True

# Warnings
if not api_key:
    st.warning("Por favor ingresa tu API key.")
