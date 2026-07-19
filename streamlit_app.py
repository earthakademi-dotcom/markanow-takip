import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta

# STREAMING_CHUNK: Tanımlamalar ve Veri Yükleme
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

# STREAMING_CHUNK: Giriş ve Menü Yapısı
if "kullanici" not in st.session_state: st.session_state.kullanici = None

if not st.session_state.kullanici:
    k = st.selectbox("Kullanıcı", list(KULLANICILAR.keys()))
    if st.button("Giriş"):
        st.session_state.kullanici = k
        st.session_state.rol = KULLANICILAR[k]["rol"]
        st.rerun()
    st.stop()

with st.sidebar:
    st.write(f"👤 {st.session_state.kullanici}")
    st.write(f"🛡️ {st.session_state.rol}")
    menu = st.radio("Menü", ["📝 Satış Girişi", "💰 Muhasebe Onayı", "⚙️ Operasyon Süreci", "📊 Danışman Raporu"])
    if st.button("Çıkış"): st.session_state.kullanici = None; st.rerun()

df = load_data()

# STREAMING_CHUNK: Satış Danışmanı (Sınıf Mantığı ve Giriş)
if menu == "📝 Satış Girişi":
    with st.form("yeni_satis"):
        m_adi = st.text_input("Marka Adı")
        tc = st.text_input("TC Kimlik (11 Hane)")
        tel = st.text_input("Telefon (05xxxxxxxxx)")
        odeme = st.selectbox("Ödeme", ["Kredi Kartı", "EFT"])
        tutar = st.number_input("Tutar")
        if st.form_submit_button("Kaydet"):
            new_row = {"ID": len(df)+1, "Marka Adı": m_adi, "TC": tc, "Telefon": tel, "Tutar": tutar, "Ödeme": odeme, "Durum": "Muhasebe Onayı Bekliyor"}
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            df.to_csv(DATA_FILE, index=False)
            st.success("Muhasebeye gönderildi.")

# STREAMING_CHUNK: Muhasebe ve Operasyon İş Akışı
elif menu == "💰 Muhasebe Onayı":
    st.header("Muhasebe Onayı")
    id_onay = st.number_input("ID Seç", step=1)
    fat_no = st.text_input("Fatura No")
    if st.button("Onayla"):
        df.loc[df['ID'] == id_onay, ['Durum', 'Fatura No']] = ['Operasyon Bekliyor', fat_no]
        df.to_csv(DATA_FILE, index=False)
        st.rerun()
    st.dataframe(df[df['Durum'] == 'Muhasebe Onayı Bekliyor'])

elif menu == "⚙️ Operasyon Süreci":
    st.header("Operasyonel İşlemler")
    st.write("Burada bülten, tescil ve itiraz süreçlerini yönetebilirsiniz.")
    st.dataframe(df)

elif menu == "📊 Danışman Raporu":
    st.header("Aylık Ciro ve Sınıf Raporu")
    # Filtreleme mantığı burada çalışır
    st.metric("Toplam Ciro", df[df['Durum'] != 'Muhasebe Onayı Bekliyor']['Tutar'].sum())
```eof
