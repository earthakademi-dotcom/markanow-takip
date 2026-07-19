import streamlit as st

# STREAMING_CHUNK: Sayfa Yapılandırması
st.set_page_config(page_title="Markanow ERP", layout="centered")

# STREAMING_CHUNK: Stil Ayarları
st.markdown("""
    <style>
    .stApp { background-color: #f4f7f9; }
    .main-box {
        background-color: white;
        padding: 40px;
        border-radius: 15px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.08);
        text-align: center;
        margin-top: 50px;
    }
    </style>
""", unsafe_allow_html=True)

# STREAMING_CHUNK: Oturum Durumu
if "giris_yapildi" not in st.session_state: st.session_state.giris_yapildi = False

# STREAMING_CHUNK: Giriş Ekranı
if not st.session_state.giris_yapildi:
    st.markdown('<div class="main-box">', unsafe_allow_html=True)
    
    # Yeni logonun entegrasyonu
    try:
        st.image("WhatsApp Image 2026-04-04 at 11.52.05 (1).jpeg", width=280)
    except:
        st.title("Markanow Patent")
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["Giriş Yap", "Kayıt Ol"])
    
    with tab1:
        kullanici = st.text_input("Kullanıcı Adı")
        sifre = st.text_input("Şifre", type="password")
        if st.button("Giriş Yap", use_container_width=True):
            # Basit Yetkilendirme
            if kullanici == "admin" and sifre == "1234":
                st.session_state.giris_yapildi = True
                st.rerun()
            else:
                st.error("Kullanıcı adı veya şifre hatalı!")
                
    with tab2:
        st.text_input("Yeni Kullanıcı Adı", key="reg_u")
        st.text_input("Yeni Şifre", type="password", key="reg_p")
        if st.button("Kaydı İlet", use_container_width=True):
            st.success("Kayıt talebiniz yöneticiye iletildi.")
            
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# STREAMING_CHUNK: Giriş Sonrası Arayüz
st.title("Markanow Yönetim Paneli")
if st.button("Güvenli Çıkış"):
    st.session_state.giris_yapildi = False
    st.rerun()
