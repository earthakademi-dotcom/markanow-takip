import streamlit as st
import pandas as pd
from datetime import datetime
import os

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
    st.session_state.kullanici_adi = ""
    st.session_state.kullanici_rolu = ""

if "markalar" not in st.session_state:
    st.session_state.markalar = pd.DataFrame(columns=[
        "Marka Adı", "Ad Soyad", "TC Kimlik", "Sınıf Kodu", "Personel", "Satış Tarihi", 
        "Ödeme Seçeneği", "Başvuru Ücreti", "B. Onay", "Savunma Ücreti", "S. Onay", 
        "Tescil Ücreti", "T. Onay", "Başvuru No", "Başvuru Tarihi", "Bülten Tarihi", 
        "İlan Bitiş Tarihi", "İtiraz Tebliğ T.", "Savunma Son Gün", "Kurul Kararı", "Yenileme T."
    ])

def add_months(date_str, months):
    try:
        dt = datetime.strptime(date_str, "%d.%m.%Y")
        month = dt.month - 1 + months
        year = dt.year + month // 12
        month = month % 12 + 1
        return datetime(year, month, min(dt.day, 28)).strftime("%d.%m.%Y")
    except: return "-"

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

if st.session_state.kullanici_rolu in ["Marka Danışmanı", "Admin"]:
    st.subheader("📝 Yeni Satış Girişi")
    with st.form("yeni_satis"):
        c1, c2 = st.columns(2)
        with c1:
            m_adi = st.text_input("Marka Adı")
            ad_soyad = st.text_input("Müşteri Ad Soyad")
            tc_no = st.text_input("TC Kimlik No")
        with c2:
            s_tarihi = st.date_input("Satış Tarihi").strftime("%d.%m.%Y")
            s_kodu = st.multiselect("Sınıf Kodu", [str(i) for i in range(1, 46)])
            fiyat = st.number_input("Başvuru Ücreti (TL)", value=0)
            odeme = st.selectbox("Ödeme", ["EFT / Havale", "Kredi Kartı"])
        
        if st.form_submit_button("Kaydet"):
            yeni = pd.DataFrame([{
                "Marka Adı": m_adi, "Ad Soyad": ad_soyad, "TC Kimlik": tc_no,
                "Sınıf Kodu": ", ".join(s_kodu), "Personel": st.session_state.kullanici_adi, 
                "Satış Tarihi": s_tarihi, "Başvuru Ücreti": fiyat, 
                "Ödeme Seçeneği": odeme, "B. Onay": "Bekliyor"
            }])
            st.session_state.markalar = pd.concat([st.session_state.markalar, yeni], ignore_index=True)
            st.success("Kaydedildi!")

if not st.session_state.markalar.empty:
    st.dataframe(st.session_state.markalar)
    
    if st.session_state.kullanici_rolu in ["Admin"]:
        st.subheader("⚙️ Süreç Yönetimi")
        secilen_marka = st.selectbox("Güncellenecek Markayı Seçin", st.session_state.markalar["Marka Adı"].unique())
        idx = st.session_state.markalar[st.session_state.markalar["Marka Adı"] == secilen_marka].index[0]
        
        with st.form("guncelleme"):
            b_no = st.text_input("Başvuru No", str(st.session_state.markalar.at[idx, "Başvuru No"]))
            b_tarih = st.text_input("Başvuru Tarihi (GG.AA.YYYY)", str(st.session_state.markalar.at[idx, "Başvuru Tarihi"]))
            bulten_t = st.text_input("Bülten Tarihi (GG.AA.YYYY)", str(st.session_state.markalar.at[idx, "Bülten Tarihi"]))
            
            if st.form_submit_button("Verileri Güncelle"):
                st.session_state.markalar.at[idx, "Başvuru No"] = b_no
                st.session_state.markalar.at[idx, "Başvuru Tarihi"] = b_tarih
                st.session_state.markalar.at[idx, "Bülten Tarihi"] = bulten_t
                st.session_state.markalar.at[idx, "İlan Bitiş Tarihi"] = add_months(bulten_t, 2)
                st.session_state.markalar.at[idx, "İtiraz Tebliğ T."] = add_months(bulten_t, 2)
                st.session_state.markalar.at[idx, "Savunma Son Gün"] = add_months(add_months(bulten_t, 2), 1)
                st.rerun()
