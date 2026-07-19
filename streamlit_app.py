import streamlit as st
import pandas as pd

# --- KULLANICI LİSTESİ ---
KULLANICILAR = {
    "Ali Osman Yelbey": {"sifre": "MarkanowAdmin2026!", "rol": "Admin"},
    "Buğra Büyükeren": {"sifre": "BugraVekil456!", "rol": "Admin"},
    "MERVE YURTLU": {"sifre": "MerveDanisman789!", "rol": "Marka Danışmanı"},
    "Ahmet Yılmaz": {"sifre": "AhmetDanisman321!", "rol": "Marka Danışmanı"},
    "Muhasebe Kullanıcısı": {"sifre": "Muhasebe987!", "rol": "Muhasebe"}
}

# --- OTURUM YÖNETİMİ ---
if "giris_yapildi" not in st.session_state:
    st.session_state.giris_yapildi = False

if not st.session_state.giris_yapildi:
    st.title("🔒 Markanow Giriş")
    kullanici = st.selectbox("Kullanıcı Adı", list(KULLANICILAR.keys()))
    sifre = st.text_input("Şifre", type="password")
    
    if st.button("Giriş Yap"):
        if KULLANICILAR[kullanici]["sifre"] == sifre:
            st.session_state.giris_yapildi = True
            st.session_state.kullanici_adi = kullanici
            st.rerun()
        else:
            st.error("Hatalı şifre!")
    st.stop()

# --- GİRİŞ YAPILDIKTAN SONRAKİ ARAYÜZ ---
st.set_page_config(page_title="Markanow ERP", layout="wide")

# ... (Kalan tasarım ve menü kodlarınız buraya eklenecek) ...

st.write(f"Hoş geldiniz, {st.session_state.kullanici_adi}")
if st.button("🚪 Güvenli Çıkış"):
    st.session_state.giris_yapildi = False
    st.rerun()
