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

# STREAMING_CHUNK: Arayüz Yapılandırması
st.set_page_config(page_title="Markanow ERP", layout="wide")

# STREAMING_CHUNK: Oturum ve Veri Durumu
if "giris_yapildi" not in st.session_state: st.session_state.giris_yapildi = False
if "markalar" not in st.session_state:
    st.session_state.markalar = pd.DataFrame(columns=["Marka Adı", "Müşteri", "Tarih", "Tutar"])

# STREAMING_CHUNK: Giriş Ekranı (Kurumsal)
if not st.session_state.giris_yapildi:
    st.markdown('<div style="max-width: 400px; margin: auto; padding: 40px; border-radius: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); background: white;">', unsafe_allow_html=True)
    st.markdown('<img src="https://i.imgur.com/zZJ3TZW.jpeg" style="width:100%; margin-bottom:20px;">', unsafe_allow_html=True)
    
    k_adi = st.selectbox("Kullanıcı Adı", list(KULLANICILAR.keys()))
    sifre = st.text_input("Şifre", type="password")
    if st.button("Giriş Yap", use_container_width=True):
        if KULLANICILAR.get(k_adi) == sifre:
            st.session_state.giris_yapildi = True
            st.session_state.kullanici_adi = k_adi
            st.rerun()
        else: st.error("Hatalı şifre!")
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# STREAMING_CHUNK: Ana Panel (Giriş Sonrası)
st.sidebar.title(f"👤 {st.session_state.kullanici_adi}")
if st.sidebar.button("🚪 Çıkış"):
    st.session_state.giris_yapildi = False
    st.rerun()

st.title("📈 Markanow Satış Takip")

# Satış Formu
with st.expander("📝 Yeni Satış Girişi", expanded=True):
    with st.form("yeni_satis", clear_on_submit=True):
        c1, c2 = st.columns(2)
        m_adi = c1.text_input("Marka Adı")
        m_musteri = c1.text_input("Müşteri Adı")
        tarih = c2.date_input("Satış Tarihi")
        tutar = c2.number_input("Tutar (TL)", min_value=0.0, format="%.2f")
        
        if st.form_submit_button("Satışı Kaydet"):
            yeni = pd.DataFrame([[m_adi, m_musteri, tarih, tutar]], columns=["Marka Adı", "Müşteri", "Tarih", "Tutar"])
            st.session_state.markalar = pd.concat([st.session_state.markalar, yeni], ignore_index=True)
            st.success("Satış başarıyla eklendi!")
