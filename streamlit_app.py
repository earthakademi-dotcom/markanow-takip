import streamlit as st
import pandas as pd
import os

# --- SAYFA YAPILANDIRMASI ---
st.set_page_config(page_title="Markanow ERP", layout="centered")

# --- TANIMLAMALAR ---
DATA_FILE = "marka_takip.csv"
USER_FILE = "kullanicilar.csv" # Kullanıcı listesi için yeni dosya
ILLER = ["Adana", "Adıyaman", "Afyonkarahisar", "Ağrı", "Aksaray", "Amasya", "Ankara", "Antalya", "Ardahan", "Artvin", "Aydın", "Balıkesir", "Bartın", "Batman", "Bayburt", "Bilecik", "Bingöl", "Bitlis", "Bolu", "Burdur", "Bursa", "Çanakkale", "Çankırı", "Çorum", "Denizli", "Diyarbakır", "Düzce", "Edirne", "Elazığ", "Erzincan", "Erzurum", "Eskişehir", "Gaziantep", "Giresun", "Gümüşhane", "Hakkari", "Hatay", "Iğdır", "Isparta", "İstanbul", "İzmir", "Kahramanmaraş", "Karabük", "Karaman", "Kars", "Kastamonu", "Kayseri", "Kırıkkale", "Kırklareli", "Kırşehir", "Kilis", "Kocaeli", "Konya", "Kütahya", "Malatya", "Manisa", "Mardin", "Mersin", "Muğla", "Muş", "Nevşehir", "Niğde", "Ordu", "Osmaniye", "Rize", "Sakarya", "Samsun", "Siirt", "Sinop", "Sivas", "Şanlıurfa", "Şırnak", "Tekirdağ", "Tokat", "Trabzon", "Tunceli", "Uşak", "Van", "Yalova", "Yozgat", "Zonguldak"]
SINIFLAR = [str(i) for i in range(1, 46)] + [f"35/{i}" for i in range(1, 35)]

# Başlangıç Kullanıcı Listesi
if not os.path.exists(USER_FILE):
    pd.DataFrame({"İsim": ["ALİ OSMAN YELBEY", "DENİZ TELLİ GÜRLEYENDAĞ", "MERVE YURTLU", "SELEN AKCAN", "OPERASYON YETKİLİSİ"]}).to_csv(USER_FILE, index=False)

def load_data():
    if os.path.exists(DATA_FILE): return pd.read_csv(DATA_FILE)
    return pd.DataFrame(columns=["ID", "Marka Adı", "Ad Soyad", "TC", "Telefon", "Doğum Tarihi", "İl", "Sınıf", "Ödeme", "Satış Tarihi", "Tutar", "Durum", "Danışman", "Fatura No"])

def get_users():
    return pd.read_csv(USER_FILE)["İsim"].tolist()

# --- GİRİŞ VE OTURUM ---
if "kullanici" not in st.session_state: st.session_state.kullanici = None

if not st.session_state.kullanici:
    st.markdown("<h1 style='text-align: center; color: #1f77b4;'>Markanow Patent Satış Takip ERP</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        k_adi = st.selectbox("Kullanıcı Seçiniz", get_users())
        if st.button("Giriş Yap", use_container_width=True):
            st.session_state.kullanici = k_adi
            st.rerun()
    st.stop()

# --- MENÜ SİSTEMİ ---
st.sidebar.title("Markanow ERP")
st.sidebar.write(f"👤 Aktif: **{st.session_state.kullanici}**")

if st.sidebar.button("🚪 Güvenli Çıkış", use_container_width=True):
    st.session_state.kullanici = None
    st.rerun()

st.sidebar.write("---")
menu_options = ["📝 Satış Girişi", "📊 Aylık Raporum", "💰 Muhasebe Onayı"]

# Admin ve Müdür için Personel Yönetimi yetkisi
yetkili_liste = ["ALİ OSMAN YELBEY", "DENİZ TELLİ GÜRLEYENDAĞ"]
if st.session_state.kullanici in yetkili_liste:
    menu_options.append("👥 Personel Yönetimi")

menu = st.sidebar.radio("Menü", menu_options)
df = load_data()

# --- MODÜLLER ---
if menu == "📝 Satış Girişi":
    # ... (Aynı kalacak)
    pass

elif menu == "📊 Aylık Raporum":
    # ... (Aynı kalacak)
    pass

elif menu == "💰 Muhasebe Onayı":
    # ... (Aynı kalacak)
    pass

elif menu == "👥 Personel Yönetimi":
    st.header("👥 Personel Yönetimi")
    users_df = pd.read_csv(USER_FILE)
    st.dataframe(users_df)
    
    yeni_personel = st.text_input("Eklenecek Personel Adı")
    if st.button("Personel Ekle"):
        new_df = pd.concat([users_df, pd.DataFrame({"İsim": [yeni_personel]})], ignore_index=True)
        new_df.to_csv(USER_FILE, index=False)
        st.success("Eklendi.")
        st.rerun()
        
    silinecek = st.selectbox("Silinecek Personel", users_df["İsim"].tolist())
    if st.button("Personel Sil"):
        users_df = users_df[users_df["İsim"] != silinecek]
        users_df.to_csv(USER_FILE, index=False)
        st.warning("Silindi.")
        st.rerun()
