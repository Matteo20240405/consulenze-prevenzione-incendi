import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import os
from PIL import Image

# --- 1. GESTIONE LOGO E ICONA SCHEDA ---
logo_path = "logo.png"

# Funzione per preparare l'icona della scheda (Favicon)
def get_favicon():
    if os.path.exists(logo_path):
        try:
            # Apriamo il logo originale da 800kb
            img = Image.open(logo_path).convert("RGBA")
            # Lo ridimensioniamo drasticamente per il browser (32x32 pixel)
            # Questo aiuta il browser ad accettarlo come icona della scheda
            return img.resize((32, 32))
        except Exception:
            return "🔥"
    return "🔥"

# --- 2. CONFIGURAZIONE PAGINA ---
st.set_page_config(
    page_title="Gestione Pratiche Incendi",
    page_icon=get_favicon(),
    layout="wide"
)

# --- 3. PULIZIA INTERFACCIA (Nasconde Streamlit) ---
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            .block-container {padding-top: 1.5rem;}
            /* Colore personalizzato per le metriche */
            [data-testid="stMetricValue"] { color: #d32f2f; }
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# --- 4. INTESTAZIONE ---
if os.path.exists(logo_path):
    # Mostriamo il logo grande dentro l'app
    st.image(logo_path, width=180)

st.title("Registro Professionale Prevenzione Incendi")
st.markdown("---")

# --- 5. CONNESSIONE GOOGLE SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)
df = conn.read(ttl=0)

# Inizializzazione se il foglio è vuoto
if df is None or df.empty:
    df = pd.DataFrame(columns=["Data", "Cliente", "Tipologia", "Attività", "Ore", "Tariffa", "Totale", "Stato"])

# --- 6. BARRA LATERALE (Inserimento) ---
with st.sidebar:
    st.header("✍️ Nuova Prestazione")
    with st.form("nuovo_inserimento", clear_on_submit=True):
        data = st.date_input("Data")
        cliente = st.text_input("Cliente/Condominio")
        tipologia = st.text_input("Tipologia")
        attivita = st.text_input("Attività")
        ore = st.number_input("Ore", min_value=0.5, step=0.5, value=1.0)
        tariffa = st.number_input("Tariffa €/ora", value=60.0)
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
    df = pd.concat([df, nuova_riga], ignore_index=True)
    conn.update(data=df)
    st.sidebar.success("✅ Salvato!")
    st.rerun()

# --- 7. VISUALIZZAZIONE E CALCOLI ---
if not df.empty:
    # Pulizia numeri
    df["Ore"] = pd.to_numeric(df["Ore"], errors='coerce').fillna(0)
    df["Totale"] = pd.to_numeric(df["Totale"], errors='coerce').fillna(0)

    # Metriche
    c1, c2, c3 = st.columns(3)
    c1.metric("Ore Totali", f"{df['Ore'].sum()} h")
    c2.metric("Da Incassare", f"{df[df['Stato'] == '❌ Non Pagata']['Totale'].sum():,.2f} €")
    c3.metric("Incassato", f"{df[df['Stato'] == '💰 Pagata']['Totale'].sum():,.2f} €")

    st.markdown("### 🔍 Ricerca Rapida")
    search = st.text_input("Filtra per nome, attività o stato...", placeholder="Es: Condominio Rossi")
    
    # Filtro dinamico
    if search:
        df_view = df[df.apply(lambda r: search.lower() in r.astype(str).str.lower().values, axis=1)]
    else:
        df_view = df

    st.dataframe(df_view, use_container_width=True, hide_index=True)

    # --- 8. AZIONI (Pagato/Elimina) ---
    st.markdown("### ⚙️ Gestione Righe")
    col_a, col_b = st.columns(2)

    with col_a:
        da_pagare = df[df["Stato"] == "❌ Non Pagata"]
        if not da_pagare.empty:
            scelta_p = st.selectbox("Segna come pagato:", da_pagare.index, 
                                   format_func=lambda x: f"{df.at[x, 'Cliente']} - {df.at[x, 'Totale']}€")
            if st.button("Conferma Saldo"):
                df.at[scelta_p, "Stato"] = "💰 Pagata"
                conn.update(data=df)
                st.rerun()

    with col_b:
        scelta_d = st.selectbox("Elimina riga:", df.index, 
                               format_func=lambda x: f"{df.at[x, 'Cliente']} ({df.at[x, 'Data']})")
        if st.button("Elimina Definitivamente", type="primary"):
            df = df.drop(scelta_d)
            conn.update(data=df)
            st.rerun()
else:
    st.info("Database pronto. Inserisci la prima pratica dal menu a sinistra.")
