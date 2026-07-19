import streamlit as st
import pandas as pd
import os
from datetime import datetime

# ... existing code ... (TANIMLAMALAR ve load_data aynı)
DATA_FILE = "marka_takip.csv"
ILLER = ["Adana", "Adıyaman", "Afyonkarahisar", "Ağrı", "Aksaray", "Amasya", "Ankara", "Antalya", "Ardahan", "Artvin", "Aydın", "Balıkesir", "Bartın", "Batman", "Bayburt", "Bilecik", "Bingöl", "Bitlis", "Bolu", "Burdur", "Bursa", "Çanakkale", "Çankırı", "Çorum", "Denizli", "Diyarbakır", "Düzce", "Edirne", "Elazığ", "Erzincan", "Erzurum", "Eskişehir", "Gaziantep", "Giresun", "Gümüşhane", "Hakkari", "Hatay", "Iğdır", "Isparta", "İstanbul", "İzmir", "Kahramanmaraş", "Karabük", "Karaman", "Kars", "Kastamonu", "Kayseri", "Kırıkkale", "Kırklareli", "Kırşehir", "Kilis", "Kocaeli", "Konya", "Kütahya", "Malatya", "Manisa", "Mardin", "Mersin", "Muğla", "Muş", "Nevşehir", "Niğde", "Ordu", "Osmaniye", "Rize", "Sakarya", "Samsun", "Siirt", "Sinop", "Sivas", "Şanlıurfa", "Şırnak", "Tekirdağ", "Tokat", "Trabzon", "Tunceli", "Uşak", "Van", "Yalova", "Yozgat", "Zonguldak"]
SINIFLAR = [str(i) for i in range(1, 46)] + [f"35/{i}" for i in range(1, 35)]

def load_data():
    if os.path.exists(DATA_FILE): return pd.read_csv(DATA_FILE)
    return pd.DataFrame(columns=["ID", "Marka Adı", "Ad Soyad", "TC", "Telefon", "Doğum Tarihi", "İl", "Sınıf", "Ödeme", "Satış Tarihi", "Tutar", "Durum", "Danışman"])

# ... existing code ... (GİRİŞ PANELİ aynı)
if "kullanici" not in st.session_state: st.session_state.kullanici = None
# (Giriş kısmı atlanmıştır - önceki kodu kullanın)

# STREAMING_CHUNK: Gelişmiş Menü (Muhasebe Yetkisi Eklendi)
st.sidebar.write(f"👤 Kullanıcı: {st.session_state.kullanici}")
menu_options = ["📝 Satış Girişi", "📊 Aylık Raporum"]
if st.session_state.kullanici == "Muhasebe Kullanıcısı":
    menu_options.append("⏳ Onay Bekleyenler")

menu = st.sidebar.radio("Menü", menu_options)
df = load_data()

# STREAMING_CHUNK: Satış Girişi (Onay Bekliyor Durumu)
if menu == "📝 Satış Girişi":
    # ... existing code ... (Satış girişi aynı kalıyor, sadece Durum = "Muhasebe Onayı Bekliyor")
    pass

# STREAMING_CHUNK: Muhasebe Onay Paneli
elif menu == "⏳ Onay Bekleyenler":
    st.header("⏳ Onay Bekleyen Satışlar")
    bekleyenler = df[df['Durum'] == "Muhasebe Onayı Bekliyor"]
    st.dataframe(bekleyenler)
    
    id_sec = st.number_input("Onaylanacak Satış ID", min_value=1, step=1)
    if st.button("Onayla"):
        df.loc[df['ID'] == id_sec, 'Durum'] = 'Onaylandı'
        df.to_csv(DATA_FILE, index=False)
        st.success("Satış onaylandı!")
        st.rerun()

elif menu == "📊 Aylık Raporum":
    # Rapor artık sadece onaylıları sayıyor
    df_onayli = df[(df['Danışman'] == st.session_state.kullanici) & (df['Durum'] == 'Onaylandı')]
    # ... (Geri kalan raporlama aynı)
