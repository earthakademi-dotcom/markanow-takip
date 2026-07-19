import streamlit as st

# STREAMING_CHUNK: Sayfa düzeni ve kurumsal arayüz tanımlamaları
st.set_page_config(page_title="Markanow ERP & Satış Takip", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #f4f7f6; }
    .login-card {
        background-color: #ffffff;
        padding: 40px;
        border-radius: 20px;
        box-shadow: 0 8px 20px rgba(0,0,0,0.1);
        text-align: center;
        border: 1px solid #e0e0e0;
    }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# STREAMING_CHUNK: Oturum durumu yönetimi
if "giris_yapildi" not in st.session_state:
    st.session_state.giris_yapildi = False

# STREAMING_CHUNK: Giriş ekranı (Kurumsal Kart)
if not st.session_state.giris_yapildi:
    st.markdown('<div class="login-card">', unsafe_allow_html=True)
    
    # Logonun yerleşimi
    LOGO_URL = "https://i.imgur.com/dhN0tyf.jpeg"
    st.markdown(f'<img src="{LOGO_URL}" width="280" style="margin-bottom:25px;">', unsafe_allow_html=True)
    
    # Giriş ve Kayıt sekmeleri
    tab1, tab2 = st.tabs(["🔑 Giriş Yap", "📝 Kayıt Ol"])
    
    with tab1:
        k_adi = st.text_input("Kullanıcı Adı")
        sifre = st.text_input("Şifre", type="password")
        if st.button("Giriş Yap"):
            if k_adi == "admin" and sifre == "1234":
                st.session_state.giris_yapildi = True
                st.rerun()
            else:
                st.error("Kullanıcı adı veya şifre hatalı!")
                
    with tab2:
        st.text_input("Yeni Kullanıcı Adı", key="new_u")
        st.text_input("Yeni Şifre", type="password", key="new_p")
        if st.button("Kayıt Talebi Gönder"):
            st.success("Kayıt talebiniz yöneticiye başarıyla iletildi.")
            
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# STREAMING_CHUNK: Giriş sonrası ana yönetim paneli
st.header("Markanow Yönetim Paneli")
st.write("Hoş geldiniz, işlemlerinize başlayabilirsiniz.")

if st.button("🚪 Güvenli Çıkış"):
    st.session_state.giris_yapildi = False
    st.rerun()
