import streamlit as st
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta

st.set_page_config(page_title="Markanow Otomasyon", layout="wide")

# --- HESAPLAMA ---
def add_months(date_str, months):
    try:
        dt = datetime.strptime(date_str, "%d.%m.%Y")
        return (dt + relativedelta(months=months)).strftime("%d.%m.%Y")
    except: return "-"

# --- VERİ HAZIRLIĞI ---
if "markalar" not in st.session_state:
    st.session_state.markalar = pd.DataFrame(columns=[
        "Marka Adı", "Başvuru No", "Başvuru Tarihi", "Bülten Tarihi", 
        "Tescil Tebliğ Tarihi", "İtiraz Tebliğ Tarihi", "Durum"
    ])

# --- SOL MENÜ ---
def sidebar_menu():
    st.sidebar.title("📌 İşlem Menüsü")
    
    st.sidebar.subheader("🎯 Başvuru Süreci")
    if st.sidebar.button("⏳ Başvuru Beklemede"): st.session_state.menu = "Basvuru_Beklemede"
    if st.sidebar.button("📋 Bülten Beklemede"): st.session_state.menu = "Bulten_Beklemede"
    
    st.sidebar.subheader("📋 Süreç Takip")
    if st.sidebar.button("📢 Bültende (Yayında)"): st.session_state.menu = "Bultende"
    if st.sidebar.button("⚖️ İtiraz Beklemede"): st.session_state.menu = "Itiraz_Beklemede"
    if st.sidebar.button("📄 Tescil Tebliğ Beklemede"): st.session_state.menu = "Tescil_Beklemede"
    if st.sidebar.button("💰 Tescil Kurum Ödeme Beklemede"): st.session_state.menu = "Odeme_Beklemede"
    if st.sidebar.button("❌ Red Edilenler"): st.session_state.menu = "Red"

sidebar_menu()

# --- UYGULAMA MANTIĞI ---
if "menu" not in st.session_state: st.session_state.menu = "Basvuru_Beklemede"

st.subheader(f"⚙️ {st.session_state.menu.replace('_', ' ')}")

# Örnek Operasyon Paneli (Burada durum değişikliği ve tarih girişi yapılır)
with st.expander("🛠 Operasyon Paneli (Veri Güncelleme)"):
    m_adi = st.selectbox("Marka Seçin", st.session_state.markalar["Marka Adı"].unique() if not st.session_state.markalar.empty else [])
    # ... buraya form alanları (Başvuru No, Bülten Tarihi, vb.) gelecek ...
    # Otomatik geçiş mantığı örneği:
    # if bulten_tarihi_girildi: durum = "Bültende"
    # if itiraz_teblig_girildi: durum = "Itiraz_Beklemede"

# --- LİSTELEME ---
df = st.session_state.markalar
if st.session_state.menu == "Basvuru_Beklemede":
    st.dataframe(df[df["Durum"] == "Başvuru Beklemede"])
elif st.session_state.menu == "Bulten_Beklemede":
    st.dataframe(df[df["Durum"] == "Bülten Beklemede"])
elif st.session_state.menu == "Bultende":
    st.dataframe(df[df["Durum"] == "Bültende"])
elif st.session_state.menu == "Itiraz_Beklemede":
    st.dataframe(df[df["Durum"] == "İtiraz Beklemede"])
elif st.session_state.menu == "Tescil_Beklemede":
    st.dataframe(df[df["Durum"] == "Tescil Tebliğ Beklemede"])
