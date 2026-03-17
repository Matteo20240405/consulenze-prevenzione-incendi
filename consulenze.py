import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- CONFIGURAZIONE ---
BASE_DIR = os.path.expanduser("~/Scrivania")
DB_CONSULENZE = os.path.join(BASE_DIR, "database_consulenze.csv")

st.set_page_config(page_title="Gestione Consulenze Incendi", layout="wide")
st.title("🔥 Registro Consulenze Prevenzione Incendi")

COLONNE = ["Data", "Cliente", "Tipologia", "Attività", "Ore", "Tariffa_Oraria", "Totale", "Stato"]

if not os.path.exists(DB_CONSULENZE):
    df = pd.DataFrame(columns=COLONNE)
    df.to_csv(DB_CONSULENZE, index=False)
else:
    df = pd.read_csv(DB_CONSULENZE)
    # Controllo per aggiungere la colonna se non esiste nel vecchio CSV
    if "Tipologia" not in df.columns:
        df["Tipologia"] = "Generale"
        df.to_csv(DB_CONSULENZE, index=False)

# --- 1. AGGIUNGI CONSULENZA (Barra Laterale) ---
with st.sidebar.form("Aggiungi"):
    st.header("Nuova Prestazione")
    data = st.date_input("Data", datetime.now())
    cliente = st.text_input("Nome Cliente (es. Condominio Roma)")
    tipologia = st.text_input("Tipologia Cliente (es. Condominio, Società, Ditta)") # CAMPO LIBERO
    attivita = st.text_input("Attività (es. Rinnovo CPI)")
    ore = st.number_input("Ore lavorate", min_value=0.5, step=0.5)
    tariffa = st.number_input("Tariffa Oraria (€/ora)", min_value=0.0, value=50.0, step=5.0)
    stato = st.selectbox("Stato Pagamento", ["❌ Non Pagata", "💰 Pagata"])
    submit = st.form_submit_button("Registra Consulenza")

if submit and cliente:
    totale_riga = ore * tariffa
    nuova_riga = pd.DataFrame([[str(data), cliente, tipologia, attivita, ore, tariffa, totale_riga, stato]], columns=COLONNE)
    df = pd.concat([df, nuova_riga], ignore_index=True)
    df.to_csv(DB_CONSULENZE, index=False)
    st.success(f"Registrata consulenza per {cliente}")
    st.rerun()

# --- 2. TABELLA E STATISTICHE ---
st.subheader("Elenco Prestazioni")
if not df.empty:
    # Mostriamo la tabella completa
    st.dataframe(df, use_container_width=True)
    
    col_a, col_b, col_c = st.columns(3)
    ore_totali = df["Ore"].sum()
    da_incassare = df[df["Stato"] == "❌ Non Pagata"]["Totale"].sum()
    incassato = df[df["Stato"] == "💰 Pagata"]["Totale"].sum()
    
    col_a.metric("Ore Totali Lavorate", f"{ore_totali} h")
    col_b.metric("Da Incassare", f"{da_incassare:.2f} €")
    col_c.metric("Totale Incassato", f"{incassato:.2f} €")

    # --- 3. MODIFICHE RAPIDE ---
    st.divider()
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("🔄 Aggiorna Pagamento")
        non_pagate = df[df["Stato"] == "❌ Non Pagata"]
        if not non_pagate.empty:
            scelta = st.selectbox("Seleziona:", [f"{i}: {r['Cliente']} ({r['Totale']}€)" for i, r in non_pagate.iterrows()])
            if st.button("Segna come PAGATA"):
                idx = int(scelta.split(":")[0])
                df.at[idx, "Stato"] = "💰 Pagata"
                df.to_csv(DB_CONSULENZE, index=False)
                st.rerun()
    with c2:
        st.subheader("🗑️ Elimina")
        scelta_e = st.selectbox("Elimina riga:", [f"{i}: {r['Cliente']}" for i, r in df.iterrows()])
        if st.button("Conferma", type="primary"):
            idx_e = int(scelta_e.split(":")[0])
            df = df.drop(idx_e)
            df.to_csv(DB_CONSULENZE, index=False)
            st.rerun()
else:
    st.info("Nessuna consulenza registrata.")
