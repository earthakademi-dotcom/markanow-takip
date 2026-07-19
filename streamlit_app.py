import streamlit as st

# STREAMING_CHUNK: Sayfa Yapılandırması
st.set_page_config(page_title="Markanow Giriş", layout="centered")

# STREAMING_CHUNK: Minimalist Tasarım (Sade arka plan)
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    /* Herhangi bir kart, çerçeve veya logo stili yoktur */
    </style>
""", unsafe_allow_html=True)

if "giris_yapildi" not in st.session_state: st.session_state.giris_yapildi = False

# STREAMING_CHUNK: Giriş Formu (Yalın hali)
if not st.session_state.giris_yapildi:
    st.title("Markanow Satış Yönetim Paneli")
    st.markdown("---")
    
    k_adi = st.text_input("Kullanıcı Adı")
    sifre = st.text_input("Şifre", type="password")
    
    if st.button("Giriş Yap", use_container_width=True):
        if k_adi == "admin" and sifre == "1234":
            st.session_state.giris_yapildi = True
            st.rerun()
        else:
            st.error("Kullanıcı adı veya şifre hatalı!")
    
    st.stop()

# STREAMING_CHUNK: Giriş Sonrası
st.header("Markanow Satış Yönetim Paneli")
if st.button("Çıkış"):
    st.session_state.giris_yapildi = False
    st.rerun()
