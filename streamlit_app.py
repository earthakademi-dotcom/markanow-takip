import streamlit as st

# STREAMING_CHUNK: Kullanıcı Listesi ve Yapılandırma
KULLANICILAR = {
    "Ali Osman Yelbey": "MarkanowAdmin2026!",
    "Buğra Büyükeren": "BugraVekil456!",
    "MERVE YURTLU": "MerveDanisman789!",
    "Ahmet Yılmaz": "AhmetDanisman321!",
    "Muhasebe Kullanıcısı": "Muhasebe987!"
}

st.set_page_config(page_title="Markanow Giriş", layout="centered")

if "giris_yapildi" not in st.session_state: st.session_state.giris_yapildi = False

# STREAMING_CHUNK: Minimalist Giriş Ekranı
if not st.session_state.giris_yapildi:
    st.title("Markanow Satış Yönetim Paneli")
    st.markdown("---")
    
    # Kullanıcıyı listeden seçtiriyoruz
    secili_kullanici = st.selectbox("Kullanıcı Adı", list(KULLANICILAR.keys()))
    sifre = st.text_input("Şifre", type="password")
    
    if st.button("Giriş Yap", use_container_width=True):
        if KULLANICILAR.get(secili_kullanici) == sifre:
            st.session_state.giris_yapildi = True
            st.session_state.kullanici_adi = secili_kullanici
            st.rerun()
        else:
            st.error("Şifre hatalı!")
    
    st.stop()

# STREAMING_CHUNK: Giriş Sonrası Arayüz
st.header(f"Hoş geldiniz, {st.session_state.get('kullanici_adi', '')}")
if st.button("Çıkış"):
    st.session_state.giris_yapildi = False
    st.rerun()
