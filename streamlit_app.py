import streamlit as st
import pandas as pd
from datetime import datetime

# STREAMING_CHUNK:Initializing configuration and session state
st.set_page_config(page_title="Markanow ERP & Satış Takip", layout="wide")

KULLANICILAR = {
    "Ali Osman Yelbey": {"sifre": "MarkanowAdmin2026!", "rol": "Admin"},
    "Buğra Büyükeren": {"sifre": "BugraVekil456!", "rol": "Admin"},
    "MERVE YURTLU": {"sifre": "MerveDanisman789!", "rol": "Marka Danışmanı"},
    "Ahmet Yılmaz": {"sifre": "AhmetDanisman321!", "rol": "Marka Danışmanı"},
    "Muhasebe Kullanıcısı": {"sifre": "Muhasebe987!", "rol": "Muhasebe"}
}

if "giris_yapildi" not in st.session_state:
    st.session_state.giris_yapildi = False
if "markalar" not in st.session_state:
    st.session_state.markalar = pd.DataFrame(columns=[
        "Marka Adı", "Ad Soyad", "Telefon", "TC Kimlik", "Sınıf Kodu", "Personel", "Satış Tarihi", 
        "Ödeme Seçeneği", "Başvuru Ücreti", "B. Onay", "Savunma Ücreti", "S. Onay", 
        "Tescil Ücreti", "T. Onay", "Başvuru No", "Başvuru Tarihi", "Bülten Tarihi", 
        "İlan Bitiş Tarihi", "İtiraz Tebliğ T.", "Savunma Son Gün", "Kurul Kararı", "Yenileme T."
    ])

# STREAMING_CHUNK:Defining class options
ana_siniflar = [str(i) for i in range(1, 46)]
alt_siniflar = [f"35/{i}" for i in range(1, 35)]
tum_siniflar = ana_siniflar + alt_siniflar

# STREAMING_CHUNK:Handling login logic
if not st.session_state.giris_yapildi:
    st.title("🔒 Markanow Takip Sistemi")
    kullanici = st.selectbox("Kullanıcı Adı", list(KULLANICILAR.keys()))
    sifre = st.text_input("Şifre", type="password")
    if st.button("Giriş Yap"):
        if sifre == KULLANICILAR[kullanici]["sifre"]:
            st.session_state.giris_yapildi = True
            st.session_state.kullanici_adi = kullanici
            st.session_state.kullanici_rolu = KULLANICILAR[kullanici]["rol"]
            st.rerun()
    st.stop()

# STREAMING_CHUNK:Rendering main application structure
st.sidebar.title(f"👤 {st.session_state.kullanici_adi}")
st.sidebar.info(f"Rolünüz: {st.session_state.kullanici_rolu}")
if st.sidebar.button("Güvenli Çıkış Yap"):
    st.session_state.giris_yapildi = False
    st.rerun()

# STREAMING_CHUNK:Rendering sale entry form
if st.session_state.kullanici_rolu in ["Marka Danışmanı", "Admin"]:
    st.subheader("📝 Yeni Satış Girişi")
    with st.form("yeni_satis", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            m_adi = st.text_input("Marka Adı")
            ad_soyad = st.text_input("Müşteri Ad Soyad")
            tel_no = st.text_input("Telefon Numarası")
            tc_no = st.text_input("TC Kimlik No")
        with c2:
            s_tarihi = st.date_input("Satış Tarihi").strftime("%d.%m.%Y")
            s_kodu = st.multiselect("Sınıf Kodu", tum_siniflar)
            fiyat = st.number_input("Başvuru Ücreti (TL)", value=0)
            odeme = st.selectbox("Ödeme", ["EFT / Havale", "Kredi Kartı"])
        
        if st.form_submit_button("Kaydet"):
            yeni = pd.DataFrame([{
                "Marka Adı": m_adi, "Ad Soyad": ad_soyad, "Telefon": tel_no, "TC Kimlik": tc_no,
                "Sınıf Kodu": ", ".join(s_kodu), "Personel": st.session_state.kullanici_adi, 
                "Satış Tarihi": s_tarihi, "Başvuru Ücreti": fiyat, 
                "Ödeme Seçeneği": odeme, "B. Onay": "Bekliyor"
            }])
            st.session_state.markalar = pd.concat([st.session_state.markalar, yeni], ignore_index=True)
            st.success("Kaydedildi!")

# STREAMING_CHUNK:Rendering data table
if not st.session_state.markalar.empty:
    st.dataframe(st.session_state.markalar)
```eof

### 🛠️ Güncelleme Hatırlatması
1. GitHub'da `streamlit_app.py` dosyanıza girin.
2. Mevcut içeriği **tamamen silin** (Ctrl+A -> Delete).
3. Yukarıdaki kodu yapıştırın ve **Commit changes** diyerek kaydedin.

Artık Danışman arkadaşlarınız müşteri telefon bilgilerini de sisteme işleyebilirler! Başka bir isteğiniz olursa lütfen belirtin.
