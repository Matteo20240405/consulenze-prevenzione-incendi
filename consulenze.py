import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import os
from PIL import Image

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Gestione Pratiche Incendi", layout="wide")

# --- CONNESSIONE (Versione Semplificata) ---
# Non passiamo più le credenziali qui, le mettiamo nei Secrets
conn = st.connection("gsheets", type=GSheetsConnection)

# URL del tuo foglio
SHEET_URL = "https://docs.google.com/spreadsheets/d/12orchamSx43ERvYjZ6VpnFr3dqZRxr6GTMxpIEbKMwM/edit#gid=0"

try:
    df = conn.read(spreadsheet=SHEET_URL, ttl=0)
except Exception as e:
    st.error(f"Attesa configurazione segreta: {e}")
    df = pd.DataFrame()

if df is None or df.empty:
    df = pd.DataFrame(columns=["Data", "Cliente", "Tipologia", "Attività", "Ore", "Tariffa", "Totale", "Stato"])

# --- INTERFACCIA ---
st.title("🔥 Registro Professionale Prevenzione Incendi")

with st.expander("➕ AGGIUNGI NUOVA PRESTAZIONE", expanded=True):
    with st.form("form_nuovo", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            data = st.date_input("Data")
            cliente = st.text_input("Cliente/Condominio")
        with c2:
            attivita = st.text_input("Attività")
            ore = st.number_input("Ore", min_value=0.5, step=0.5, value=1.0)
        
        stato = st.selectbox("Stato", ["❌ Non Pagata", "💰 Pagata"])
        
        if st.form_submit_button("💾 SALVA"):
            nuova_riga = pd.DataFrame([{
                "Data": str(data), "Cliente": cliente, "Attività": attivita,
                "Ore": float(ore), "Stato": stato
            }])
            df = pd.concat([df, nuova_riga], ignore_index=True)
            conn.update(spreadsheet=SHEET_URL, data=df)
            st.success("Salvato!")
            st.rerun()

if not df.empty:
    st.dataframe(df, use_container_width=True, hide_index=True)
