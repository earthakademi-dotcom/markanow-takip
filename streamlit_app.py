import streamlit as st
import pandas as pd

# --- OTURUM YÖNETİMİ ---
if "giris_yapildi" not in st.session_state:
    st.session_state.giris_yapildi = False

# --- MENÜ İLKLENDİRME ---
# Hatanın sebebi: 'menu' anahtarının olmaması. .get() ile bunu garantiye alıyoruz.
if "menu" not in st.session_state:
    st.session_state.menu = "Basvuru_Beklemede"

# --- LOGIN MANTIĞI ---
if not st.session_state.giris_yapildi:
    # ... Login kodlarınız ...
    st.stop()

# --- GÜVENLİ ERİŞİM ---
# Artık menu her zaman var
if st.session_state.menu == "Sifre_Ayarlari":
    st.subheader("🔑 Şifre Yönetimi")
    # ... Şifre değiştirme formunuz ...

# --- SİDEBAR ---
with st.sidebar:
    if st.button("🔑 Şifre Ayarları"): 
        st.session_state.menu = "Sifre_Ayarlari"
        st.rerun()
