import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import os
from PIL import Image

# --- CONFIGURAZIONE PAGINA ---
# Nome del file logo che devi caricare su GitHub: logo.png
logo_path = "logo.png"

# Controllo se il logo esiste per impostarlo come icona della scheda (Favicon)
if os.path.exists(logo_path):
    page_icon = Image.open(logo_path)
else:
    page_icon = "🔥"

st.set_page_config(
    page_title="Gestione Pratiche Incendi",
    page_icon=page_icon,
    layout="wide"
)

# --- STILE CSS PER NASCONDERE MENU STREAMLIT ---
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            .block-container {padding-top: 1rem;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# --- LOGO E TITOLO ---
if os.path.exists(logo_path):
    st.image(logo_path, width=150)

st.title("🔥 Registro Professionale Prevenzione Incendi")

# --- CONNESSIONE GOOGLE SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)
df = conn.read(ttl=0)

# Inizializzazione se il foglio è vuoto
if df is None or df.empty:
    df = pd.DataFrame(columns=["Data", "Cliente", "Tipologia", "Attività", "Ore", "Tariffa", "Totale", "Stato"])

# --- BARRA LATERALE: INSERIMENTO ---
with st.sidebar.form("Aggiungi"):
    st.header("✍️ Nuova Prestazione")
    data = st.date_input("Data")
    cliente = st.text_input("Cliente/Condominio")
    tipologia = st.text_input("Tipologia (es. Condominio, Ditta)")
    attivita = st.text_input("Attività (es. Rinnovo CPI)")
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
    df = pd.concat([df, nuova_riga], ignore_index=True)
    conn.update(data=df)
    st.success(f"Dato salvato per {cliente}!")
    st.rerun()

# --- CORPO PRINCIPALE: FILTRI E TABELLA ---
if not df.empty:
    # Pulizia dati per calcoli
    df["Ore"] = pd.to_numeric(df["Ore"], errors='coerce').fillna(0)
    df["Totale"] = pd.to_numeric(df["Totale"], errors='coerce').fillna(0)

    # 📊 METRICHE IN ALTO
    c1, c2, c3 = st.columns(3)
    c1.metric("Ore Totali", f"{df['Ore'].sum()} h")
    c2.metric("Da Incassare", f"{df[df['Stato'] == '❌ Non Pagata']['Totale'].sum():,.2f} €")
    c3.metric("Incassato", f"{df[df['Stato'] == '💰 Pagata']['Totale'].sum():,.2f} €")

    st.divider()

    # 🔍 RICERCA
    search = st.text_input("🔍 Cerca per Cliente o Attività", "")
    df_mostrato = df[df.apply(lambda row: search.lower() in row.astype(str).str.lower().values, axis=1)] if search else df

    st.subheader("📋 Elenco Prestazioni")
    st.dataframe(df_mostrato, use_container_width=True)

    st.divider()

    # ⚙️ GESTIONE (PAGAMENTI ED ELIMINAZIONE)
    col_pay, col_del = st.columns(2)

    with col_pay:
        st.subheader("🔄 Aggiorna Pagamento")
        non_pagate = df[df["Stato"] == "❌ Non Pagata"]
        if not non_pagate.empty:
            scelta = st.selectbox("Seleziona pratica saldata:", 
                                  options=non_pagate.index, 
                                  format_func=lambda x: f"{df.at[x, 'Cliente']} ({df.at[x, 'Totale']}€)")
            if st.button("Segna come PAGATA"):
                df.at[scelta, "Stato"] = "💰 Pagata"
                conn.update(data=df)
                st.rerun()
        else:
            st.write("Ottimo! Non ci sono sospesi. ✅")

    with col_del:
        st.subheader("🗑️ Elimina Pratica")
        scelta_del = st.selectbox("Seleziona pratica da rimuovere:", 
                                  options=df.index, 
                                  format_func=lambda x: f"{df.at[x, 'Cliente']} - {df.at[x, 'Data']}")
        if st.button("Elimina Definitivamente", type="primary"):
            df = df.drop(scelta_del)
            conn.update(data=df)
            st.warning("Pratica rimossa.")
            st.rerun()
else:
    st.info("Database vuoto. Inserisci la prima pratica dalla barra laterale!")
