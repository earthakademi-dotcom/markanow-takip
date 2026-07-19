import streamlit as st
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta

st.set_page_config(page_title="Markanow Operasyon", layout="wide")

# STREAMING_CHUNK: Geri Butonu Yardımcı Fonksiyonu
def geri_butonu():
    if st.button("⬅️ Geri Dön"):
        st.session_state.menu = "Hatırlatma"
        st.rerun()

# STREAMING_CHUNK: Genel Veri Hazırlığı
if "markalar" not in st.session_state:
    st.session_state.markalar = pd.DataFrame(columns=[
        "Marka Adı", "Süreç", "Tescil Tebliğ Tarihi", "Durum"
    ])

# STREAMING_CHUNK: Menü Yönetimi
def sidebar_menu():
    st.sidebar.title("📌 İşlem Menüsü")
    if st.sidebar.button("📅 Bugünün Hatırlatmaları"): st.session_state.menu = "Hatırlatma"
    if st.sidebar.button("⚙️ Operasyon Paneli"): st.session_state.menu = "Operasyon"
    st.sidebar.markdown("---")
    st.sidebar.subheader("📋 Süreç Takip")
    if st.sidebar.button("⏳ Tescil Tebliğ Beklemede"): st.session_state.menu = "Tescil_Beklemede"

sidebar_menu()
if "menu" not in st.session_state: st.session_state.menu = "Hatırlatma"

# STREAMING_CHUNK: Sayfa İçerikleri
if st.session_state.menu == "Tescil_Beklemede":
    geri_butonu() # Geri butonu her sayfada üstte
    st.subheader("⏳ Tescil Tebliğ Beklemede")
    df = st.session_state.markalar[st.session_state.markalar["Süreç"] == "Tescil Tebliğ Süreci"]
    for index, row in df.iterrows():
        col1, col2 = st.columns([1, 10])
        if col1.button(f"🔵 İşlem", key=f"btn_{index}"):
            st.session_state.menu = "Operasyon"
            st.session_state.secili_marka = row["Marka Adı"]
            st.rerun()
        col2.write(f"**{row['Marka Adı']}**")

elif st.session_state.menu == "Operasyon":
    geri_butonu()
    st.subheader("⚙️ Operasyon Paneli")
    # ... mevcut operasyon mantığı ...
    st.dataframe(st.session_state.markalar)

elif st.session_state.menu == "Hatırlatma":
    st.subheader("🔔 Bugünün Hatırlatmaları")
    st.dataframe(st.session_state.markalar)
