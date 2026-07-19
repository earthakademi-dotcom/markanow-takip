import streamlit as st
import pandas as pd
import os

# STREAMING_CHUNK: Yapılandırma ve CSS
KULLANICILAR = {
    "Ali Osman Yelbey": {"sifre": "MarkanowAdmin2026!", "rol": "Admin"},
    "MERVE YURTLU": {"sifre": "MerveDanisman789!", "rol": "Danışman"},
    "Muhasebe Kullanıcısı": {"sifre": "Muhasebe987!", "rol": "Muhasebe"},
    "Operasyon Yetkilisi": {"sifre": "Op123456!", "rol": "Operasyon"}
}
ILLER = ["Adana", "Ankara", "İstanbul", "İzmir", "Bursa", "Antalya", "Konya", "Diğer"]
DATA_FILE = "marka_satislar.csv"
tum_sinif_secenekleri = [str(i) for i in range(1, 46)] + [f"35/{i}" for i in range(1, 35)]

# Hatalı kutucukları kırmızı yapan CSS
st.markdown("""
    <style>
    .error-input { border: 2px solid red !important; }
    </style>
""", unsafe_allow_html=True)

def load_data():
    if os.path.exists(DATA_FILE): return pd.read_csv(DATA_FILE)
    return pd.DataFrame(columns=["ID", "Marka Adı", "TC Kimlik", "Telefon", "Tutar", "Durum", "Danışman"])

# STREAMING_CHUNK: Giriş Kontrolü
if "giris_yapildi" not in st.session_state: st.session_state.giris_yapildi = False

if not st.session_state.giris_yapildi:
    k_adi = st.selectbox("Kullanıcı Adı", list(KULLANICILAR.keys()))
    sifre = st.text_input("Şifre", type="password")
    if st.button("Giriş Yap"):
        if KULLANICILAR[k_adi]["sifre"] == sifre:
            st.session_state.giris_yapildi = True
            st.session_state.kullanici = k_adi
            st.session_state.rol = KULLANICILAR[k_adi]["rol"]
            st.rerun()
    st.stop()

# STREAMING_CHUNK: Satış Giriş Formu ve Anlık Hata Kontrolü
st.title("🏢 Markanow Satış Yönetim Paneli")
df = load_data()
tab1, tab2, tab3 = st.tabs(["📝 Satış Girişi", "⚙️ Operasyon Onay", "📊 Finansal Raporlar"])

with tab1:
    m_adi = st.text_input("Marka Adı*")
    tc = st.text_input("TC Kimlik No (11 Hane)*")
    
    # TC Hata Kontrolü
    tc_hata = False
    if tc and (len(tc) != 11 or not tc.isdigit()):
        st.error("⚠️ TC Kimlik No 11 haneli sayı olmalıdır!")
        tc_hata = True
        
    tel = st.text_input("Telefon (05xxxxxxxxx)*")
    tel_hata = False
    if tel and (not tel.startswith("05") or len(tel) != 11 or not tel.isdigit()):
        st.error("⚠️ Telefon 05 ile başlamalı ve 11 hane olmalıdır!")
        tel_hata = True

    tutar = st.number_input("Tutar (TL)*", min_value=0.0)
    
    if st.button("Satışı Kaydet"):
        if tc_hata or tel_hata or not m_adi:
            st.error("Lütfen hatalı alanları düzeltin!")
        else:
            st.success("Satış kaydedildi.")
