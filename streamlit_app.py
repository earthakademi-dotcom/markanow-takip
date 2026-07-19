import streamlit as st

# STREAMING_CHUNK: Sayfa düzeni ve kurumsal arka plan
st.set_page_config(page_title="Markanow ERP", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #eef2f5; }
    .login-card {
        background-color: #ffffff;
        padding: 40px;
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        text-align: center;
        border: 1px solid #e1e4e8;
    }
    .stButton>button { border-radius: 10px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# STREAMING_CHUNK: Oturum yönetimi
if "giris_yapildi" not in st.session_state: st.session_state.giris_yapildi = False

# STREAMING_CHUNK: Giriş ekranı (Kurumsal Kart yapısı)
if not st.session_state.giris_yapildi:
    st.markdown('<div class="login-card">', unsafe_allow_html=True)
    
    # Logonun yüklenmesi
    try:
        st.image("logo.jpeg.jpeg", width=250)
    except Exception:
        st.title("Markanow")

    tab1, tab2 = st.tabs(["Giriş Yap", "Yeni Kullanıcı Kayıt"])
    
    with tab1:
        k_adi = st.text_input("Kullanıcı Adı")
        sifre = st.text_input("Şifre", type="password")
        if st.button("Giriş Yap", use_container_width=True):
            if k_adi == "admin" and sifre == "1234":
                st.session_state.giris_yapildi = True
                st.rerun()
            else:
                st.error("Kullanıcı adı veya şifre hatalı!")
                
    with tab2:
        st.text_input("Yeni Kullanıcı Adı", key="reg_u")
        st.text_input("Yeni Şifre", type="password", key="reg_p")
        if st.button("Kayıt Talebi Gönder", use_container_width=True):
            st.success("Talebiniz yöneticiye iletildi.")
            
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# STREAMING_CHUNK: Giriş sonrası panel
st.header("Markanow Yönetim Paneli")
if st.button("🚪 Güvenli Çıkış"):
    st.session_state.giris_yapildi = False
    st.rerun()
