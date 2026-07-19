import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- AYARLAR ---
st.set_page_config(page_title="Markanow ERP", layout="wide")
DATA_FILE = "marka_takip.csv"
USER_FILE = "kullanicilar.csv"

# --- VERİ YÜKLEME ---
def load_data():
    if os.path.exists(DATA_FILE): 
        df = pd.read_csv(DATA_FILE)
        # Tarih formatı dönüşümü
        if 'Satış Tarihi' in df.columns:
            df['Satış Tarihi'] = pd.to_datetime(df['Satış Tarihi'], dayfirst=True)
        return df
    return pd.DataFrame(columns=["ID", "Marka Adı", "Ad Soyad", "TC", "Telefon", "Doğum Tarihi", "İl", "Sınıf", "Ödeme", "Satış Tarihi", "Tutar", "Durum", "Danışman", "Fatura No", "Fatura Tarihi"])

# --- GİRİŞ ---
if "kullanici" not in st.session_state: st.session_state.kullanici = None

if not st.session_state.kullanici:
    # (Giriş bloğu aynı kalmıştır)
    st.stop()

df = load_data()
user = st.session_state.kullanici

# --- MENÜ ---
menu_options = ["📝 Yeni Satış", "📂 Satışlarım", "📊 Aylık Raporum"]
if user in ["SELEN AKCAN", "ALİ OSMAN YELBEY", "DENİZ TELLİ GÜRLEYENDAĞ"]:
    menu_options.append("💰 Muhasebe Onayı")
if user in ["MERVE YURTLU"]: # Fatura oluşturma yetkisi olanlar
    menu_options.append("🧾 Fatura Oluşturma")
if user in ["ALİ OSMAN YELBEY", "DENİZ TELLİ GÜRLEYENDAĞ"]:
    menu_options.extend(["📊 Performans Raporu", "👥 Personel Yönetimi"])

menu = st.sidebar.radio("Menü", menu_options)

# --- MODÜLLER ---
if menu == "📂 Satışlarım":
    st.header("📂 Satışlarım")
    my_sales = df[df['Danışman'] == user].copy()
    
    # Filtreleme
    c1, c2, c3 = st.columns(3)
    ay_filtre = c1.selectbox("Ay Seçin", range(1, 13), index=datetime.now().month-1)
    # Sınıf/Ciro filtreleri buraya eklenebilir
    
    filtered_sales = my_sales[my_sales['Satış Tarihi'].dt.month == ay_filtre]
    st.dataframe(filtered_sales, use_container_width=True)

elif menu == "💰 Muhasebe Onayı":
    st.header("💰 Muhasebe Onayı")
    bekleyenler = df[df['Durum'] == "Muhasebe Onayı Bekliyor"]
    st.dataframe(bekleyenler)
    # Onaylama mantığı...

elif menu == "🧾 Fatura Oluşturma":
    st.header("🧾 Fatura Oluşturma")
    onayli_sales = df[(df['Danışman'] == user) & (df['Durum'] == "Onaylandı") & (df['Fatura No'].isna())]
    st.dataframe(onayli_sales)
    
    id_sec = st.number_input("İşlem ID", min_value=1)
    f_no = st.text_input("Fatura No")
    f_tar = st.date_input("Fatura Tarihi")
    
    if st.button("Faturayı İşle"):
        df.loc[df['ID'] == id_sec, ['Fatura No', 'Fatura Tarihi', 'Durum']] = [f_no, f_tar, "Tamamlandı"]
        df.to_csv(DATA_FILE, index=False)
        st.success("Fatura oluşturuldu, Admin raporuna eklendi.")
        st.rerun()
