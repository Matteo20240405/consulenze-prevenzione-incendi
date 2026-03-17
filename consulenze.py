import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="Gestione Consulenze Incendi", layout="wide")
st.title("🔥 Registro Professionale Prevenzione Incendi")

# --- CONNESSIONE ---
conn = st.connection("gsheets", type=GSheetsConnection)

# Leggiamo i dati (ttl=0 forza l'aggiornamento immediato ad ogni click)
df = conn.read(ttl=0)

# Se il foglio è nuovo o vuoto, inizializziamo le colonne
if df is None or df.empty:
    df = pd.DataFrame(columns=["Data", "Cliente", "Tipologia", "Attività", "Ore", "Tariffa", "Totale", "Stato"])

# --- 1. AGGIUNGI NUOVA PRATICA (Barra Laterale) ---
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
    df_aggiornato = pd.concat([df, nuova_riga], ignore_index=True)
    conn.update(data=df_aggiornato)
    st.success("Dato salvato!")
    st.rerun()

# --- 2. RESOCONTO E STATISTICHE ---
if not df.empty:
    # Convertiamo i dati in numeri per sicurezza
    df["Ore"] = pd.to_numeric(df["Ore"], errors='coerce').fillna(0)
    df["Totale"] = pd.to_numeric(df["Totale"], errors='coerce').fillna(0)

    st.subheader("📊 Riepilogo Ore e Incassi")
    c1, c2, c3 = st.columns(3)
    
    ore_totali = df["Ore"].sum()
    da_incassare = df[df["Stato"] == "❌ Non Pagata"]["Totale"].sum()
    incassato = df[df["Stato"] == "💰 Pagata"]["Totale"].sum()
    
    c1.metric("Ore Totali", f"{ore_totali} h")
    c2.metric("Da Incassare", f"{da_incassare:,.2f} €", delta_color="inverse")
    c3.metric("Incassato", f"{incassato:,.2f} €")

    st.divider()

    # --- 3. TABELLA PRATICHE ---
    st.subheader("📋 Elenco Prestazioni")
    st.dataframe(df, use_container_width=True)

    st.divider()

    # --- 4. GESTIONE PRATICHE (Aggiorna/Elimina) ---
    col_update, col_delete = st.columns(2)

    with col_update:
        st.subheader("🔄 Segna come Pagato")
        non_pagate = df[df["Stato"] == "❌ Non Pagata"]
        if not non_pagate.empty:
            scelta = st.selectbox("Seleziona pratica saldata:", 
                                  options=non_pagate.index, 
                                  format_func=lambda x: f"{df.at[x, 'Cliente']} - {df.at[x, 'Totale']}€")
            if st.button("Conferma Pagamento"):
                df.at[scelta, "Stato"] = "💰 Pagata"
                conn.update(data=df)
                st.success("Pagamento registrato!")
                st.rerun()
        else:
            st.write("Tutte le pratiche sono pagate! ✅")

    with col_delete:
        st.subheader("🗑️ Elimina Pratica")
        scelta_del = st.selectbox("Seleziona pratica da rimuovere:", 
                                  options=df.index, 
                                  format_func=lambda x: f"{df.at[x, 'Cliente']} ({df.at[x, 'Data']})")
        if st.button("Elimina Definitivamente", type="primary"):
            df = df.drop(scelta_del)
            conn.update(data=df)
            st.warning("Pratica eliminata.")
            st.rerun()
else:
    st.info("Nessuna pratica registrata nel database.")
