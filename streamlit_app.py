import streamlit as st
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta

st.set_page_config(page_title="Markanow Operasyon", layout="wide")

# --- YARDIMCI ---
def geri_butonu():
    if st.button("⬅️ Geri Dön"):
        st.session_state.menu = "Hatırlatma"
        st.rerun()

# --- VERİ YAPISI ---
if "markalar" not in st.session_state:
    st.session_state.markalar = pd.DataFrame(columns=[
        "Marka Adı", "Süreç", "Tescil Tebliğ Tarihi", "Durum"
    ])

# --- MENÜ ---
def sidebar_menu():
    st.sidebar.title("📌 İşlem Menüsü")
    if st.sidebar.button("📅 Bugünün Hatırlatmaları"): st.session_state.menu = "Hatırlatma"
    if st.sidebar.button("⚙️ Operasyon Paneli"): st.session_state.menu = "Operasyon"
    st.sidebar.markdown("---")
    st.sidebar.subheader("📋 Süreç Takip")
    if st.sidebar.button("⏳ Tescil Tebliğ Beklemede"): st.session_state.menu = "Tescil_Beklemede"

sidebar_menu()
if "menu" not in st.session_state: st.session_state.menu = "Hatırlatma"

# --- SAYFALAR ---
if st.session_state.menu == "Tescil_Beklemede":
    geri_butonu()
    st.subheader("⏳ Tescil Tebliğ Beklemede")
    
    # Süreç bazlı filtreleme
    df_tescil = st.session_state.markalar[st.session_state.markalar["Süreç"] == "Tescil Tebliğ Süreci"]
    
    if df_tescil.empty:
        st.info("Şu an tescil tebliğ bekleyen marka bulunmuyor.")
    else:
        for index, row in df_tescil.iterrows():
            col1, col2 = st.columns([1, 10])
            if col1.button(f"🔵 İşlem", key=f"btn_{index}"):
                st.session_state.menu = "Operasyon"
                st.session_state.secili_marka = row["Marka Adı"]
                st.rerun()
            col2.write(f"**{row['Marka Adı']}**")

elif st.session_state.menu == "Operasyon":
    geri_butonu()
    st.subheader("⚙️ Operasyon Paneli")
    if not st.session_state.markalar.empty:
        # Marka seçimi
        m_list = st.session_state.markalar["Marka Adı"].unique().tolist()
        secili = st.session_state.get("secili_marka", m_list[0])
        m_adi = st.selectbox("Marka Seçin", m_list, index=m_list.index(secili))
        idx = st.session_state.markalar[st.session_state.markalar["Marka Adı"] == m_adi].index[0]
        
        with st.form("tarih_form"):
            tarih = st.date_input("Tescil Tebliğ Tarihi")
            if st.form_submit_button("Tarihi Kaydet"):
                st.session_state.markalar.at[idx, "Tescil Tebliğ Tarihi"] = tarih.strftime("%d.%m.%Y")
                st.success("Tarih kaydedildi!")
                st.rerun()
    else:
        st.warning("Henüz sistemde kayıtlı marka bulunmuyor.")

elif st.session_state.menu == "Hatırlatma":
    st.subheader("🔔 Bugünün Hatırlatmaları")
    st.dataframe(st.session_state.markalar)
