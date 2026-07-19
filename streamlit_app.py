import streamlit as st
import pandas as pd
import os
import re

# STREAMING_CHUNK: Kullanıcı Tanımları ve Yapılandırma
KULLANICILAR = {
    "Ali Osman Yelbey": {"sifre": "MarkanowAdmin2026!", "rol": "Admin"},
    "MERVE YURTLU": {"sifre": "MerveDanisman789!", "rol": "Danışman"},
    "Muhasebe Kullanıcısı": {"sifre": "Muhasebe987!", "rol": "Muhasebe"},
    "Operasyon Yetkilisi": {"sifre": "Op123456!", "rol": "Operasyon"}
}

ILLER = ["Adana", "Ankara", "İstanbul", "İzmir", "Bursa", "Antalya", "Konya", "Diğer"]
DATA_FILE = "marka_satislar.csv"
tum_sinif_secenekleri = [str(i) for i in range(1, 46)] + [f"35/{i}" for i in range(1, 35)]

def load_data():
    cols = ["ID", "Marka Adı", "Ad Soyad", "TC Kimlik", "Telefon", "Doğum Tarihi", "İl", "Sınıf", "Satış Tarihi", "Tutar", "Durum", "Danışman"]
    if os.path.exists(DATA_FILE): return pd.read_csv(DATA_FILE)
    return pd.DataFrame(columns=cols)

# STREAMING_CHUNK: CSS ile Kırmızı Çerçeve Desteği
st.markdown("""
    <style>
    .stTextInput > div > div > input:invalid { border: 2px solid red; }
    </style>
""", unsafe_allow_html=True)

# STREAMING_CHUNK: Giriş Paneli
if "giris_yapildi" not in st.session_state: st.session_state.giris_yapildi = False

if not st.session_state.giris_yapildi:
    st.markdown('<div class="login-card" style="max-width:400px; margin:auto; padding:40px; border-radius:20px; box-shadow:0 4px 15px rgba(0,0,0,0.1); background:white; text-align:center;">', unsafe_allow_html=True)
    st.markdown('<img src="https://i.imgur.com/zZJ3TZW.jpeg" style="width:250px; margin-bottom:20px;">', unsafe_allow_html=True)
    k_adi = st.selectbox("Kullanıcı Adı", list(KULLANICILAR.keys()))
    sifre = st.text_input("Şifre", type="password")
    if st.button("Giriş Yap", use_container_width=True):
        if KULLANICILAR[k_adi]["sifre"] == sifre:
            st.session_state.giris_yapildi = True
            st.session_state.kullanici = k_adi
            st.session_state.rol = KULLANICILAR[k_adi]["rol"]
            st.rerun()
    st.stop()

# STREAMING_CHUNK: Ana Yönetim ve Hata Mekanizması
with st.sidebar:
    st.title(f"👤 {st.session_state.kullanici}")
    st.info(f"Görev: {st.session_state.rol}")
    if st.button("🚪 Güvenli Çıkış"):
        st.session_state.giris_yapildi = False
        st.rerun()

df = load_data()
st.title("🏢 Markanow Satış Yönetim Paneli")

tab1, tab2, tab3 = st.tabs(["📝 Satış Girişi", "⚙️ Operasyon Onay", "📊 Finansal Raporlar"])

with tab1:
    with st.form("yeni_satis", clear_on_submit=False):
        c1, c2 = st.columns(2)
        m_adi = c1.text_input("Marka Adı*", help="Zorunlu alan")
        ad_soyad = c1.text_input("Müşteri Ad Soyad*")
        tc = c1.text_input("TC Kimlik No (11 Hane)*")
        tel = c1.text_input("Telefon (05xxxxxxxxx)*")
        dogum = c2.date_input("Doğum Tarihi (GG.AA.YYYY)")
        il = c2.selectbox("İl Seçin*", ILLER)
        sinif = c2.multiselect("Sınıf Seçimi*", tum_sinif_secenekleri)
        satis_tarihi = c2.date_input("Satış Tarihi (GG.AA.YYYY)")
        tutar = st.number_input("Tutar (TL)*", min_value=0.0, format="%.2f")
        
        submitted = st.form_submit_button("Satışı Kaydet")
        
        if submitted:
            errors = []
            if not m_adi: errors.append("Marka Adı")
            if not ad_soyad: errors.append("Müşteri Ad Soyad")
            if len(tc) != 11 or not tc.isdigit(): errors.append("TC Kimlik (11 hane olmalı)")
            if not re.match(r"^05\d{9}$", tel): errors.append("Telefon (05 ile başlamalı ve 11 hane olmalı)")
            
            if errors:
                st.error(f"⚠️ Hata: Lütfen şu alanları düzeltin: {', '.join(errors)}")
            else:
                new_row = {"ID": len(df)+1, "Marka Adı": m_adi, "Ad Soyad": ad_soyad, "TC Kimlik": tc, "Telefon": tel, 
                           "Doğum Tarihi": dogum.strftime("%d.%m.%Y"), "İl": il, "Sınıf": ", ".join(sinif), 
                           "Satış Tarihi": satis_tarihi.strftime("%d.%m.%Y"), "Tutar": tutar, "Durum": "Bekliyor", "Danışman": st.session_state.kullanici}
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                df.to_csv(DATA_FILE, index=False)
                st.success("Satış başarıyla kaydedildi!")
                st.rerun()
