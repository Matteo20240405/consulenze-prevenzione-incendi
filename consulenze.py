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
    
    # Lista completa delle colonne inclusa "Tipologia"
    colonne_richieste = ["Data", "Cliente", "Tipologia", "Attività", "Ore", "Tariffa Oraria", "Totale", "Stato"]
    
    # Inizializzazione se il foglio è vuoto
    if df is None or df.empty:
        df = pd.DataFrame(columns=colonne_richieste)
    else:
        # Controllo se mancano colonne (es. Tipologia) e le aggiungo se necessario
        for col in colonne_richieste:
            if col not in df.columns:
                df[col] = "" # Aggiunge la colonna vuota se manca

    st.title("🔥 Registro Professionale Prevenzione Incendi")

    # --- 3. INSERIMENTO NUOVA PRATICA ---
    with st.expander("➕ AGGIUNGI NUOVA PRESTAZIONE", expanded=True):
        with st.form("form_nuovo", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                data = st.date_input("Data")
                cliente = st.text_input("Cliente/Condominio")
                tipologia = st.text_input("Tipologia (es. SCIA, Rinnovo, Progetto)") # VOCE REINSERITA
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
                        "Tipologia": tipologia,
                        "Attività": attivita,
                        "Ore": float(ore),
                        "Tariffa Oraria": float(tariffa_h),
                        "Totale": float(ore * tariffa_h),
                        "Stato": stato
                    }])
                    df = pd.concat([df, nuova_riga], ignore_index=True)
                    conn.update(data=df)
                    st.success(f"Pratica per {cliente} salvata con successo!")
                    st.rerun()
                else:
                    st.error("Il campo 'Cliente' è obbligatorio.")

    # --- 4. CALCOLI E METRICHE ---
    if not df.empty:
        st.divider()
        # Conversione dati per i calcoli
        df["Ore"] = pd.to_numeric(df["Ore"], errors='coerce').fillna(0)
        df["Totale"] = pd.to_numeric(df["Totale"], errors='coerce').fillna(0)

        m1, m2, m3 = st.columns(3)
        m1.metric("Ore Totali", f"{df['Ore'].sum()} h")
        m2.metric("Da Incassare", f"{df[df['Stato'] == '❌ Non Pagata']['Totale'].sum():,.2f} €")
        m3.metric("Profitti (Incassato)", f"{df[df['Stato'] == '💰 Pagata']['Totale'].sum():,.2f} €")

        st.subheader("📋 Storico Prestazioni")
        
        # Filtro di ricerca che include anche la Tipologia
        cerca = st.text_input("🔍 Filtra per Cliente, Tipologia o Attività...")
        if cerca:
            df_view = df[df.apply(lambda r: cerca.lower() in r.astype(str).str.lower().values, axis=1)]
        else:
            df_view = df
            
        st.dataframe(df_view, use_container_width=True, hide_index=True)

        # --- 5. AZIONI (PAGATO / ELIMINA) ---
        st.divider()
        col_p, col_e = st.columns(2)

        with col_p:
            st.subheader("✅ Pagamenti")
            non_pagate = df[df["Stato"] == "❌ Non Pagata"]
            if not non_pagate.empty:
                idx_p = st.selectbox("Segna come pagata:", non_pagate.index, 
                                    format_func=lambda x: f"{df.at[x, 'Cliente']} - {df.at[x, 'Tipologia']} ({df.at[x, 'Totale']}€)")
                if st.button("Conferma Pagamento"):
                    df.at[idx_p, "Stato"] = "💰 Pagata"
                    conn.update(data=df)
                    st.rerun()
            else:
                st.info("Nessuna pendenza trovata.")

        with col_e:
            st.subheader("🗑️ Eliminazione")
            if not df.empty:
                idx_e = st.selectbox("Elimina riga:", df.index, 
                                    format_func=lambda x: f"{df.at[x, 'Cliente']} - {df.at[x, 'Data']}")
                if st.button("Elimina Definitivamente", type="primary"):
                    df = df.drop(idx_e)
                    conn.update(data=df)
                    st.rerun()

except Exception as e:
    st.error(f"Errore: {e}")
