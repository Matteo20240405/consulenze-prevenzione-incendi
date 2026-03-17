import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# --- CONFIGURAZIONE PAGINA (Qui cambi Nome e Icona) ---
st.set_page_config(
    page_title="Gestione Pratiche Incendi", # Il nome che appare sulla scheda del browser
    page_icon="👨‍🚒",                         # L'icona (puoi mettere: 🔥, 🚒, 📋, o 🏢)
    layout="wide"
)

st.title("🔥 Registro Professionale Prevenzione Incendi")

# --- IL RESTO DEL CODICE RIMANE UGUALE ---
conn = st.connection("gsheets", type=GSheetsConnection)
df = conn.read(ttl=0)

if df is None or df.empty:
    df = pd.DataFrame(columns=["Data", "Cliente", "Tipologia", "Attività", "Ore", "Tariffa", "Totale", "Stato"])

# --- BARRA LATERALE ---
with st.sidebar.form("Aggiungi"):
    st.header("✍️ Nuova Prestazione")
    data = st.date_input("Data")
    cliente = st.text_input("Cliente/Condominio")
    tipologia = st.text_input("Tipologia")
    attivita = st.text_input("Attività")
    ore = st.number_input("Ore lavorate", min_value=0.5, step=0.5)
    tariffa = st.number_input("Tariffa €/ora", value=50.0)
    stato = st.selectbox("Stato Pagamento", ["❌ Non Pagata", "💰 Pagata"])
    submit = st.form_submit_button("Salva nel Cloud")

if submit and cliente:
    nuova_riga = pd.DataFrame([{
        "Data": str(data),
        "Cliente": cliente,
        "Tipologia": tipologia,
        "Attività": attivita,
        "Ore": float(ore),
        "Tariffa": float(tariffa),
        "Totale": float(ore * tariffa),
        "Stato": stato
    }])
    df_aggiornato = pd.concat([df, nuova_riga], ignore_index=True)
    conn.update(data=df_aggiornato)
    st.success("Dato salvato!")
    st.rerun()

# --- TABELLA E GESTIONE ---
if not df.empty:
    # Calcoli
    df["Ore"] = pd.to_numeric(df["Ore"], errors='coerce').fillna(0)
    df["Totale"] = pd.to_numeric(df["Totale"], errors='coerce').fillna(0)
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Ore Totali", f"{df['Ore'].sum()} h")
    c2.metric("Da Incassare", f"{df[df['Stato'] == '❌ Non Pagata']['Totale'].sum():,.2f} €")
    c3.metric("Incassato", f"{df[df['Stato'] == '💰 Pagata']['Totale'].sum():,.2f} €")
    
    st.divider()
    st.subheader("📋 Elenco Prestazioni")
    st.dataframe(df, use_container_width=True)
    
    # Sezione eliminazione e aggiornamento (come prima)...
    # [Il codice per aggiornare/eliminare segue qui sotto]
