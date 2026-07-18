import streamlit as st
import pandas as pd

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
        "Marka Adı", "Ad Soyad", "Telefon", "TC Kimlik", "Sınıf Kodu", "Personel", 
        "Satış Tarihi", "Ödeme Seçeneği", "Başvuru Ücreti", "B. Onay", "Fatura No"
    ])

tum_siniflar = [str(i) for i in range(1, 46)] + [f"35/{i}" for i in range(1, 35)]

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

st.sidebar.title(f"👤 {st.session_state.kullanici_adi}")
if st.sidebar.button("Güvenli Çıkış Yap"):
    st.session_state.giris_yapildi = False
    st.rerun()

if st.session_state.kullanici_rolu in ["Marka Danışmanı", "Admin"]:
    st.subheader("📝 Yeni Satış Girişi")
    with st.form("yeni_satis", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            m_adi = st.text_input("Marka Adı")
            ad_soyad = st.text_input("Müşteri Ad Soyad")
            tel = st.text_input("Telefon Numarası")
            tc = st.text_input("TC Kimlik No")
        with c2:
            s_tarihi = st.date_input("Satış Tarihi").strftime("%d.%m.%Y")
            s_kodu = st.multiselect("Sınıf Kodu", tum_siniflar)
            fiyat = st.number_input("Başvuru Ücreti (TL)", value=0)
            odeme = st.selectbox("Ödeme", ["EFT / Havale", "Kredi Kartı"])
        if st.form_submit_button("Kaydet"):
            yeni = pd.DataFrame([{"Marka Adı": m_adi, "Ad Soyad": ad_soyad, "Telefon": tel, "TC Kimlik": tc, "Sınıf Kodu": ", ".join(s_kodu), "Personel": st.session_state.kullanici_adi, "Satış Tarihi": s_tarihi, "Ödeme Seçeneği": odeme, "Başvuru Ücreti": fiyat, "B. Onay": "Bekliyor", "Fatura No": "-"}])
            st.session_state.markalar = pd.concat([st.session_state.markalar, yeni], ignore_index=True)
            st.success("Kaydedildi!")

if st.session_state.kullanici_rolu == "Muhasebe":
    st.subheader("💰 Muhasebe Onay Paneli")
    if not st.session_state.markalar.empty:
        marka_sec = st.selectbox("Marka Seçin", st.session_state.markalar["Marka Adı"].unique())
        idx = st.session_state.markalar[st.session_state.markalar["Marka Adı"] == marka_sec].index[0]
        with st.form("muhasebe_onay"):
            onay = st.selectbox("Ödeme Durumu", ["Bekliyor", "Onaylandı"])
            fatura = st.text_input("Fatura Numarası", value=st.session_state.markalar.at[idx, "Fatura No"])
            if st.form_submit_button("Güncelle"):
                st.session_state.markalar.at[idx, "B. Onay"] = onay
                st.session_state.markalar.at[idx, "Fatura No"] = fatura
                st.success("Muhasebe bilgileri güncellendi!")

st.dataframe(st.session_state.markalar)
