import streamlit as st
import pandas as pd
import os
from datetime import datetime

# STREAMING_CHUNK: Tanımlamalar
DATA_FILE = "marka_takip.csv"
ILLER = ["Adana", "Adıyaman", "Afyonkarahisar", "Ağrı", "Aksaray", "Amasya", "Ankara", "Antalya", "Ardahan", "Artvin", "Aydın", "Balıkesir", "Bartın", "Batman", "Bayburt", "Bilecik", "Bingöl", "Bitlis", "Bolu", "Burdur", "Bursa", "Çanakkale", "Çankırı", "Çorum", "Denizli", "Diyarbakır", "Düzce", "Edirne", "Elazığ", "Erzincan", "Erzurum", "Eskişehir", "Gaziantep", "Giresun", "Gümüşhane", "Hakkari", "Hatay", "Iğdır", "Isparta", "İstanbul", "İzmir", "Kahramanmaraş", "Karabük", "Karaman", "Kars", "Kastamonu", "Kayseri", "Kırıkkale", "Kırklareli", "Kırşehir", "Kilis", "Kocaeli", "Konya", "Kütahya", "Malatya", "Manisa", "Mardin", "Mersin", "Muğla", "Muş", "Nevşehir", "Niğde", "Ordu", "Osmaniye", "Rize", "Sakarya", "Samsun", "Siirt", "Sinop", "Sivas", "Şanlıurfa", "Şırnak", "Tekirdağ", "Tokat", "Trabzon", "Tunceli", "Uşak", "Van", "Yalova", "Yozgat", "Zonguldak"]
SINIFLAR = [str(i) for i in range(1, 46)] + [f"35/{i}" for i in range(1, 35)]

def load_data():
    if os.path.exists(DATA_FILE): return pd.read_csv(DATA_FILE)
    return pd.DataFrame(columns=["ID", "Marka Adı", "Ad Soyad", "TC", "Telefon", "Doğum Tarihi", "İl", "Sınıf", "Ödeme", "Satış Tarihi", "Tutar", "Durum", "Danışman"])

# STREAMING_CHUNK: Giriş Paneli
if "kullanici" not in st.session_state: st.session_state.kullanici = None
if not st.session_state.kullanici:
    k_adi = st.text_input("Kullanıcı Adı")
    sifre = st.text_input("Şifre", type="password")
    if st.button("Giriş"):
        st.session_state.kullanici = k_adi
        st.rerun()
    st.stop()

# STREAMING_CHUNK: Satış Danışmanı Paneli
st.sidebar.write(f"👤 Danışman: {st.session_state.kullanici}")
menu = st.sidebar.radio("Menü", ["📝 Satış Girişi", "📊 Aylık Raporum"])

df = load_data()

if menu == "📝 Satış Girişi":
    st.header("📝 Yeni Satış Girişi")
    with st.form("yeni_satis"):
        c1, c2 = st.columns(2)
        m_adi = c1.text_input("Marka Adı")
        ad_soyad = c1.text_input("İsim Soyisim")
        tc = c1.text_input("TC (11 Hane)")
        tel = c1.text_input("Telefon")
        dogum = c2.date_input("Doğum Tarihi")
        il = c2.selectbox("İl", ILLER)
        sinif = c2.multiselect("Sınıf Seçimi", SINIFLAR)
        odeme = c2.selectbox("Ödeme", ["EFT", "Kredi Kartı"])
        tutar = c2.number_input("Tutar (TL)", min_value=0.0)
        
        if st.form_submit_button("Satışı Kaydet"):
            if len(tc) == 11:
                new_row = {"ID": len(df)+1, "Marka Adı": m_adi, "Ad Soyad": ad_soyad, "TC": tc, "Telefon": tel, 
                           "Doğum Tarihi": dogum.strftime("%d/%m/%Y"), "İl": il, "Sınıf": ",".join(sinif),
                           "Ödeme": odeme, "Satış Tarihi": datetime.now().strftime("%d/%m/%Y"), 
                           "Tutar": tutar, "Durum": "Muhasebe Onayı Bekliyor", "Danışman": st.session_state.kullanici}
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                df.to_csv(DATA_FILE, index=False)
                st.success("Satış kaydedildi.")
            else: st.error("TC 11 hane olmalı!")

elif menu == "📊 Aylık Raporum":
    st.header("📊 Aylık Rapor")
    # Adet hesaplama (35/ ile başlayanlar hariç)
    df_danisman = df[df['Danışman'] == st.session_state.kullanici]
    df_danisman = df_danisman[df_danisman['Durum'] != "Muhasebe Onayı Bekliyor"]
    
    col1, col2 = st.columns(2)
    col1.metric("Toplam Ciro", f"{df_danisman['Tutar'].sum():,.2f} TL")
    
    # Adet hesabı: 35/ olmayan sınıflar
    adet = 0
    for s in df_danisman['Sınıf']:
        if not str(s).startswith("35/"): adet += 1
    col2.metric("Toplam Satış Adedi", adet)
