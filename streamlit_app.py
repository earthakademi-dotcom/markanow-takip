import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta

# STREAMING_CHUNK: Tanımlamalar
DATA_FILE = "marka_takip.csv"
KULLANICILAR = {
    "Ali Osman Yelbey": {"rol": "Admin"},
    "MERVE YURTLU": {"rol": "Satış Danışmanı"},
    "Muhasebe Kullanıcısı": {"rol": "Muhasebe"},
    "Operasyon Yetkilisi": {"rol": "Operasyon"}
}

def load_data():
    cols = ["ID", "Marka Adı", "Ad Soyad", "TC", "Telefon", "Doğum Tarihi", "İl", "Sınıf", "Ödeme", "Tutar", 
            "Durum", "Fatura No", "Fatura Tarihi", "Başvuru No", "Başvuru Tarihi", "Bülten Tarihi", "Tescil Tebliğ T.", "Ödeme Tarihi"]
    if os.path.exists(DATA_FILE): return pd.read_csv(DATA_FILE)
    return pd.DataFrame(columns=cols)

st.set_page_config(page_title="Markanow ERP", layout="wide")

# STREAMING_CHUNK: Giriş Kontrolü
if "kullanici" not in st.session_state: st.session_state.kullanici = None

if not st.session_state.kullanici:
    k = st.selectbox("Kullanıcı Seçiniz", list(KULLANICILAR.keys()))
    if st.button("Giriş Yap"):
        st.session_state.kullanici = k
        st.session_state.rol = KULLANICILAR[k]["rol"]
        st.rerun()
    st.stop()

# STREAMING_CHUNK: Sidebar Menü
with st.sidebar:
    st.write(f"👤 {st.session_state.kullanici}")
    st.write(f"🛡️ {st.session_state.rol}")
    menu = st.radio("Menü", ["📝 Satış Girişi", "💰 Muhasebe Onayı", "⚙️ Operasyon Süreci", "📊 Danışman Raporu"])
    if st.button("Çıkış"): st.session_state.kullanici = None; st.rerun()

df = load_data()

# STREAMING_CHUNK: Satış Girişi İşlemleri
if menu == "📝 Satış Girişi":
    st.header("📝 Yeni Satış Girişi")
    with st.form("yeni_satis"):
        m_adi = st.text_input("Marka Adı")
        tc = st.text_input("TC Kimlik (11 Hane)")
        tel = st.text_input("Telefon (05xxxxxxxxx)")
        odeme = st.selectbox("Ödeme Şekli", ["Kredi Kartı", "EFT"])
        tutar = st.number_input("Tutar (TL)")
        if st.form_submit_button("Satışı Kaydet"):
            if len(tc) == 11 and tel.startswith("05"):
                new_row = {"ID": len(df)+1, "Marka Adı": m_adi, "TC": tc, "Telefon": tel, "Tutar": tutar, "Ödeme": odeme, "Durum": "Muhasebe Onayı Bekliyor"}
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                df.to_csv(DATA_FILE, index=False)
                st.success("Satış başarıyla muhasebeye iletildi.")
            else:
                st.error("Lütfen verileri kurallara uygun giriniz (TC 11 hane, Tel 05 ile başlamalı).")

# STREAMING_CHUNK: Muhasebe ve Operasyon Panelleri
elif menu == "💰 Muhasebe Onayı":
    st.header("Muhasebe Onayı")
    st.dataframe(df[df['Durum'] == 'Muhasebe Onayı Bekliyor'])
    id_onay = st.number_input("Onaylanacak Satış ID", step=1)
    fatura_no = st.text_input("Fatura Numarası")
    if st.button("Onayı Tamamla"):
        df.loc[df['ID'] == id_onay, ['Durum', 'Fatura No']] = ['Operasyon Bekliyor', fatura_no]
        df.to_csv(DATA_FILE, index=False)
        st.rerun()

elif menu == "⚙️ Operasyon Süreci":
    st.header("Operasyonel Takip")
    st.dataframe(df)

elif menu == "📊 Danışman Raporu":
    st.header("Danışman Raporu")
    st.metric("Toplam Ciro", df[df['Durum'] != 'Muhasebe Onayı Bekliyor']['Tutar'].sum())
