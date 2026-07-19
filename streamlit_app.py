import streamlit as st

st.set_page_config(page_title="Markanow ERP", layout="centered")

# STREAMING_CHUNK: Stil ve Logo Düzenlemesi
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
    .logo-container {
        background-color: white; /* Logonun arkasını tamamen beyaz yapar */
        padding: 10px;
        border-radius: 10px;
        margin-bottom: 20px;
        display: flex;
        justify-content: center;
    }
    .logo-img { 
        width: 100%; 
        max-width: 320px; 
    }
    </style>
""", unsafe_allow_html=True)

if "giris_yapildi" not in st.session_state: st.session_state.giris_yapildi = False

# STREAMING_CHUNK: Giriş Ekranı
if not st.session_state.giris_yapildi:
    st.markdown('<div class="login-card">', unsafe_allow_html=True)
    
    # Yeni linki entegre ettik
    LOGO_URL = "https://i.imgur.com/zZJ3TZW.jpeg"
    
    st.markdown(f'''
        <div class="logo-container">
            <img src="{LOGO_URL}" class="logo-img">
        </div>
    ''', unsafe_allow_html=True)
    
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
