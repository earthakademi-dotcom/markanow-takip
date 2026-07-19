import streamlit as st

# STREAMING_CHUNK: Sayfa Yapılandırması
st.set_page_config(page_title="Markanow Yönetim Paneli", layout="centered")

# STREAMING_CHUNK: Stil Düzenlemeleri (Sade ve Kurumsal)
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    .login-card {
        background-color: #ffffff;
        padding: 50px;
        border-radius: 20px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.05);
        text-align: center;
        border: 1px solid #e9ecef;
    }
    .title-text { color: #2c3e50; font-weight: 600; margin-bottom: 30px; }
    </style>
""", unsafe_allow_html=True)

if "giris_yapildi" not in st.session_state: st.session_state.giris_yapildi = False

# STREAMING_CHUNK: Giriş Ekranı
if not st.session_state.giris_yapildi:
    st.markdown('<div class="login-card">', unsafe_allow_html=True)
    
    # Logo
    st.markdown('<img src="https://i.imgur.com/zZJ3TZW.jpeg" style="width:280px; margin-bottom:20px;">', unsafe_allow_html=True)
    
    # Başlık
    st.markdown('<h2 class="title-text">Markanow Satış Yönetim Paneli</h2>', unsafe_allow_html=True)
    
    # Giriş Formu
    k_adi = st.text_input("Kullanıcı Adı")
    sifre = st.text_input("Şifre", type="password")
    
    if st.button("Sisteme Giriş Yap", use_container_width=True):
        if k_adi == "admin" and sifre == "1234":
            st.session_state.giris_yapildi = True
            st.rerun()
        else:
            st.error("Kullanıcı adı veya şifre hatalı!")
            
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# STREAMING_CHUNK: Giriş Sonrası
st.header("Markanow Satış Yönetim Paneli")
if st.button("🚪 Çıkış"):
    st.session_state.giris_yapildi = False
    st.rerun()
