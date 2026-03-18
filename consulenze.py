import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import os
from PIL import Image

# --- 1. CONFIGURAZIONE LOGO E PAGINA ---
logo_path = "logo.png"

def get_favicon():
    if os.path.exists(logo_path):
        try:
            img = Image.open(logo_path).convert("RGBA")
            return img.resize((32, 32))
        except:
            return "🔥"
    return "🔥"

st.set_page_config(
    page_title="Gestione Pratiche Incendi",
    page_icon=get_favicon(),
    layout="wide"
)

# --- 2. NASCONDI MENU STREAMLIT ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .block-container {padding-top: 1rem;}
    </style>
    """, unsafe_allow_html=True)

# --- 3. INTESTAZIONE ---
if os.path.exists(logo_path):
    st.image(logo_path, width=150)

st.title("🔥 Registro Professionale Prevenzione Incendi")
st.divider()

# --- 4. CONNESSIONE DATI ---
conn = st.connection("gsheets", type=GSheetsConnection)
df = conn.read(ttl=0)

if df is None or df.empty:
    df = pd.DataFrame(columns=["Data", "Cliente", "Tipologia", "Attività", "Ore", "Tariffa", "Totale", "Stato"])

# --- 5. MODULO DI INSERIMENTO (Sempre visibile in alto) ---
with st.expander("➕ AGGIUNGI NUOVA PRATICA / PRESTAZIONE", expanded=True):
    with st.form("form_inserimento", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            data = st.date_input("Data")
            cliente = st.text_input("Cliente / Condominio")
        with c2:
            tipologia = st.text_input("Tipologia (es. SCIA)")
            attivita = st.text_input("Dettaglio Attività")
        with c3:
            ore = st.number_input("Ore lavorate", min_value=0.5, step=0.5, value=1.0)
            tariffa = st.number_input("Tariffa €/ora", value=60.0)
        
        stato = st.selectbox("Stato Pagamento", ["❌ Non Pagata", "💰 Pagata"])
        
        if st.form_submit_button("💾 SALVA NEL CLOUD", use_container_width=True):
            if cliente:
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
                df = pd.concat([df, nuova_riga], ignore_index=True)
                conn.update(data=df)
                st.success(f"✅ Pratica per {cliente} salvata!")
                st.rerun()
            else:
                st.error("Inserisci il nome del cliente!")

st.divider()

# --- 6. VISUALIZZAZIONE E RICERCA ---
if not df.empty:
    # Calcoli rapidi
    df["Ore"] = pd.to_numeric(df["Ore"], errors='coerce').fillna(0)
    df["Totale"] = pd.to_numeric(df["Totale"], errors='coerce').fillna(0)

    # Metriche di riepilogo
    m1, m2, m3 = st.columns(3)
    m1.metric("Ore Totali", f"{df['Ore'].sum()} h")
    m2.metric("Da Incassare", f"{df[df['Stato'] == '❌ Non Pagata']['Totale'].sum():,.2f} €")
    m3.metric("Incassato", f"{df[df['Stato'] == '💰 Pagata']['Totale'].sum():,.2f} €")

    # Ricerca
    cerca = st.text_input("🔍 Cerca nel database...", placeholder="Filtra per cliente o attività")
    if cerca:
        df_mostra = df[df.apply(lambda r: cerca.lower() in r.astype(str).str.lower().values, axis=1)]
    else:
        df_mostra = df

    st.subheader("📋 Elenco Prestazioni")
    st.dataframe(df_mostra, use_container_width=True, hide_index=True)

    # --- 7. MODIFICA E CANCELLAZIONE ---
    st.divider()
    col_a, col_b = st.columns(2)
    
