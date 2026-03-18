import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# --- 1. CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Gestione Pratiche Incendi", layout="wide")

# --- 2. CONNESSIONE ---
# Utilizza i Secrets che abbiamo configurato precedentemente
conn = st.connection("gsheets", type=GSheetsConnection)

try:
    # Lettura dati in tempo reale
    df = conn.read(ttl=0)
    
    # Se il foglio è nuovo/vuoto, inizializziamo le colonne corrette
    if df is None or df.empty:
        df = pd.DataFrame(columns=["Data", "Cliente", "Attività", "Ore", "Tariffa", "Totale", "Stato"])

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
                tariffa = st.number_input("Tariffa €/ora", min_value=0.0, step=5.0, value=60.0)
                stato = st.selectbox("Stato Pagamento", ["❌ Non Pagata", "💰 Pagata"])
            
            if st.form_submit_button("💾 SALVA NEL DATABASE"):
                if cliente:
                    nuova_riga = pd.DataFrame([{
                        "Data": str(data),
                        "Cliente": cliente,
                        "Attività": attivita,
                        "Ore": float(ore),
                        "Tariffa": float(tariffa),
                        "Totale": float(ore * tariffa),
                        "Stato": stato
                    }])
                    df = pd.concat([df, nuova_riga], ignore_index=True)
                    conn.update(data=df)
                    st.success(f"Pratica per {cliente} salvata!")
                    st.rerun()
                else:
                    st.error("Inserisci il nome del cliente per salvare.")

    # --- 4. CALCOLI E METRICHE ---
    if not df.empty:
        st.divider()
        # Assicuriamoci che i numeri siano trattati come tali
        df["Ore"] = pd.to_numeric(df["Ore"], errors='coerce').fillna(0)
        df["Totale"] = pd.to_numeric(df["Totale"], errors='coerce').fillna(0)

        m1, m2, m3 = st.columns(3)
        m1.metric("Ore Totali", f"{df['Ore'].sum()} h")
        m2.metric("Da Incassare", f"{df[df['Stato'] == '❌ Non Pagata']['Totale'].sum():,.2f} €")
        m3.metric("Incassato (Profitto)", f"{df[df['Stato'] == '💰 Pagata']['Totale'].sum():,.2f} €")

        st.subheader("📋 Elenco Pratiche")
        
        # Ricerca veloce
        cerca = st.text_input("🔍 Cerca cliente o attività...")
        if cerca:
            df_view = df[df.apply(lambda r: cerca.lower() in r.astype(str).str.lower().values, axis=1)]
        else:
            df_view = df
            
        st.dataframe(df_view, use_container_width=True, hide_index=True)

        # --- 5. AZIONI: PAGATO ED ELIMINA ---
        st.divider()
        col_p, col_e = st.columns(2)

        with col_p:
            st.subheader("✅ Segna come Pagato")
            non_pagate = df[df["Stato"] == "❌ Non Pagata"]
            if not non_pagate.empty:
                idx_p = st.selectbox("Seleziona pratica saldata:", non_pagate.index, 
                                    format_func=lambda x: f"{df.at[x, 'Cliente']} - {df.at[x, 'Totale']}€")
                if st.button("Conferma Pagamento"):
                    df.at[idx_p, "Stato"] = "💰 Pagata"
                    conn.update(data=df)
                    st.success("Stato aggiornato!")
                    st.rerun()
            else:
                st.write("Tutte le pratiche risultano pagate! 🎉")

        with col_e:
            st.subheader("🗑️ Elimina Pratica")
            idx_e = st.selectbox("Seleziona riga da cancellare:", df.index, 
                                format_func=lambda x: f"{df.at[x, 'Cliente']} ({df.at[x, 'Data']})")
            if st.button("Elimina Definitivamente", type="primary"):
                df = df.drop(idx_e)
                conn.update(data=df)
                st.warning("Pratica eliminata.")
                st.rerun()

except Exception as e:
    st.error(f"Errore di configurazione: {e}")
    st.info("Assicurati che i Secrets siano impostati correttamente e che il file Google Sheets sia condiviso come Editor.")
