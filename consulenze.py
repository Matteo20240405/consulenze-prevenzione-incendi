import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import os
from PIL import Image

# --- 1. CONFIGURAZIONE PAGINA E LOGO ---
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

# --- 2. CREDENZIALI E CONNESSIONE ---
service_info = {
    "type": "service_account",
    "project_id": "gestionale-incendi",
    "private_key_id": "3794050ab4dd3ab03f1fae6b3e6913e5db3d20de",
    "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCvRztElIINAC73\niVaQCAxbFwYTHVjEfV1GKJEVZMxmen7PsAvYy6pO41tYT0gF6EUfYzApe5Fiy8uE\nudsmhjb15UHeF6cKD+lupPtvV14rQB8PRgg+balm5182ySawr96os/ZLNfFzcF34\n7o3EmPvjQHxmxnlDYNYb6QYotr1QIC/VFee+Y8Zf20LkIBKzbG/dkiBr9J3CiFBs\nachwgYX9F+XjlMpuT+0iLvbAm7uNfareFh4WYrudnxp7PB9Ps8IX6iHfCbj2gkk7\nQWPlYkyZTIr6Mcap+6lRvfDWbaf9RcV+dRl4hpVl4oDzctlIWtyz84yJ0bRILKZd\n2PWGOScfAgMBAAECggEAC8mvFzgjnOs3vWcLnskjx5Z/TpbJKwHBXaAJzdYHFxdC\n4wXUbiKYVBDfSkuerOMHjwpVKV0JlIrfJ5B2SBt7o8Lk0KJnlfom+U14KW9HQoJf\n9F+B22z1mRmTYjRZ+UUCpPbhaAJ7OAfFEiI8/41IV2q1UxYi/qCLFbpwsxlDFxnO\ndoCaS1rvRcDub5Vkk40vGvqpES+f/PmZeDAv19bWsiPkVvAlYC3T70zNV7Cqm2rT\nPabus1nYrsf/EBQtUD6b5ELo2ALiyS6BeEhbEfZa4hqRVOSKNle5bKPhd8LIjCcK\nbvU6G3C2C0ABf7O3bssU55C309McsH5D2xGR1j/zmQKBgQDmLyNo9PNQxqWMJt1s\n5gzYC24fJgmgc1Con5+lCgbgjeEAdThyo95+CBdB/brrX/ILnYfvs5sJ0kRybrDL\nRlxZ9Lq8zkin26XUzWeXWRF1cM7b4kS4vXgaXwmV5j68C1ut0lEXtwNCzB1g0nk3\nAs/GprllViFAZ21EAbzRwBVGlwKBgQDC7634J0I/QEXv3OV5OhbdP9f4zUw9Mdn4\nmwDolwaYQDhoVKGAV78r1ahEFL7RRtC7P9kststLLwOKkU7BD/8Vfj3Sf4E3b4dp\qsK/qg77yCJpGyDFYqEFGKxGg43IMt/7J2IQhzzIMQs3jZtFQF+DNbQpjUGoq0j2\nTm+NWZh8uQKBgQCY3k1h8ut0hbiD73u2SsHU6SJlRVm3WV4D3p6jeJlAoHkBWNf4\nKqQkhzMK/Hsavkl9NU2F/33DdAVJCgIXvc6vXzx1D3ppIBJt1Uwq01go6pY2qXqC\nRjJxMRSonJSlRdXJBpgca8qanfwUxTMDObbLcwZFKoJCx21lcNH5atu2WQKBgB1l\nfYuth+z36VQJsMU+QFJvHUeU1gloaiF2ZoWsuL7e+GKrWIt9MAQRPUW/ByOSFUoX\nj82RZ0jYNyV/UiwFGIeKORJ0Te0pMXd629GBeK75eE73W1LI09Vr6hbcIdZt7Z73\nSm+JpV3fH3zqKt8fnQexYpDdj2g7JE6Yd3QObdNpAoGACrT6cdFNz4lBcGsNg7Lb\nOcQkf3XG1eza0PbM6Vh1yiQ/GRsYnOZZQH4aKIbNTcH3jQ47gGGmhErgS7hyh3PE\nB7kwNTxBV1deXpgvIZ9Xvk9mToRmkJpMsDqTkQjAL0FIViK53BetGf2IZNh9pFlh\nt5H74X4javFdQ57BwyyZsGs=\n-----END PRIVATE KEY-----\n",
    "client_email": "consulenza@gestionale-incendi.iam.gserviceaccount.com",
    "client_id": "106428390095267440624",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/consulenza%40gestionale-incendi.iam.gserviceaccount.com"
}

SHEET_URL = "https://docs.google.com/spreadsheets/d/12orchamSx43ERvYjZ6VpnFr3dqZRxr6GTMxpIEbKMwM/edit#gid=0"

conn = st.connection("gsheets", type=GSheetsConnection, service_account_info=service_info)

try:
    df = conn.read(spreadsheet=SHEET_URL, ttl=0)
except Exception as e:
    st.error(f"Errore di lettura: {e}")
    df = pd.DataFrame()

if df is None or df.empty:
    df = pd.DataFrame(columns=["Data", "Cliente", "Tipologia", "Attività", "Ore", "Tariffa", "Totale", "Stato"])

# --- 3. INTERFACCIA ---
if os.path.exists(logo_path):
    st.image(logo_path, width=150)

st.title("🔥 Registro Professionale Prevenzione Incendi")

with st.expander("➕ AGGIUNGI NUOVA PRESTAZIONE", expanded=True):
    with st.form("form_nuovo", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            data = st.date_input("Data")
            cliente = st.text_input("Cliente/Condominio")
            tipologia = st.text_input("Tipologia")
        with c2:
            attivita = st.text_input("Attività")
            ore = st.number_input("Ore", min_value=0.5, step=0.5, value=1.0)
            tariffa = st.number_input("Tariffa €/ora", value=60.0)
        
        stato = st.selectbox("Stato Pagamento", ["❌ Non Pagata", "💰 Pagata"])
        
        if st.form_submit_button("💾 SALVA NEL CLOUD"):
            if cliente:
                nuova_riga = pd.DataFrame([{
                    "Data": str(data), "Cliente": cliente, "Tipologia": tipologia,
                    "Attività": attivita, "Ore": float(ore), "Tariffa": float(tariffa),
                    "Totale": float(ore * tariffa), "Stato": stato
                }])
                df = pd.concat([df, nuova_riga], ignore_index=True)
                conn.update(spreadsheet=SHEET_URL, data=df)
                st.success("Dati salvati!")
                st.rerun()

# --- 4. VISUALIZZAZIONE ---
if not df.empty:
    st.divider()
    df["Ore"] = pd.to_numeric(df["Ore"], errors='coerce').fillna(0)
    df["Totale"] = pd.to_numeric(df["Totale"], errors='coerce').fillna(0)
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Ore Totali", f"{df['Ore'].sum()} h")
    m2.metric("Da Incassare", f"{df[df['Stato'] == '❌ Non Pagata']['Totale'].sum():,.2f} €")
    m3.metric("Incassato", f"{df[df['Stato'] == '💰 Pagata']['Totale'].sum():,.2f} €")

    st.subheader("📋 Elenco Pratiche")
    cerca = st.text_input("🔍 Cerca...")
    df_f = df[df.apply(lambda r: cerca.lower() in r.astype(str).str.lower().values, axis=1)] if cerca else df
    st.dataframe(df_f, use_container_width=True, hide_index=True)

    # GESTIONE PAGAMENTI ED ELIMINAZIONE
    st.divider()
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.subheader("🔄 Pagamenti")
        non_pagate = df[df["Stato"] == "❌ Non Pagata"]
        if not non_pagate.empty:
            scelta_p = st.selectbox("Segna pagato:", non_pagate.index, format_func=lambda x: f"{df.at[x, 'Cliente']} ({df.at[x, 'Totale']}€)")
            if st.button("Conferma Saldo"):
                df.at[scelta_p, "Stato"] = "💰 Pagata"
                conn.update(spreadsheet=SHEET_URL, data=df)
                st.rerun()
    
    with col_b:
        st.subheader("🗑️ Elimina")
        if not df.empty:
            scelta_d = st.selectbox("Elimina riga:", df.index, format_func=lambda x: f"{df.at[x, 'Cliente']} - {df.at[x, 'Data']}")
            if st.button("Elimina", type="primary"):
                df = df.drop(scelta_d)
                conn.update(spreadsheet=SHEET_URL, data=df)
                st.rerun()
