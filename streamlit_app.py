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
        "Marka Adı", "Bülten Tarihi", "İlan Bitiş", "Durum"
    ])

# --- SOL MENÜ ---
def sidebar_menu():
    st.sidebar.title("📌 İşlem Menüsü")
    st.sidebar.subheader("🎯 Günlük Takip")
    if st.sidebar.button("📅 Bugünün Hatırlatmaları"): st.session_state.menu = "Hatırlatma"
    if st.sidebar.button("⚙️ Operasyon Paneli"): st.session_state.menu = "Operasyon"
    
    st.sidebar.subheader("📋 Bülten Süreci")
    if st.sidebar.button("⏳ Bülten Beklemede"): st.session_state.menu = "B_Beklemede"
    if st.sidebar.button("📢 Bültende Olanlar"): st.session_state.menu = "B_Aktif"
    
    st.sidebar.subheader("📋 Süreç Takip")
    if st.sidebar.button("⏳ Başvuru Beklemede"): st.session_state.menu = "Bekleyen"
    if st.sidebar.button("📄 Tescil Tebliğde"): st.session_state.menu = "Tescil"
    if st.sidebar.button("⚖️ İtiraz Tebliğde"): st.session_state.menu = "İtiraz"

# --- UYGULAMA ---
if "menu" not in st.session_state: st.session_state.menu = "Hatırlatma"
sidebar_menu()

df = st.session_state.markalar

if st.session_state.menu == "B_Beklemede":
    st.subheader("⏳ Bülten Beklemede")
    st.dataframe(df[df["Bülten Tarihi"].isna() | (df["Bülten Tarihi"] == "-")])

elif st.session_state.menu == "B_Aktif":
    st.subheader("📢 Bültende Olanlar")
    st.dataframe(df[df["Bülten Tarihi"].notna() & (df["Bülten Tarihi"] != "-")])

elif st.session_state.menu == "Operasyon":
    st.subheader("⚙️ Operasyon ve Takip")
    if not df.empty:
        m_adi = st.selectbox("Marka Seçin", df["Marka Adı"].unique())
        idx = df[df["Marka Adı"] == m_adi].index[0]
        with st.form("oto_takip"):
            bulten = st.date_input("Bülten Tarihi (Boş bırakırsanız beklemede kalır)")
            durum = st.selectbox("Durum", ["Bekleyen", "İtiraz", "Tescil"])
            if st.form_submit_button("Hesapla ve Güncelle"):
                b_str = bulten.strftime("%d.%m.%Y") if bulten else "-"
                st.session_state.markalar.at[idx, "Bülten Tarihi"] = b_str
                st.session_state.markalar.at[idx, "İlan Bitiş"] = add_months(b_str, 2) if b_str != "-" else "-"
                st.session_state.markalar.at[idx, "Durum"] = durum
                st.rerun()
    st.dataframe(df)

elif st.session_state.menu == "Hatırlatma":
    st.info("📌 Bugünün Takibi")
    today = datetime.now().strftime("%d.%m.%Y")
    st.dataframe(df[(df["İlan Bitiş"] == today)])
