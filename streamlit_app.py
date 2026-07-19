import streamlit as st
import pandas as pd

# --- OTURUM YÖNETİMİ BAŞLANGICI ---
if "giris_yapildi" not in st.session_state:
    st.session_state.giris_yapildi = False

# Eğer giriş yapılmadıysa login ekranını göster
if not st.session_state.giris_yapildi:
    st.title("🔒 Markanow Giriş")
    kullanici = st.text_input("Kullanıcı Adı")
    sifre = st.text_input("Şifre", type="password")
    if st.button("Giriş Yap"):
        # Basit bir kontrol (kendi kullanıcı listenize göre güncelleyebilirsiniz)
        if kullanici == "admin" and sifre == "1234":
            st.session_state.giris_yapildi = True
            st.rerun()
        else:
            st.error("Hatalı bilgiler!")
    st.stop()

# --- GİRİŞ YAPILDIKTAN SONRAKİ ARAYÜZ ---
st.set_page_config(page_title="Markanow ERP", layout="wide")

# --- TASARIM VE STİL ---
st.markdown("""
    <style>
    [data-testid="stSidebar"] { background-color: #ffffff; border-right: 1px solid #e1e4e8; }
    .stButton>button { 
        width: 100%; border-radius: 5px; border: none; 
        background-color: #f8f9fa; color: #34495e; 
        text-align: left; padding: 10px 15px; margin-bottom: 5px;
    }
    .stButton>button:hover { background-color: #e9ecef; }
    </style>
""", unsafe_allow_html=True)

# --- MENÜ VE ÇIKIŞ MANTIĞI ---
def sidebar_menu():
    with st.sidebar:
        st.markdown("### 🏢 MARKANOW ERP")
        # ... (diğer menü butonları) ...
        
        st.markdown("---")
        # GÜVENLİ ÇIKIŞ BUTONU
        if st.button("🚪 Güvenli Çıkış"):
            # Tüm session verilerini temizle
            for key in st.session_state.keys():
                del st.session_state[key]
            st.rerun()

sidebar_menu()

st.title("Hoş Geldiniz")
st.write("Sisteminiz başarıyla çalışıyor.")
