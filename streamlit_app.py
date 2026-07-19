import streamlit as st
import pandas as pd

# STREAMING_CHUNK: Kullanıcı Tanımları
KULLANICILAR = {
    "Ali Osman Yelbey": "MarkanowAdmin2026!",
    "Buğra Büyükeren": "BugraVekil456!",
    "MERVE YURTLU": "MerveDanisman789!",
    "Ahmet Yılmaz": "AhmetDanisman321!",
    "Muhasebe Kullanıcısı": "Muhasebe987!"
}

# STREAMING_CHUNK: Sayfa Yapılandırması
st.set_page_config(page_title="Markanow ERP", layout="wide")

# STREAMING_CHUNK: Genel Stil Ayarları
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    .login-card {
        background-color: white; padding: 40px; border-radius: 20px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1); text-align: center;
        max-width: 500px; margin: auto;
    }
    </style>
""", unsafe_allow_html=True)

# STREAMING_CHUNK: Oturum ve Veri Başlatma
if "giris_yapildi" not in st.session_state: st.session_state.giris_yapildi = False
if "markalar" not in st.session_state:
    st.session_state.markalar = pd.DataFrame(columns=["Marka Adı", "Müşteri", "Tarih", "Tutar"])

# STREAMING_CHUNK: Giriş Ekranı (Logo ile)
if not st.session_state.giris_yapildi:
    st.markdown('<div class="login-card">', unsafe_allow_html=True)
    st.markdown('<img src="https://i.imgur.com/zZJ3TZW.jpeg" style="width:250px; margin-bottom:20px;">', unsafe_allow_html=True)
    
    secili_kullanici = st.selectbox("Kullanıcı Adı", list(KULLANICILAR.keys()))
    sifre = st.text_input("Şifre", type="password")
    
    if st.button("Giriş Yap", use_container_width=True):
        if KULLANICILAR.get(secili_kullanici) == sifre:
            st.session_state.giris_yapildi = True
            st.session_state.kullanici_adi = secili_kullanici
            st.rerun()
        else: st.error("Hatalı giriş!")
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# STREAMING_CHUNK: Ana Panel (Giriş Sonrası)
st.sidebar.title(f"👤 {st.session_state.kullanici_adi}")
if st.sidebar.button("🚪 Çıkış"):
    st.session_state.giris_yapildi = False
    st.rerun()

st.title("📊 Markanow Satış Yönetim Paneli")

with st.expander("📝 Yeni Satış Girişi"):
    with st.form("yeni_satis", clear_on_submit=True):
        col1, col2 = st.columns(2)
        m_adi = col1.text_input("Marka Adı")
        m_musteri = col1.text_input("Müşteri Adı")
        tarih = col2.date_input("Satış Tarihi")
        tutar = col2.number_input("Tutar (TL)")
        
        if st.form_submit_button("Kaydet"):
            yeni = pd.DataFrame([[m_adi, m_musteri, tarih, tutar]], columns=["Marka Adı", "Müşteri", "Tarih", "Tutar"])
            st.session_state.markalar = pd.concat([st.session_state.markalar, yeni], ignore_index=True)
            st.success("Satış başarıyla kaydedildi.")

st.dataframe(st.session_state.markalar, use_container_width=True)
