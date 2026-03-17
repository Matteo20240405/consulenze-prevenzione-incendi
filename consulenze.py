import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from PIL import Image
import os

# --- CARICAMENTO LOGO ---
# Verifichiamo se il file esiste per evitare errori
logo_path = "logo.png" 

if os.path.exists(logo_path):
    img = Image.open(logo_path)
    page_icon = img
else:
    page_icon = "🔥" # Icona di riserva se il file non viene trovato

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(
    page_title="Gestione Pratiche Incendi",
    page_icon=page_icon,
    layout="wide"
)

# --- MOSTRA IL LOGO IN ALTO ---
if os.path.exists(logo_path):
    # Puoi regolare la larghezza (width) come preferisci
    st.image(logo_path, width=150)

st.title("Registro Professionale Prevenzione Incendi")

# --- NASCONDI ELEMENTI STREAMLIT (Per un look pulito) ---
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            /* Rimuove lo spazio bianco in alto */
            .block-container {padding-top: 2rem;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# ... (Qui prosegue il resto del codice per Google Sheets che abbiamo già scritto)
