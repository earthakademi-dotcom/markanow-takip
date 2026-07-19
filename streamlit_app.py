import streamlit as st
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta

st.set_page_config(page_title="Markanow ERP & Takip", layout="wide")

def add_months(date_str, months):
    try:
        dt = datetime.strptime(date_str, "%d.%m.%Y")
        return (dt + relativedelta(months=months)).strftime("%d.%m.%Y")
    except: return "-"

# Veri yapısı kontrolü
if "markalar" not in st.session_state:
    st.session_state.markalar = pd.DataFrame(columns=[
        "Marka Adı", "Bülten Tarihi", "İlan Bitiş", "Durum"
    ])

# --- SOL MENÜ ---
def sidebar_menu():
    st.sidebar.title("📌 İşlem Menüsü")
    if st.sidebar.button("📅 Bugünün Hatırlatmaları"): st.session_state.menu = "Hatırlatma"
    if st.sidebar.button("⚙️ Operasyon Paneli"): st.session_state.menu = "Operasyon"
    st.sidebar.markdown("---")
    st.sidebar.subheader("📋 Bülten Süreci")
    if st.sidebar.button("⏳ Bülten Beklemede"): st.session_state.menu = "B_Beklemede"
    if st.sidebar.button("📢 Bültende (Yayında)"): st.session_state.menu = "B_Aktif"
    
    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 Güvenli Çıkış"): 
        st.session_state.giris_yapildi = False
        st.rerun()

sidebar_menu()
if "menu" not in st.session_state: st.session_state.menu = "Hatırlatma"

# --- UYGULAMA MANTIĞI ---
if st.session_state.menu == "B_Beklemede":
    st.subheader("⏳ Bülten Beklemede")
    df = st.session_state.markalar
    st.dataframe(df[df["Bülten Tarihi"].isna() | (df["Bülten Tarihi"] == "-")])

elif st.session_state.menu == "B_Aktif":
    st.subheader("📢 Yayında Olanlar (Bültende)")
    df = st.session_state.markalar
    st.dataframe(df[df["Bülten Tarihi"].notna() & (df["Bülten Tarihi"] != "-")])

elif st.session_state.menu == "Operasyon":
    st.subheader("⚙️ Operasyon Paneli")
    if not st.session_state.markalar.empty:
        m_adi = st.selectbox("Marka Seçin", st.session_state.markalar["Marka Adı"].unique())
        idx = st.session_state.markalar[st.session_state.markalar["Marka Adı"] == m_adi].index[0]
        with st.form("oto_takip"):
            bulten = st.date_input("Bülten Tarihi (Boş ise beklemede kalır)")
            if st.form_submit_button("Hesapla ve Yayınla"):
                if bulten:
                    b_str = bulten.strftime("%d.%m.%Y")
                    st.session_state.markalar.at[idx, "Bülten Tarihi"] = b_str
                    st.session_state.markalar.at[idx, "İlan Bitiş"] = add_months(b_str, 2)
                st.rerun()
    st.dataframe(st.session_state.markalar)

elif st.session_state.menu == "Hatırlatma":
    st.subheader("🔔 Bugünün Hatırlatmaları")
    today = datetime.now().strftime("%d.%m.%Y")
    df = st.session_state.markalar
    st.write(f"Bugün ilan süresi bitenler: {df[df['İlan Bitiş'] == today].shape[0]} marka")
    st.dataframe(df[df["İlan Bitiş"] == today])
