import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# --- 1. CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Gestione Pratiche Incendi", layout="wide")

# --- 2. CONNESSIONE ---
conn = st.connection("gsheets", type=GSheetsConnection)

try:
    # Lettura dati
    df = conn.read(ttl=0)
    
    # Lista delle colonne necessarie
    colonne_richieste = ["Data", "Cliente", "Attività", "Ore", "Tariffa Oraria", "Totale", "Stato"]
    
    # Se il foglio è vuoto o mancano colonne, lo inizializziamo correttamente
    if df is None or df.empty:
        df = pd.DataFrame(columns=colonne_richieste)
    else:
        # Verifica se tutte le colonne esistono, altrimenti le aggiunge vuote
        for col in colonne_richieste:
            if col not in df.columns:
                df[col] = 0 if col in ["Ore", "Tariffa Oraria", "Totale"] else ""

    st.title("🔥 Registro Professionale Prevenzione Incendi")

    # --- 3. INSERIMENTO NUOVA PRATICA ---
    with st.expander("➕ AGGIUNGI NUOVA PRESTAZIONE", expanded=True):
        with st.form("form_nuovo", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                data = st.date_input("Data")
                cliente = st.text_input("Cliente/Condominio")
                attivita = st.text_input("Dettaglio Attività")
            with c2:
                ore = st.number_input("Ore Lavorate", min_value=0.0, step=0.5, value=1.0)
                tariffa_h = st.number_input("Tariffa Oraria (€/h)", min_value=0.0, step=5.0, value=60.0)
                stato = st.selectbox("Stato Pagamento", ["❌ Non Pagata", "💰 Pagata"])
            
            if st.form_submit_button("💾 SALVA NEL DATABASE"):
                if cliente:
                    nuova_riga = pd.DataFrame([{
                        "Data": str(data),
                        "Cliente": cliente,
                        "Attività": attivita,
                        "Ore": float(ore),
                        "Tariffa Oraria": float(tariffa_h),
                        "Totale": float(ore * tariffa_h),
                        "Stato": stato
                    }])
                    df = pd.concat([df, nuova_riga], ignore_index=True)
                    conn.update(data=df)
                    st.success(f"Pratica per {cliente} salvata!")
                    st.rerun()
                else:
                    st.error("Inserisci il nome del cliente.")

    # --- 4. CALCOLI E METRICHE (TOTALI E PROFITTI) ---
    if not df.empty:
        st.divider()
        # Conversione sicura per evitare errori di calcolo
        df["Ore"] = pd.to_numeric(df["Ore"], errors='coerce').fillna(0)
        df["Tariffa Oraria"] = pd.to_numeric(df["Tariffa Oraria"], errors='coerce').fillna(0)
        df["Totale"] = pd.to_numeric(df["Totale"], errors='coerce').fillna(0)

        m1, m2, m3 = st.columns(3)
        m1.metric("Ore Totali", f"{df['Ore'].sum()} h")
        m2.metric("Da Incassare", f"{df[df['Stato'] == '❌ Non Pagata']['Totale'].sum():,.2f} €")
        m3.metric("Incassato (Profitto)", f"{df[df['Stato'] == '💰 Pagata']['Totale'].sum():,.2f} €")

        st.subheader("📋 Storico Prestazioni")
        st.dataframe(df, use_container_width=True, hide_index=True)

        # --- 5. GESTIONE PAGAMENTI ED ELIMINAZIONE ---
        st.divider()
        col_pag, col_del = st.columns(2)

        with col_pag:
            st.subheader("✅ Segna come Pagato")
            da_pagare = df[df["Stato"] == "❌ Non Pagata"]
            if not da_pagare.empty:
                idx_p = st.selectbox("Seleziona pratica saldata:", da_pagare.index, 
                                    format_func=lambda x: f"{df.at[x, 'Cliente']} - {df.at[x, 'Totale']}€")
                if st.button("Conferma Incasso"):
                    df.at[idx_p, "Stato"] = "💰 Pagata"
                    conn.update(data=df)
                    st.rerun()
            else:
                st.info("Nessun pagamento in sospeso.")

        with col_del:
            st.subheader("🗑️ Elimina Pratica")
            idx_e = st.selectbox("Seleziona riga da cancellare:", df.index, 
                                format_func=lambda x: f"{df.at[x, 'Cliente']} ({df.at[x, 'Data']})")
            if st.button("Elimina Definitivamente", type="primary"):
                df = df.drop(idx_e)
                conn.update(data=df)
                st.warning("Riga eliminata.")
                st.rerun()

except Exception as e:
    st.error(f"Errore di connessione o colonne: {e}")
    st.info("Se l'errore persiste, prova a rinominare manualmente le colonne del tuo Foglio Google come: Data, Cliente, Attività, Ore, Tariffa Oraria, Totale, Stato")
