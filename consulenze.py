import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="Gestione Consulenze Incendi", layout="wide")
st.title("🔥 Registro Consulenze (Cloud Edition)")

# Collegamento a Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# Lettura dati esistenti
try:
    df = conn.read()
except:
    # Se il foglio è vuoto, crea la struttura
    df = pd.DataFrame(columns=["Data", "Cliente", "Tipologia", "Attività", "Ore", "Tariffa", "Totale", "Stato"])

# --- FORM DI INSERIMENTO ---
with st.sidebar.form("Aggiungi"):
    data = st.date_input("Data")
    cliente = st.text_input("Cliente")
    tipologia = st.text_input("Tipologia (libera)")
    attivita = st.text_input("Attività")
    ore = st.number_input("Ore", min_value=0.5, step=0.5)
    tariffa = st.number_input("Tariffa €/h", value=50.0)
    stato = st.selectbox("Stato", ["❌ Non Pagata", "💰 Pagata"])
    submit = st.form_submit_button("Salva su Google Sheets")

if submit and cliente:
    nuova_riga = pd.DataFrame([{
        "Data": str(data),
        "Cliente": cliente,
        "Tipologia": tipologia,
        "Attività": attivita,
        "Ore": ore,
        "Tariffa": tariffa,
        "Totale": ore * tariffa,
        "Stato": stato
    }])
    
    # Unisce i nuovi dati ai vecchi
    df_aggiornato = pd.concat([df, nuova_riga], ignore_index=True)
    
    # Salva direttamente nel cloud di Google
    conn.update(data=df_aggiornato)
    st.success("Dato salvato nel Foglio Google!")
    st.rerun()

# Visualizzazione
st.dataframe(df, use_container_width=True)
