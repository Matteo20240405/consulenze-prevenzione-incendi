import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# CONFIGURAZIONE PAGINA
st.set_page_config(page_title="Gestione Pratiche Incendi", layout="wide")

# CONNESSIONE (Usa automaticamente i Secrets impostati su Streamlit Cloud)
conn = st.connection("gsheets", type=GSheetsConnection)

# Lettura dati (L'URL è già nei Secrets, quindi qui lasciamo vuoto o mettiamo l'URL)
try:
    df = conn.read(ttl=0)
except Exception as e:
    st.error(f"Configurazione in corso... se vedi questo errore controlla i Secrets: {e}")
    df = pd.DataFrame(columns=["Data", "Cliente", "Tipologia", "Attività", "Ore", "Tariffa", "Totale", "Stato"])

st.title("🔥 Registro Professionale Prevenzione Incendi")

# FORM DI INSERIMENTO
with st.expander("➕ AGGIUNGI NUOVA PRESTAZIONE", expanded=True):
    with st.form("form_nuovo", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            data = st.date_input("Data")
            cliente = st.text_input("Cliente/Condominio")
        with c2:
            attivita = st.text_input("Attività")
            ore = st.number_input("Ore lavorate", min_value=0.5, step=0.5)
        
        stato = st.selectbox("Stato Pagamento", ["❌ Non Pagata", "💰 Pagata"])
        
        if st.form_submit_button("💾 SALVA NEL CLOUD"):
            if cliente:
                nuova_riga = pd.DataFrame([{
                    "Data": str(data), "Cliente": cliente, "Attività": attivita,
                    "Ore": float(ore), "Stato": stato
                }])
                df = pd.concat([df, nuova_riga], ignore_index=True)
                conn.update(data=df)
                st.success("Dato salvato!")
                st.rerun()

# TABELLA
if not df.empty:
    st.divider()
    st.dataframe(df, use_container_width=True, hide_index=True)
