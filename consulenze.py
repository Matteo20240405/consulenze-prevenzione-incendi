import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# --- 1. CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Gestione Pratiche Incendi", layout="wide")

# --- 2. CONNESSIONE ---
conn = st.connection("gsheets", type=GSheetsConnection)

try:
    df = conn.read(ttl=0)
    
    if df is None or df.empty:
        df = pd.DataFrame(columns=["Data", "Cliente", "Attività", "Ore", "Tariffa Oraria", "Totale", "Stato"])

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

    # --- 4. CALCOLI E METRICHE ---
    if not df.empty:
        st.divider()
        # Conversione sicura dei dati numerici
        df["Ore"] = pd.to_numeric(df["Ore"], errors='coerce').fillna(0)
        df["Tariffa Oraria"] = pd.to_numeric(df["Tariffa Oraria"], errors='coerce').fillna(0)
        df["Totale"] = pd.to_numeric(df["Totale"], errors='coerce').fillna(0)

        m1, m2, m3 = st.columns(3)
        m1.metric("Ore Totali Lavorate", f"{df['Ore'].sum()} h")
        m2.metric("Crediti (Da Incassare)", f"{df[df['Stato'] == '❌ Non Pagata']['Totale'].sum():,.2f} €")
        m3.metric("Profitti (Incassato)", f"{df[df['Stato'] == '💰 Pagata']['Totale'].sum():,.2f} €")

        st.subheader("📋 Storico Prestazioni")
        
        cerca = st.text_input("🔍 Cerca cliente o attività...")
        df_view = df[df.apply(lambda r: cerca.lower() in r.astype(str).str.lower().values, axis=1)] if cerca else df
            
        st.dataframe(df_view, use_container_width=True, hide_index=True)

        # --- 5. GESTIONE STATO E CANCELLAZIONE ---
        st.divider()
        col_pag, col_del = st.columns(2)

        with col_pag:
            st.subheader("✅ Gestione Pagamenti")
            da_pagare = df[df["Stato"] == "❌ Non Pagata"]
            if not da_pagare.empty:
                idx_p = st.selectbox("Seleziona per segnare come pagato:", da_pagare.index, 
                                    format_func=lambda x: f"{df.at[x, 'Cliente']} - {df.at[x, 'Totale']}€")
                if st.button("Conferma Incasso"):
                    df.at[idx_p, "Stato"] = "💰 Pagata"
                    conn.update(data=df)
                    st.rerun()
            else:
                st.info("Ottimo lavoro! Non ci sono pagamenti in sospeso.")

        with col_del:
            st.subheader("🗑️ Elimina Pratica")
            idx_e = st.selectbox("Seleziona riga da rimuovere:", df.index, 
                                format_func=lambda x: f"{df.at[x, 'Cliente']} ({df.at[x, 'Data']})")
            if st.button("Elimina Voce", type="primary"):
                df = df.drop(idx_e)
                conn.update(data=df)
                st.rerun()

except Exception as e:
    st.error(f"Errore di connessione: {e}")
