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
        "Marka Adı", "Bülten Tarihi", "İlan Bitiş", "Durum", "Süreç"
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
    if st.sidebar.button("⚖️ İtiraz Süreci"): st.session_state.menu = "İtiraz"
    if st.sidebar.button("📄 Tescil Tebliğ Süreci"): st.session_state.menu = "Tescil"

sidebar_menu()
if "menu" not in st.session_state: st.session_state.menu = "Hatırlatma"

# --- UYGULAMA MANTIĞI ---
if st.session_state.menu == "B_Beklemede":
    st.subheader("⏳ Bülten Beklemede")
    df = st.session_state.markalar
    st.dataframe(df[df["Bülten Tarihi"].isna() | (df["Bülten Tarihi"] == "-")])

elif st.session_state.menu == "B_Aktif":
    st.subheader("📢 Yayında Olanlar")
    df = st.session_state.markalar
    st.dataframe(df[df["Bülten Tarihi"].notna() & (df["Bülten Tarihi"] != "-")])

elif st.session_state.menu == "Operasyon":
    st.subheader("⚙️ Operasyon Paneli")
    if not st.session_state.markalar.empty:
        m_adi = st.selectbox("Marka Seçin", st.session_state.markalar["Marka Adı"].unique())
        idx = st.session_state.markalar[st.session_state.markalar["Marka Adı"] == m_adi].index[0]
        with st.form("oto_takip"):
            bulten = st.date_input("Bülten Tarihi")
            surec = st.selectbox("İlan Sonrası Durum Seçin", ["Tescil Tebliğ Süreci", "İtiraz Süreci"])
            if st.form_submit_button("Hesapla ve İlerlet"):
                b_str = bulten.strftime("%d.%m.%Y")
                st.session_state.markalar.at[idx, "Bülten Tarihi"] = b_str
                st.session_state.markalar.at[idx, "İlan Bitiş"] = add_months(b_str, 2)
                st.session_state.markalar.at[idx, "Süreç"] = surec
                st.success("Süreç otomatik ilerletildi!")
                st.rerun()
    st.dataframe(st.session_state.markalar)

elif st.session_state.menu == "İtiraz":
    st.subheader("⚖️ İtiraz Süreci")
    st.dataframe(st.session_state.markalar[st.session_state.markalar["Süreç"] == "İtiraz Süreci"])

elif st.session_state.menu == "Tescil":
    st.subheader("📄 Tescil Tebliğ Süreci")
    st.dataframe(st.session_state.markalar[st.session_state.markalar["Süreç"] == "Tescil Tebliğ Süreci"])

elif st.session_state.menu == "Hatırlatma":
    st.subheader("🔔 Bugünün Hatırlatmaları")
    today = datetime.now().strftime("%d.%m.%Y")
    df = st.session_state.markalar
    st.dataframe(df[df["İlan Bitiş"] == today])
