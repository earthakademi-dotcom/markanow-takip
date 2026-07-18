import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Markanow ERP & Satış Takip", layout="wide")

KULLANICILAR = {
    "Ali Osman Yelbey": {"sifre": "MarkanowAdmin2026!", "rol": "Admin"},
    "Buğra Büyükeren": {"sifre": "BugraVekil456!", "rol": "Admin"},
    "MERVE YURTLU": {"sifre": "MerveDanisman789!", "rol": "Marka Danışmanı"},
    "Ahmet Yılmaz": {"sifre": "AhmetDanisman321!", "rol": "Marka Danışmanı"},
    "Muhasebe Kullanıcısı": {"sifre": "Muhasebe987!", "rol": "Muhasebe"},
    "Operasyon Yetkilisi": {"sifre": "Operasyon123!", "rol": "Operasyon"}
}

if "giris_yapildi" not in st.session_state:
    st.session_state.giris_yapildi = False
if "markalar" not in st.session_state:
    st.session_state.markalar = pd.DataFrame(columns=[
        "Marka Adı", "Ad Soyad", "Telefon", "TC Kimlik", "Sınıf Kodu", "Personel", 
        "Satış Tarihi", "Ödeme Seçeneği", "Başvuru Ücreti", "B. Onay", "Fatura No",
        "Başvuru No", "Başvuru Tarihi", "Bülten Tarihi"
    ])

def str_to_date(d):
    try: return datetime.strptime(d, "%d.%m.%Y")
    except: return datetime(2000, 1, 1)

if not st.session_state.giris_yapildi:
    st.title("🔒 Markanow Takip Sistemi")
    kullanici = st.selectbox("Kullanıcı Adı", list(KULLANICILAR.keys()))
    sifre = st.text_input("Şifre", type="password")
    if st.button("Giriş Yap"):
        if sifre == KULLANICILAR[kullanici]["sifre"]:
            st.session_state.giris_yapildi = True
            st.session_state.kullanici_adi = kullanici
            st.session_state.kullanici_rolu = KULLANICILAR[kullanici]["rol"]
            st.rerun()
    st.stop()

st.sidebar.title(f"👤 {st.session_state.kullanici_adi}")

# --- TAKİP MENÜLERİ ---
if st.sidebar.button("İlan Bitişi Gelenler"): st.session_state.tab = "İlan"
if st.sidebar.button("Savunma Süresi Gelenler"): st.session_state.tab = "Savunma"
if st.sidebar.button("Tescil Ödemesi Gelenler"): st.session_state.tab = "Tescil"

if st.sidebar.button("Güvenli Çıkış Yap"):
    st.session_state.giris_yapildi = False
    st.rerun()

# --- MANTIKSAL KONTROLLER ---
if st.session_state.kullanici_rolu in ["Marka Danışmanı", "Admin"]:
    st.subheader("📝 Yeni Satış Girişi")
    with st.form("yeni_satis", clear_on_submit=True):
        c1, c2 = st.columns(2)
        m_adi = c1.text_input("Marka Adı")
        tc = c1.text_input("TC Kimlik No (11 Rakam)")
        tel = c1.text_input("Telefon (05... ile başlayın)")
        fiyat = c2.number_input("Başvuru Ücreti", value=0)
        
        if st.form_submit_button("Kaydet"):
            if len(tc) != 11 or not tc.isdigit(): st.error("TC Kimlik 11 rakam olmalı!")
            elif not tel.startswith("05") or len(tel) != 11: st.error("Telefon 05 ile başlamalı ve 11 hane olmalı!")
            else:
                yeni = pd.DataFrame([{"Marka Adı": m_adi, "TC Kimlik": tc, "Telefon": tel, "Başvuru Ücreti": fiyat, "B. Onay": "Bekliyor"}])
                st.session_state.markalar = pd.concat([st.session_state.markalar, yeni], ignore_index=True)
                st.success("Kaydedildi!")

# --- TAKİP GÖRÜNTÜLEME ---
if "tab" in st.session_state:
    st.subheader(f"🔍 Takip: {st.session_state.tab}")
    df = st.session_state.markalar[st.session_state.markalar["Bülten Tarihi"] != "-"]
    st.dataframe(df)

if st.sidebar.button("Operasyon Paneli"): st.session_state.tab = "Operasyon"
