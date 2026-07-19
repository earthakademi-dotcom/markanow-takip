import streamlit as st
import pandas as pd

st.set_page_config(page_title="Markanow ERP", layout="centered")

# --- TASARIM VE KURUMSAL HİS ---
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    /* Login Kartı */
    .login-box {
        background-color: white;
        padding: 40px;
        border-radius: 20px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.05);
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# --- LOGIN MANTIĞI ---
if "giris_yapildi" not in st.session_state: st.session_state.giris_yapildi = False

if not st.session_state.giris_yapildi:
    # Kartı başlat
    st.markdown('<div class="login-box">', unsafe_allow_html=True)
    
    # LOGO (Eğer resim dosyanız klasördeyse direkt ismini yazın, örn: "logo.png")
    # Eğer web'de bir adreste ise tam URL'sini kullanın.
    try:
        st.image("WhatsApp Image 2026-04-04 at 11.52.05.jpeg", width=250)
    except:
        st.subheader("🏢 MARKANOW")
        
    st.markdown("<br>", unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["Giriş Yap", "Kayıt Ol"])
    
    with tab1:
        k_adi = st.text_input("Kullanıcı Adı")
        sifre = st.text_input("Şifre", type="password")
        if st.button("Giriş Yap", use_container_width=True):
            # Basit kontrol
            if k_adi == "admin" and sifre == "1234":
                st.session_state.giris_yapildi = True
                st.rerun()
            else:
                st.error("Hatalı bilgiler!")

    with tab2:
        y_k = st.text_input("Yeni Kullanıcı Adı", key="y_k")
        y_s = st.text_input("Yeni Şifre", type="password", key="y_s")
        if st.button("Kaydı Tamamla", use_container_width=True):
            st.success("Talebiniz yöneticiye iletildi.")
            
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- GİRİŞ SONRASI ---
st.title("Markanow Paneli")
if st.button("🚪 Çıkış"):
    st.session_state.giris_yapildi = False
    st.rerun()
