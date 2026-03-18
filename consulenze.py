import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="Gestione Pratiche Incendi", layout="wide")

# Connessione automatica tramite Secrets
conn = st.connection("gsheets", type=GSheetsConnection)

try:
    df = conn.read(ttl=0)
    st.title("🔥 Registro Professionale Prevenzione Incendi")
    
    with st.expander("➕ AGGIUNGI NUOVA PRESTAZIONE", expanded=True):
        with st.form("form_nuovo", clear_on_submit=True):
            data = st.date_input("Data")
            cliente = st.text_input("Cliente")
            attivita = st.text_input("Attività")
            ore = st.number_input("Ore", min_value=0.5, step=0.5)
            
            if st.form_submit_button("💾 SALVA"):
                nuova_riga = pd.DataFrame([{"Data": str(data), "Cliente": cliente, "Attività": attivita, "Ore": ore}])
                df = pd.concat([df, nuova_riga], ignore_index=True)
                conn.update(data=df)
                st.success("Salvato!")
                st.rerun()

    if not df.empty:
        st.dataframe(df, use_container_width=True, hide_index=True)

except Exception as e:
    st.error(f"Errore critico di connessione. Verifica i Secrets: {e}")
