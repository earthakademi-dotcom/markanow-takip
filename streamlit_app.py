import streamlit as st
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta

st.set_page_config(page_title="Markanow Operasyon", layout="wide")

# STREAMING_CHUNK: Yardımcı fonksiyonlar
def add_months(date_str, months):
    try:
        dt = datetime.strptime(date_str, "%d.%m.%Y")
        return (dt + relativedelta(months=months)).strftime("%d.%m.%Y")
    except: return "-"

if "markalar" not in st.session_state:
    st.session_state.markalar = pd.DataFrame(columns=[
        "Marka Adı", "Bülten Tarihi", "İlan Bitiş", "Süreç", "Tescil Tebliğ Tarihi", "Durum"
    ])

# STREAMING_CHUNK: Sidebar ve Menü yönetimi
def sidebar_menu():
    st.sidebar.title("📌 İşlem Menüsü")
    if st.sidebar.button("📅 Bugünün Hatırlatmaları"): st.session_state.menu = "Hatırlatma"
    if st.sidebar.button("⚙️ Operasyon Paneli"): st.session_state.menu = "Operasyon"
    st.sidebar.markdown("---")
    st.sidebar.subheader("📋 Süreç Takip")
    if st.sidebar.button("⏳ Tescil Tebliğ Beklemede"): st.session_state.menu = "Tescil_Beklemede"

sidebar_menu()
if "menu" not in st.session_state: st.session_state.menu = "Hatırlatma"

# STREAMING_CHUNK: Tescil Tebliğ Beklemede Görünümü
if st.session_state.menu == "Tescil_Beklemede":
    st.subheader("⏳ Tescil Tebliğ Beklemede")
    df = st.session_state.markalar[st.session_state.markalar["Süreç"] == "Tescil Tebliğ Süreci"]
    
    # Her satır için bir buton (İşlem Yap)
    for index, row in df.iterrows():
        col1, col2 = st.columns([1, 10])
        if col1.button(f"🔵 İşlem", key=f"btn_{index}"):
            st.session_state.menu = "Operasyon"
            st.session_state.secili_marka = row["Marka Adı"]
            st.rerun()
        col2.write(f"**{row['Marka Adı']}** - {row['Süreç']}")

elif st.session_state.menu == "Operasyon":
    st.subheader("⚙️ Operasyon Paneli")
    # Seçili marka varsa onu otomatik seç
    secili = st.session_state.get("secili_marka", st.session_state.markalar["Marka Adı"].iloc[0] if not st.session_state.markalar.empty else None)
    
    m_adi = st.selectbox("Marka Seçin", st.session_state.markalar["Marka Adı"].unique(), index=list(st.session_state.markalar["Marka Adı"]).index(secili) if secili in list(st.session_state.markalar["Marka Adı"]) else 0)
    idx = st.session_state.markalar[st.session_state.markalar["Marka Adı"] == m_adi].index[0]
    
    with st.form("oto_takip"):
        tt_tarih = st.date_input("Tescil Tebliğ Tarihi")
        if st.form_submit_button("Tarihi Güncelle"):
            st.session_state.markalar.at[idx, "Tescil Tebliğ Tarihi"] = tt_tarih.strftime("%d.%m.%Y")
            st.success("Tarih kaydedildi!")
            st.rerun()

st.dataframe(st.session_state.markalar)
