import streamlit as st
import base64

# STREAMING_CHUNK: Görseli kodun içine gömmek için helper (Hata almamak için en güvenli yol)
def get_image_as_base64(path):
    try:
        with open(path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()
    except: return None

img_base64 = get_image_as_base64("logo.jpeg.jpeg")

st.set_page_config(page_title="Markanow ERP", layout="centered")

# STREAMING_CHUNK: Kurumsal Tasarım
st.markdown("""
    <style>
    .stApp { background-color: #eef2f5; }
    .card {
        background-color: white; padding: 40px; border-radius: 20px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1); text-align: center;
    }
    .logo-img { width: 250px; margin-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)

if "giris_yapildi" not in st.session_state: st.session_state.giris_yapildi = False

# STREAMING_CHUNK: Giriş Ekranı
if not st.session_state.giris_yapildi:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    
    # Görseli base64 üzerinden güvenli yükleme
    if img_base64:
        st.markdown(f'<img src="data:image/jpeg;base64,{img_base64}" class="logo-img">', unsafe_allow_html=True)
    else:
        st.subheader("🏢 Markanow")

    tab1, tab2 = st.tabs(["Giriş Yap", "Yeni Kullanıcı Kayıt"])
    
    with tab1:
        k_adi = st.text_input("Kullanıcı Adı")
        sifre = st.text_input("Şifre", type="password")
        if st.button("Giriş Yap", use_container_width=True):
            if k_adi == "admin" and sifre == "1234":
                st.session_state.giris_yapildi = True
                st.rerun()
            else: st.error("Hatalı giriş!")

    with tab2:
        st.text_input("Yeni Kullanıcı Adı", key="n_u")
        st.text_input("Yeni Şifre", type="password", key="n_p")
        if st.button("Kayıt Talebi Gönder", use_container_width=True):
            st.success("Talebiniz yöneticiye iletildi.")
            
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()
