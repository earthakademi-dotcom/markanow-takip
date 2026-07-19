import streamlit as st
import pandas as pd

# STREAMING_CHUNK: Stil ve Kurumsal Görünüm
st.set_page_config(page_title="Markanow ERP", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #f0f2f6; }
    .login-container { 
        background: white; padding: 30px; border-radius: 15px; 
        box-shadow: 0 4px 15px rgba(0,0,0,0.1); 
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# STREAMING_CHUNK: Kullanıcı Veritabanı (Başlangıç için)
if "KULLANICILAR" not in st.session_state:
    st.session_state.KULLANICILAR = {
        "admin": {"sifre": "1234", "rol": "Admin"}
    }

# STREAMING_CHUNK: Giriş ve Kayıt Ekranı
if not st.session_state.get("giris_yapildi", False):
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    # Logoyu yerleştiriyoruz
    st.image("https://upload.wikimedia.org/wikipedia/commons/e/e4/Markanow_Logo.png", width=200) # Logonuzun URL'sini buraya ekleyin
    
    tab1, tab2 = st.tabs(["Giriş Yap", "Yeni Kullanıcı Kayıt"])
    
    with tab1:
        k_adi = st.text_input("Kullanıcı Adı")
        sifre = st.text_input("Şifre", type="password")
        if st.button("Giriş Yap"):
            user = st.session_state.KULLANICILAR.get(k_adi)
            if user and user["sifre"] == sifre:
                st.session_state.giris_yapildi = True
                st.session_state.kullanici_adi = k_adi
                st.rerun()
            else: st.error("Hatalı bilgiler!")

    with tab2:
        yeni_k = st.text_input("Yeni Kullanıcı Adı")
        yeni_s = st.text_input("Yeni Şifre", type="password")
        if st.button("Kaydet"):
            st.session_state.KULLANICILAR[yeni_k] = {"sifre": yeni_s, "rol": "Kullanıcı"}
            st.success("Kullanıcı oluşturuldu! Giriş yapabilirsiniz.")
            
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- Giriş Yapıldıktan Sonra ---
st.title(f"Hoş geldiniz, {st.session_state.kullanici_adi}")
if st.button("🚪 Güvenli Çıkış"):
    st.session_state.giris_yapildi = False
    st.rerun()
