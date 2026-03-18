import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import os
from PIL import Image

# --- 1. CONFIGURAZIONE LOGO E PAGINA ---
logo_path = "logo.png"
nome_app = "Gestione Pratiche Incendi"

# Tentativo di caricamento logo per la Favicon (icona della scheda)
try:
    if os.path.exists(logo_path):
        img_per_favicon = Image.open(logo_path).convert("RGBA")
        # Ridimensioniamo a 32x32 per assicurarci che il browser la accetti
        favicon = img_per_favicon.resize((32, 32))
    else:
        favicon = "🔥"
except Exception:
    favicon = "🔥"

st.set_page_config(
    page_title=nome_app,
    page_icon=favicon,
    layout="wide"
)

# --- 2. STILE GRAFICO (Nasconde menu Streamlit) ---
hide_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .block-container {padding-top: 1rem;}
    /* Rende la tabella più leggibile */
    .stDataFrame {border: 1px solid #e6e9ef; border-radius: 10px;}
    </style>
"""
st.markdown(hide_style, unsafe_allow_html=True)

# --- 3. INTESTAZIONE CON LOGO ---
if os.path.exists(logo_path):
    st.image(logo_path, width=150)

st.title(f"🏢 {nome_app}")

# --- 4. CONNESSIONE AL DATABASE (Google Sheets) ---
conn = st.connection("gsheets", type=GSheetsConnection)

def carica_dati():
    return conn.read(ttl=0)

df = carica_dati()

# Inizializza colonne se il foglio è nuovo/vuoto
if df is None or df.empty:
    df = pd.DataFrame(columns=["Data", "Cliente", "Tipologia", "Attività", "Ore", "Tariffa", "Totale", "Stato"])

# --- 5. BARRA LATERALE: INSERIMENTO DATI ---
with st.sidebar:
    st.header("✍️ Nuova Prestazione")
    with st.form("form_aggiunta", clear_on_submit=True):
        data = st.date_input("Data")
        cliente = st.text_input("Cliente/Condominio")
        tipologia = st.text_input("Tipologia (es. Condominio)")
        attivita = st.text_input("Attività (es. Rinnovo CPI)")
        ore = st.number_input("Ore lavorate", min_value=0.1, step=0.1, value=1.0)
        tariffa = st.number_input("Tariffa €/ora", min_value=1.0, value=60.0)
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
    st.sidebar.success("✅ Salvato con successo!")
    st.rerun()

# --- 6. AREA PRINCIPALE: CALCOLI E TABELLA ---
if not df.empty:
    # Conversione numerica sicura
    df["Ore"] = pd.to_numeric(df["Ore"], errors='coerce').fillna(0)
    df["Totale"] = pd.to_numeric(df["Totale"], errors='coerce').fillna(0)

    # Widget Metriche
    c1, c2, c3 = st.columns(3)
    c1.metric("Ore Totali", f"{df['Ore'].sum():.1f} h")
    c2.metric("In Attesa (Lordo)", f"{df[df['Stato'] == '❌ Non Pagata']['Totale'].sum():,.2f} €", delta_color="inverse")
    c3.metric("Incassato", f"{df[df['Stato'] == '💰 Pagata']['Totale'].sum():,.2f} €")

    st.divider()

    # Barra di Ricerca
    search = st.text_input("🔍 Cerca cliente, attività o stato...", placeholder="Scrivi qui per filtrare...")
    
    if search:
        mask = df.apply(lambda row: row.astype(str).str.contains(search, case=False).any(), axis=1)
        df_visualizza = df[mask]
    else:
        df_visualizza = df

    st.subheader("📋 Elenco Pratiche")
    st.dataframe(df_visualizza, use_container_width=True, hide_index=True)

    st.divider()

    # --- 7. AZIONI RAPIDE: PAGAMENTI ED ELIMINAZIONE ---
    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("💰 Registra Saldo")
        da_pagare = df[df["Stato"] == "❌ Non Pagata"]
        if not da_pagare.empty:
            scelta_pag = st.selectbox("Pratica saldata:", 
                                     options=da_pagare.index, 
                                     format_func=lambda x: f"{df.at[x, 'Cliente']} - {df.at[x, 'Totale']}€")
            if st.button("Conferma Pagamento", use_container_width=True):
                df.at[scelta_pag, "Stato"] = "💰 Pagata"
                conn.update(data=df)
                st.rerun()
        else:
            st.info("Tutte le pratiche risultano pagate.")

    with col_b:
        st.subheader("🗑️ Rimuovi Errore")
        scelta_del = st.selectbox("Pratica da eliminare:", 
                                 options=df.index, 
                                 format_func=lambda x: f"{df.at[x, 'Cliente']} ({df.at[x, 'Data']})")
        if st.button("Elimina Definitivamente", type="primary", use_container_width=True):
            df = df.drop(scelta_del)
            conn.update(data=df)
            st.warning("Pratica eliminata.")
            st.rerun()
else:
    st.info("👋 Benvenuto! Inizia inserendo una pratica nel menu a sinistra.")
