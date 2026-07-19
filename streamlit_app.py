import streamlit as st
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta

st.set_page_config(page_title="Markanow Operasyon", layout="wide")

def add_months(date_str, months):
    try:
        dt = datetime.strptime(date_str, "%d.%m.%Y")
        return (dt + relativedelta(months=months)).strftime("%d.%m.%Y")
    except: return "-"

if "markalar" not in st.session_state:
    st.session_state.markalar = pd.DataFrame(columns=[
        "Marka Adı", "Bülten Tarihi", "İlan Bitiş", "Süreç", "Tescil Tebliğ Tarihi"
    ])

# --- SOL MENÜ ---
def sidebar_menu():
    st.sidebar.title("📌 İşlem Menüsü")
    if st.sidebar.button("📅 Bugünün Hatırlatmaları"): st.session_state.menu = "Hatırlatma"
    if st.sidebar.button("⚙️ Operasyon Paneli"): st.session_state.menu = "Operasyon"
    st.sidebar.markdown("---")
    st.sidebar.subheader("📋 Süreç Takip")
    if st.sidebar.button("⏳ Bülten Beklemede"): st.session_state.menu = "B_Beklemede"
    if st.sidebar.button("📢 Bültende (Yayında)"): st.session_state.menu = "B_Aktif"
    if st.sidebar.button("⏳ Tescil Tebliğ Beklemede"): st.session_state.menu = "Tescil_Beklemede"
    if st.sidebar.button("⚖️ İtiraz Süreci"): st.session_state.menu = "İtiraz"

sidebar_menu()
if "menu" not in st.session_state: st.session_state.menu = "Hatırlatma"

# --- UYGULAMA ---
if st.session_state.menu == "Tescil_Beklemede":
    st.subheader("⏳ Tescil Tebliğ Beklemede")
    st.dataframe(st.session_state.markalar[st.session_state.markalar["Süreç"] == "Tescil Tebliğ Süreci"])

elif st.session_state.menu == "Operasyon":
    st.subheader("⚙️ Operasyon Paneli")
    if not st.session_state.markalar.empty:
        m_adi = st.selectbox("Marka Seçin", st.session_state.markalar["Marka Adı"].unique())
        idx = st.session_state.markalar[st.session_state.markalar["Marka Adı"] == m_adi].index[0]
        
        # Süreç belirleme formu
        with st.form("oto_takip"):
            bulten = st.date_input("Bülten Tarihi")
            surec = st.selectbox("Süreç", ["Tescil Tebliğ Süreci", "İtiraz Süreci"])
            if st.form_submit_button("Hesapla ve İlerlet"):
                st.session_state.markalar.at[idx, "Bülten Tarihi"] = bulten.strftime("%d.%m.%Y")
                st.session_state.markalar.at[idx, "Süreç"] = surec
                st.rerun()

        # Tescil Tebliğ Tarihi giriş formu (Eğer tescil sürecindeyse)
        if st.session_state.markalar.at[idx, "Süreç"] == "Tescil Tebliğ Süreci":
            with st.form("tescil_form"):
                tt_tarih = st.date_input("Tescil Tebliğ Tarihi Girin")
                if st.form_submit_button("Tebliğ Tarihini Kaydet"):
                    st.session_state.markalar.at[idx, "Tescil Tebliğ Tarihi"] = tt_tarih.strftime("%d.%m.%Y")
                    st.rerun()
    st.dataframe(st.session_state.markalar)

# ... (Diğer menülerin kodları aynı kalır)
