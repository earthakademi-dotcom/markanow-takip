import streamlit as st

# STREAMING_CHUNK: Sayfa Yapılandırması
st.set_page_config(page_title="Markanow ERP", layout="centered")

# STREAMING_CHUNK: Stil ve Logo Entegrasyonu
st.markdown("""
    <style>
    .stApp { background-color: #eef2f5; }
    .login-card {
        background-color: #ffffff;
        padding: 40px;
        border-radius: 20px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        text-align: center;
        border: 1px solid #e1e4e8;
    }
    /* Logonun beyaz alanını arka planla birleştirme */
    .logo-img { 
        width: 320px; 
        margin-bottom: 20px;
        mix-blend-mode: multiply; 
    }
    </style>
""", unsafe_allow_html=True)

if "giris_yapildi" not in st.session_state: st.session_state.giris_yapildi = False

# STREAMING_CHUNK: Giriş Ekranı (Merkezi Tasarım)
if not st.session_state.giris_yapildi:
    st.markdown('<div class="login-card">', unsafe_allow_html=True)
    
    LOGO_URL = "https://i.imgur.com/dhN0tyf.jpeg"
    # mix-blend-mode sınıfı logodaki beyaz arka planı kaldırıp web rengiyle birleştirir
    st.markdown(f'<img src="{LOGO_URL}" class="logo-img">', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["Giriş Yap", "Kayıt Ol"])
    
    with tab1:
        k_adi = st.text_input("Kullanıcı Adı")
        sifre = st.text_input("Şifre", type="password")
        if st.button("Giriş Yap", use_container_width=True):
            if k_adi == "admin" and sifre == "1234":
                st.session_state.giris_yapildi = True
                st.rerun()
            else: st.error("Hatalı giriş!")
            
    with tab2:
        st.text_input("Yeni Kullanıcı Adı", key="reg_u")
        st.text_input("Yeni Şifre", type="password", key="reg_p")
        if st.button("Kayıt Talebi Gönder", use_container_width=True):
            st.success("Talebiniz yöneticiye iletildi.")
            
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()
