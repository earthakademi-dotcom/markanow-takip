import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Markanow ERP & Satış Takip", layout="wide")

KULLANICILAR = {
    "Ali Osman Yelbey": {"sifre": "MarkanowAdmin2026!", "rol": "Admin"},
    "Buğra Büyükeren": {"sifre": "BugraVekil456!", "rol": "Admin"},
    "MERVE YURTLU": {"sifre": "MerveDanisman789!", "rol": "Marka Danışmanı"},
    "Ahmet Yılmaz": {"sifre": "AhmetDanisman321!", "rol": "Marka Danışmanı"},
    "Muhasebe Kullanıcısı": {"sifre": "Muhasebe987!", "rol": "Muhasebe"},
    "Operasyon Yetkilisi": {"sifre": "Operasyon123!", "rol": "Operasyon"}
}

if "giris_yapildi" not in st.session_state:
    st.session_state.giris_yapildi = False
if "markalar" not in st.session_state:
    st.session_state.markalar = pd.DataFrame(columns=[
        "Marka Adı", "Ad Soyad", "Telefon", "TC Kimlik", "Sınıf Kodu", "Personel", 
        "Satış Tarihi", "Ödeme Seçeneği", "Başvuru Ücreti", "B. Onay", "Fatura No",
        "Başvuru No", "Başvuru Tarihi"
    ])

tum_siniflar = [str(i) for i in range(1, 46)] + [f"35/{i}" for i in range(1, 35)]

def hesapla_satis_adeti(secili_siniflar):
    liste = [s.strip() for s in secili_siniflar.split(", ") if s.strip()]
    return sum(1 for s in liste if "/" not in s)

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

# --- DANIŞMAN RAPORLARI ---
if st.session_state.kullanici_rolu in ["Marka Danışmanı", "Admin"]:
    st.subheader(f"📊 {st.session_state.kullanici_adi} - Performans Raporu")
    aylar = sorted(list(set([d[3:] for d in st.session_state.markalar["Satış Tarihi"] if d != "-"])), reverse=True)
    secili_ay = st.selectbox("Raporlanacak Ayı Seçin:", aylar if aylar else [datetime.now().strftime("%m.%Y")])
    onayli_kisisel = st.session_state.markalar[
        (st.session_state.markalar["Personel"] == st.session_state.kullanici_adi) & 
        (st.session_state.markalar["B. Onay"] == "Onaylandı") &
        (st.session_state.markalar["Satış Tarihi"].str.endswith(secili_ay))
    ]
    c1, c2 = st.columns(2)
    c1.metric(f"{secili_ay} Satış Adedim", sum(onayli_kisisel["Sınıf Kodu"].apply(hesapla_satis_adeti)))
    c2.metric(f"{secili_ay} Cirom (TL)", f"{onayli_kisisel['Başvuru Ücreti'].sum():,.0f} TL")

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
            yeni = pd.DataFrame([{"Marka Adı": m_adi, "Ad Soyad": ad_soyad, "Telefon": tel, "TC Kimlik": tc, "Sınıf Kodu": ", ".join(s_kodu), "Personel": st.session_state.kullanici_adi, "Satış Tarihi": s_tarihi, "Ödeme Seçeneği": odeme, "Başvuru Ücreti": fiyat, "B. Onay": "Bekliyor", "Fatura No": "-", "Başvuru No": "-", "Başvuru Tarihi": "-"}])
            st.session_state.markalar = pd.concat([st.session_state.markalar, yeni], ignore_index=True)
            st.success("Kaydedildi!")

# --- MUHASEBE PANELİ ---
if st.session_state.kullanici_rolu in ["Muhasebe", "Admin"]:
    st.subheader("💰 Muhasebe Paneli")
    bekleyen = st.session_state.markalar[st.session_state.markalar["B. Onay"] == "Bekliyor"]
    if not bekleyen.empty:
        marka_sec = st.selectbox("Onaylanacak Marka Seçin", bekleyen["Marka Adı"].unique())
        idx = st.session_state.markalar[st.session_state.markalar["Marka Adı"] == marka_sec].index[0]
        with st.form("muhasebe_form"):
            fatura = st.text_input("Fatura Numarası")
            if st.form_submit_button("Onayla"):
                st.session_state.markalar.at[idx, "B. Onay"] = "Onaylandı"
                st.session_state.markalar.at[idx, "Fatura No"] = fatura
                st.rerun()

# --- OPERASYON PANELİ ---
if st.session_state.kullanici_rolu in ["Operasyon", "Admin"]:
    st.subheader("⚙️ Operasyon Paneli")
    onayli = st.session_state.markalar[st.session_state.markalar["B. Onay"] == "Onaylandı"]
    if not onayli.empty:
        marka_sec = st.selectbox("Başvuru Girişi Yapılacak Marka", onayli["Marka Adı"].unique())
        idx = st.session_state.markalar[st.session_state.markalar["Marka Adı"] == marka_sec].index[0]
        st.info(f"Marka Bilgileri: {st.session_state.markalar.at[idx, 'Marka Adı']} | Sınıf: {st.session_state.markalar.at[idx, 'Sınıf Kodu']}")
        with st.form("operasyon_form"):
            b_no = st.text_input("Başvuru Numarası")
            b_tarih = st.date_input("Başvuru Tarihi").strftime("%d.%m.%Y")
            if st.form_submit_button("Başvuruyu Kaydet"):
                st.session_state.markalar.at[idx, "Başvuru No"] = b_no
                st.session_state.markalar.at[idx, "Başvuru Tarihi"] = b_tarih
                st.success("Operasyon bilgileri güncellendi!")
    st.dataframe(onayli)
