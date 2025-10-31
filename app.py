# -*- coding: utf-8 -*-
import os
import time
import glob
import base64
import platform
import re
import streamlit as st
from gtts import gTTS
from PIL import Image

# =========================
# Configuración de página
# =========================
st.set_page_config(
    page_title="🧠🔊 Text-to-Speech | Tech Mode",
    page_icon="🎧",
    layout="centered",
    initial_sidebar_state="expanded"
)

# =========================
# Estilos Tech (oscuro + neón)
# =========================
st.markdown("""
<style>
  :root {
    --bg:#0b1220;
    --panel:#0f182b;
    --text:#e6f7ff;
    --muted:#9fb3c8;
    --accent:#00e5ff;
    --accent2:#00ffa3;
  }
  html, body, .stApp {
    background: radial-gradient(1000px 600px at 10% 0%, #0f1a30 0%, var(--bg) 60%);
    color: var(--text) !important;
  }
  [data-testid="stSidebar"], section[data-testid="stSidebar"] > div{
    background: linear-gradient(180deg, #0e1628 0%, #0b1220 100%) !important;
    color: var(--text) !important;
    border-right: 1px solid rgba(0,229,255,.15);
  }
  h1, h2, h3, h4, h5, h6 {
    color: var(--accent);
    font-family: "JetBrains Mono", monospace;
    letter-spacing: .5px;
  }
  p, label, span, div, .stMarkdown {
    color: var(--text) !important;
    font-family: "Inter", system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif;
  }
  .stButton>button {
    background: linear-gradient(90deg, var(--accent) 0%, var(--accent2) 100%) !important;
    color: #00121a !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 700 !important;
    transition: transform .08s ease-in-out, box-shadow .2s ease-in-out;
    box-shadow: 0 0 12px rgba(0,229,255,.5);
  }
  .stButton>button:hover {
    transform: translateY(-1px);
    box-shadow: 0 0 18px rgba(0,229,255,.75);
  }
  textarea, input, .stTextInput>div>div>input {
    background: #0f182b !important;
    color: var(--text) !important;
    border: 1px solid rgba(0,229,255,.3) !important;
    border-radius: 10px !important;
  }
  .stExpander {
    background: var(--panel) !important;
    border: 1px solid rgba(0,229,255,.2);
    border-radius: 10px;
  }
</style>
""", unsafe_allow_html=True)

# =========================
# Encabezado
# =========================
st.title("🎧 Text-to-Speech | Tech Mode")
st.caption(f"💻 Python: `{platform.python_version()}` · gTTS · Streamlit")

# Banner/imagen opcional
try:
    banner = Image.open("gato_raton.png")
    st.image(banner, width=360, caption="🐭📘 Fábula · Kafka (demo)")
except Exception as e:
    st.warning(f"⚠️ Imagen no cargada: {e}")

# =========================
# Sidebar
# =========================
with st.sidebar:
    st.subheader("🗣️ ¿Qué hace esta app?")
    st.markdown("""
- Convierte **texto** en **audio MP3** con **gTTS**  
- Soporta **Español** e **Inglés**  
- Descarga directa del archivo  
- Limpia MP3 antiguos automáticamente  
    """)
    st.markdown("**Tip:** Pega texto largo o usa el demo de la fábula 📘")

# =========================
# Utilidades
# =========================
def ensure_temp_dir(path="temp"):
    try:
        os.makedirs(path, exist_ok=True)
    except Exception as e:
        st.error(f"❌ No se pudo crear el directorio temporal: {e}")

def sanitize_filename(text: str, default="audio"):
    """Crea un nombre de archivo seguro a partir del texto."""
    if not text:
        return default
    # primeras 30 letras/números/espacios → guiones
    base = re.sub(r"[^A-Za-z0-9 _-]", "", text[:30]).strip().replace(" ", "_")
    return base or default

def text_to_speech(text: str, lang: str = "es", tld: str = "com", slow: bool = False, outdir: str = "temp"):
    """Convierte texto a audio con gTTS y devuelve ruta del archivo."""
    if not text or not text.strip():
        raise ValueError("El texto está vacío.")
    ensure_temp_dir(outdir)
    filename = sanitize_filename(text)
    out_path = os.path.join(outdir, f"{filename}.mp3")
    tts = gTTS(text=text, lang=lang, tld=tld, slow=slow)
    tts.save(out_path)
    return out_path

def remove_old_files(days: int = 7, pattern: str = "temp/*.mp3"):
    """Elimina MP3 más antiguos que N días."""
    mp3_files = glob.glob(pattern)
    if not mp3_files:
        return
    now = time.time()
    threshold = days * 86400
    for f in mp3_files:
        try:
            if os.stat(f).st_mtime < now - threshold:
                os.remove(f)
        except Exception:
            pass

# Limpieza programada
remove_old_files(7)

# =========================
# Demo de fábula
# =========================
FABULA = (
    "¡Ay! —dijo el ratón—. El mundo se hace cada día más pequeño. "
    "Al principio era tan grande que le tenía miedo. Corría y corría y me alegraba ver los muros a diestra y siniestra, "
    "a lo lejos. Pero esas paredes se estrechan tan rápido que me encuentro en el último cuarto y, en el rincón, "
    "está la trampa sobre la cual debo pasar. —Todo lo que debes hacer es cambiar de rumbo— dijo el gato… y se lo comió. "
    "Franz Kafka."
)

st.subheader("📘 Demo: Una pequeña fábula")
st.markdown("Si quieres probar rápido, usa el texto de ejemplo o pega el tuyo.")

col_demo_a, col_demo_b = st.columns(2)
use_demo = col_demo_a.toggle("Usar fábula de ejemplo", value=False)
slow_voice = col_demo_b.toggle("Voz lenta (slow)", value=False)

# =========================
# Entrada de texto
# =========================
st.subheader("✍️ Texto a convertir")
if use_demo:
    text = st.text_area("Ingresa el texto a escuchar:", value=FABULA, height=180)
else:
    text = st.text_area("Ingresa el texto a escuchar:", placeholder="Pega aquí tu texto…", height=180)

# =========================
# Configuración de voz
# =========================
st.subheader("⚙️ Configuración de voz")
col1, col2, col3 = st.columns(3)
with col1:
    option_lang = st.selectbox("Idioma", ("Español", "English"), index=0)
with col2:
    # tld puede cambiar acento/región en gTTS
    tld = st.selectbox("TLD (acento/servidor)", ("com", "com.mx", "es", "co.uk", "com.au"), index=0)
with col3:
    filename_hint = st.text_input("Nombre base del archivo (opcional)", value="audio")

lang_code = "es" if option_lang == "Español" else "en"

# =========================
# Botón de conversión
# =========================
if st.button("🚀 Convertir a Audio (MP3)"):
    try:
        if not text or not text.strip():
            st.warning("⚠️ Ingresa texto para convertir.")
        else:
            with st.spinner("🧠 Generando audio con gTTS…"):
                # Si el usuario dio un nombre, úsalo; si no, sanitiza desde el texto.
                base_name = sanitize_filename(filename_hint) if filename_hint else sanitize_filename(text)
                # gTTS no acepta nombre del archivo directamente, así que guardamos y luego renombramos si hace falta.
                tmp_path = text_to_speech(text=text.strip(), lang=lang_code, tld=tld, slow=slow_voice, outdir="temp")
                out_path = os.path.join("temp", f"{base_name}.mp3")
                # Renombrar si el nombre base es distinto
                if os.path.abspath(tmp_path) != os.path.abspath(out_path):
                    try:
                        if os.path.exists(out_path):
                            os.remove(out_path)
                        os.replace(tmp_path, out_path)
                    except Exception:
                        out_path = tmp_path  # fallback

            st.success("✅ Audio generado correctamente.")
            st.markdown("### 🔊 Tu audio:")
            with open(out_path, "rb") as f:
                audio_bytes = f.read()
            st.audio(audio_bytes, format="audio/mp3", start_time=0)

            # Descargar con el componente nativo
            st.download_button(
                "📥 Descargar MP3",
                data=audio_bytes,
                file_name=os.path.basename(out_path),
                mime="audio/mpeg"
            )

            # (Opcional) Descargar también con enlace base64 (por compatibilidad)
            def download_link_from_bytes(data: bytes, filename: str, label: str = "Descargar (alternativo)"):
                b64 = base64.b64encode(data).decode()
                href = f'<a href="data:application/octet-stream;base64,{b64}" download="{filename}">{label}</a>'
                return href

            st.markdown(download_link_from_bytes(audio_bytes, os.path.basename(out_path)), unsafe_allow_html=True)

    except Exception as e:
        st.error(f"❌ Error al convertir: {e}")

# =========================
# Footer
# =========================
st.markdown("---")
st.markdown("""
**TTS Tech Mode 🤖**  
Convierte texto a audio **MP3** con **gTTS** en una interfaz **oscura** con acentos **neón**.  
> “Turning words into voice.” ⚡
""")
