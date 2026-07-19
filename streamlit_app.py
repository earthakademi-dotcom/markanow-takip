import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- TANIMLAMALAR ---
DATA_FILE = "marka_takip.csv"
ILLER = ["Adana", "Adıyaman", "Afyonkarahisar", "Ağrı", "Aksaray", "Amasya", "Ankara", "Antalya", "Ardahan", "Artvin", "Aydın", "Balıkesir", "Bartın", "Batman", "Bayburt", "Bilecik", "Bingöl", "Bitlis", "Bolu", "Burdur", "Bursa", "Çanakkale", "Çankırı", "Çorum", "Denizli", "Diyarbakır", "Düzce", "Edirne", "Elazığ", "Erzincan", "Erzurum", "Eskişehir", "Gaziantep", "Giresun", "Gümüşhane", "Hakkari", "Hatay", "Iğdır", "Isparta", "İstanbul", "İzmir", "Kahramanmaraş", "Karabük", "Karaman", "Kars", "Kastamonu", "Kayseri", "Kırıkkale", "Kırklareli", "Kırşehir", "Kilis", "Kocaeli", "Konya", "Kütahya", "Malatya", "Manisa", "Mardin", "Mersin", "Muğla", "Muş", "Nevşehir", "Niğde", "Ordu", "Osmaniye", "Rize", "Sakarya", "Samsun", "Siirt", "Sinop", "Sivas", "Şanlıurfa", "Şırnak", "Tekirdağ", "Tokat", "Trabzon", "Tunceli", "Uşak", "Van", "Yalova", "Yozgat", "Zonguldak"]
SINIFLAR = [str(i) for i in range(1, 46)] + [f"35/{i}" for i in range(1, 35)]

def load_data():
    if os.path.exists(DATA_FILE): return pd.read_csv(DATA_FILE)
    return pd.DataFrame(columns=["ID", "Marka Adı", "Ad Soyad", "TC", "Telefon", "Doğum Tarihi", "İl", "Sınıf", "Ödeme", "Satış Tarihi", "Tutar", "Durum", "Danışman", "Fatura No"])

# --- GİRİŞ VE OTURUM ---
if "kullanici" not in st.session_state: st.session_state.kullanici = None

if not st.session_state.kullanici:
    k_adi = st.text_input("Kullanıcı Adı")
    sifre = st.text_input("Şifre", type="password")
    if st.button("Giriş"):
        st.session_state.kullanici = k_adi
        st.rerun()
    st.stop()

# --- MENÜ SİSTEMİ ---
st.sidebar.write(f"👤 Danışman: **{st.session_state.kullanici}**")

# Güvenli Çıkış Butonu
if st.sidebar.button("🚪 Güvenli Çıkış"):
    st.session_state.kullanici = None
    st.rerun()

menu = st.sidebar.radio("Menü", ["📝 Satış Girişi", "📊 Aylık Raporum", "💰 Muhasebe Onayı"])

df = load_data()

# --- MODÜLLER ---
if menu == "📝 Satış Girişi":
    st.header("📝 Yeni Satış Girişi")
    with st.form("yeni_satis", clear_on_submit=True):
        c1, c2 = st.columns(2)
        m_adi = c1.text_input("Marka Adı")
        ad_soyad = c1.text_input("İsim Soyisim")
        tc = c1.text_input("TC (11 Hane)")
        tel = c1.text_input("Telefon")
        dogum = c2.date_input("Doğum Tarihi")
        il = c2.selectbox("İl", ILLER)
        sinif = c2.multiselect("Sınıf Seçimi", SINIFLAR)
        odeme = c2.selectbox("Ödeme", ["EFT", "Kredi Kartı"])
        s_tarihi = c2.date_input("Satış Tarihi")
        tutar = c2.number_input("Tutar (TL)", min_value=0.0)
        
        if st.form_submit_button("Satışı Kaydet"):
            if len(tc) == 11:
                new_row = {"ID": len(df)+1, "Marka Adı": m_adi, "Ad Soyad": ad_soyad, "TC": tc, "Telefon": tel, 
                           "Doğum Tarihi": dogum.strftime("%d/%m/%Y"), "İl": il, "Sınıf": ",".join(sinif),
                           "Ödeme": odeme, "Satış Tarihi": s_tarihi.strftime("%d/%m/%Y"), 
                           "Tutar": tutar, "Durum": "Muhasebe Onayı Bekliyor", "Danışman": st.session_state.kullanici}
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                df.to_csv(DATA_FILE, index=False)
                st.success("Satış muhasebe onayına gönderildi.")
            else: st.error("TC 11 hane olmalı!")

elif menu == "📊 Aylık Raporum":
    st.header("📊 Aylık Rapor")
    df_dan = df[df['Danışman'] == st.session_state.kullanici]
    df_onay = df_dan[df_dan['Durum'] == "Onaylandı"]
    col1, col2 = st.columns(2)
    col1.metric("Toplam Ciro", f"{df_onay['Tutar'].sum():,.2f} TL")
    adet = sum(1 for s in df_onay['Sınıf'] if not str(s).startswith("35/"))
    col2.metric("Toplam Satış Adedi", adet)

elif menu == "💰 Muhasebe Onayı":
    st.header("💰 Muhasebe Onayı Bekleyenler")
    bekleyenler = df[df['Durum'] == "Muhasebe Onayı Bekliyor"]
    st.dataframe(bekleyenler)
    id_sec = st.number_input("Onaylanacak Satış ID", min_value=1, step=1)
    f_no = st.text_input("Fatura No")
    if st.button("Onayla"):
        df.loc[df['ID'] == id_sec, ['Durum', 'Fatura No']] = ["Onaylandı", f_no]
        df.to_csv(DATA_FILE, index=False)
        st.rerun()
