import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os

# --- STREAMING_CHUNK: Configuration and Auth Initialization ---
KULLANICILAR = {
    "Ali Osman Yelbey": {"sifre": "MarkanowAdmin2026!", "rol": "Admin"},
    "Buğra Büyükeren": {"sifre": "BugraVekil456!", "rol": "Admin"},
    "MERVE YURTLU": {"sifre": "MerveDanisman789!", "rol": "Marka Danışmanı"},
    "Ahmet Yılmaz": {"sifre": "AhmetDanisman321!", "rol": "Marka Danışmanı"},
    "Muhasebe Kullanıcısı": {"sifre": "Muhasebe987!", "rol": "Muhasebe"}
}

st.set_page_config(page_title="Markanow ERP & Satış Takip", layout="wide")

if "giris_yapildi" not in st.session_state:
    st.session_state.giris_yapildi = False
    st.session_state.kullanici_adi = ""
    st.session_state.kullanici_rolu = ""

if "markalar" not in st.session_state:
    st.session_state.markalar = pd.DataFrame(columns=[
        "Marka Adı", "Sınıf Kodu", "Personel", "Adı Soyadı", "Telefon No", "Satış Tarihi",
        "Ödeme Seçeneği", "Başvuru Ücreti", "B. Onay Durumu", "Savunma Ücreti", "S. Onay Durumu",
        "Tescil Ücreti", "T. Onay Durumu", "Toplam Onaylı Ciro", "Başvuru No",
        "Başvuru Tarihi", "Bülten Tarihi", "İlan Bitiş Tarihi", "İtiraz Tebliğ T.",
        "Savunma Son Gün", "Kurul Kararı / Durum", "Belge Son Ödeme T.", "Yenileme (Vize) T."
    ])

# --- STREAMING_CHUNK: Date Logic and UI Helpers ---
def add_months(date_str, months):
    try:
        dt = datetime.strptime(date_str, "%d.%m.%Y")
        month = dt.month - 1 + months
        year = dt.year + month // 12
        month = month % 12 + 1
        day = min(dt.day, [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month])
        return datetime(year, month, day).strftime("%d.%m.%Y")
    except:
        return "-"

def logo_goster():
    if os.path.exists("logo.png"):
        st.image("logo.png", width=260)
    else:
        st.markdown("<h2 style='color:#1e3a8a;'>markanow ERP</h2>", unsafe_allow_html=True)

# --- STREAMING_CHUNK: Auth and Role Control ---
if not st.session_state.giris_yapildi:
    st.title("🔒 Giriş Paneli")
    secilen_kullanici = st.selectbox("Kullanıcı Adı", list(KULLANICILAR.keys()))
    girilen_sifre = st.text_input("Şifre", type="password")
    if st.button("Giriş Yap"):
        if girilen_sifre == KULLANICILAR[secilen_kullanici]["sifre"]:
            st.session_state.giris_yapildi = True
            st.session_state.kullanici_adi = secilen_kullanici
            st.session_state.kullanici_rolu = KULLANICILAR[secilen_kullanici]["rol"]
            st.rerun()
    st.stop()

# --- STREAMING_CHUNK: Admin Update Panel with Auto-Date Calculation ---
if st.session_state.kullanici_rolu == "Admin":
    st.subheader("⚙️ Admin Süreç Paneli")
    marka_listesi = st.session_state.markalar["Marka Adı"].tolist()
    secilen_marka = st.selectbox("Marka Seçin", marka_listesi)
    idx = st.session_state.markalar[st.session_state.markalar["Marka Adı"] == secilen_marka].index[0]
    
    with st.form("admin_guncelleme"):
        c1, c2, c3 = st.columns(3)
        with c1:
            b_ucreti = st.number_input("Başvuru Ücreti", value=int(st.session_state.markalar.at[idx, "Başvuru Ücreti"]))
            b_onay = st.selectbox("B. Onay", ["-", "Bekliyor", "ONAYLANDI"], index=["-", "Bekliyor", "ONAYLANDI"].index(str(st.session_state.markalar.at[idx, "B. Onay Durumu"])))
            b_no = st.text_input("Başvuru No", value=str(st.session_state.markalar.at[idx, "Başvuru No"]))
            b_tarih = st.text_input("Başvuru Tarihi (GG.AA.YYYY)", value=str(st.session_state.markalar.at[idx, "Başvuru Tarihi"]))
        with c2:
            s_ucreti = st.number_input("Savunma Ücreti", value=int(st.session_state.markalar.at[idx, "Savunma Ücreti"]))
            s_onay = st.selectbox("S. Onay", ["-", "Bekliyor", "ONAYLANDI"], index=["-", "Bekliyor", "ONAYLANDI"].index(str(st.session_state.markalar.at[idx, "S. Onay Durumu"])))
            bulten_t = st.text_input("Bülten Tarihi (GG.AA.YYYY)", value=str(st.session_state.markalar.at[idx, "Bülten Tarihi"]))
        with c3:
            t_ucreti = st.number_input("Tescil Ücreti", value=int(st.session_state.markalar.at[idx, "Tescil Ücreti"]))
            t_onay = st.selectbox("T. Onay", ["-", "Bekliyor", "ONAYLANDI"], index=["-", "Bekliyor", "ONAYLANDI"].index(str(st.session_state.markalar.at[idx, "T. Onay Durumu"])))
            
        if st.form_submit_button("Güncelle ve Otomatik Hesapla"):
            # Tarihleri Otomatik Hesapla
            ilan_bitis = add_months(bulten_t, 2)
            itiraz_t = add_months(bulten_t, 2)
            savunma_son = add_months(itiraz_t, 1)
            
            st.session_state.markalar.at[idx, "Başvuru Ücreti"] = b_ucreti
            st.session_state.markalar.at[idx, "B. Onay Durumu"] = b_onay
            st.session_state.markalar.at[idx, "Başvuru No"] = b_no
            st.session_state.markalar.at[idx, "Başvuru Tarihi"] = b_tarih
            st.session_state.markalar.at[idx, "Savunma Ücreti"] = s_ucreti
            st.session_state.markalar.at[idx, "S. Onay Durumu"] = s_onay
            st.session_state.markalar.at[idx, "Tescil Ücreti"] = t_ucreti
            st.session_state.markalar.at[idx, "T. Onay Durumu"] = t_onay
            st.session_state.markalar.at[idx, "Bülten Tarihi"] = bulten_t
            st.session_state.markalar.at[idx, "İlan Bitiş Tarihi"] = ilan_bitis
            st.session_state.markalar.at[idx, "İtiraz Tebliğ T."] = itiraz_t
            st.session_state.markalar.at[idx, "Savunma Son Gün"] = savunma_son
            st.rerun()

# --- STREAMING_CHUNK: Live Report Table ---
st.subheader("📊 Rapor")
for i, row in st.session_state.markalar.iterrows():
    toplam = 0
    if row["B. Onay Durumu"] == "ONAYLANDI": toplam += int(row["Başvuru Ücreti"])
    if row["S. Onay Durumu"] == "ONAYLANDI": toplam += int(row["Savunma Ücreti"])
    if row["T. Onay Durumu"] == "ONAYLANDI": toplam += int(row["Tescil Ücreti"])
    st.session_state.markalar.at[i, "Toplam Onaylı Ciro"] = toplam

st.dataframe(st.session_state.markalar)
