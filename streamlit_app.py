import streamlit as st
import pandas as pd
import os

# --- SAYFA YAPILANDIRMASI ---
st.set_page_config(page_title="Markanow ERP", layout="centered")

# --- TANIMLAMALAR ---
DATA_FILE = "marka_takip.csv"
USER_FILE = "kullanicilar.csv"
ILLER = ["Adana", "Adıyaman", "Afyonkarahisar", "Ağrı", "Aksaray", "Amasya", "Ankara", "Antalya", "Ardahan", "Artvin", "Aydın", "Balıkesir", "Bartın", "Batman", "Bayburt", "Bilecik", "Bingöl", "Bitlis", "Bolu", "Burdur", "Bursa", "Çanakkale", "Çankırı", "Çorum", "Denizli", "Diyarbakır", "Düzce", "Edirne", "Elazığ", "Erzincan", "Erzurum", "Eskişehir", "Gaziantep", "Giresun", "Gümüşhane", "Hakkari", "Hatay", "Iğdır", "Isparta", "İstanbul", "İzmir", "Kahramanmaraş", "Karabük", "Karaman", "Kars", "Kastamonu", "Kayseri", "Kırıkkale", "Kırklareli", "Kırşehir", "Kilis", "Kocaeli", "Konya", "Kütahya", "Malatya", "Manisa", "Mardin", "Mersin", "Muğla", "Muş", "Nevşehir", "Niğde", "Ordu", "Osmaniye", "Rize", "Sakarya", "Samsun", "Siirt", "Sinop", "Sivas", "Şanlıurfa", "Şırnak", "Tekirdağ", "Tokat", "Trabzon", "Tunceli", "Uşak", "Van", "Yalova", "Yozgat", "Zonguldak"]
SINIFLAR = [str(i) for i in range(1, 46)] + [f"35/{i}" for i in range(1, 35)]

def load_data():
    if os.path.exists(DATA_FILE): return pd.read_csv(DATA_FILE)
    return pd.DataFrame(columns=["ID", "Marka Adı", "Ad Soyad", "TC", "Telefon", "Doğum Tarihi", "İl", "Sınıf", "Ödeme", "Satış Tarihi", "Tutar", "Durum", "Danışman", "Fatura No"])

# --- GİRİŞ VE OTURUM ---
if "kullanici" not in st.session_state: st.session_state.kullanici = None

if not st.session_state.kullanici:
    st.markdown("<h1 style='text-align: center; color: #1f77b4;'>Markanow Patent Satış Takip ERP</h1>", unsafe_allow_html=True)
    if not os.path.exists(USER_FILE):
        pd.DataFrame({"İsim": ["ALİ OSMAN YELBEY", "DENİZ TELLİ GÜRLEYENDAĞ", "MERVE YURTLU", "SELEN AKCAN", "OPERASYON YETKİLİSİ"],
                      "Şifre": ["MARKA123", "MARKA123", "MARKA123", "MARKA123", "MARKA123"]}).to_csv(USER_FILE, index=False)
    user_df = pd.read_csv(USER_FILE)
    user_df.columns = ["İsim", "Şifre"]
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        secili_kullanici = st.selectbox("Kullanıcı Seçiniz", user_df["İsim"].tolist())
        girilen_sifre = st.text_input("Şifre", type="password")
        if st.button("Giriş Yap", use_container_width=True):
            user_row = user_df[user_df["İsim"] == secili_kullanici]
            if str(girilen_sifre).strip() == str(user_row.iloc[0]["Şifre"]).strip():
                st.session_state.kullanici = secili_kullanici
                st.rerun()
            else: st.error("Hatalı şifre!")
    st.stop()

# --- MENÜ SİSTEMİ ---
st.sidebar.title("Markanow ERP")
st.sidebar.write(f"👤 Aktif: **{st.session_state.kullanici}**")
if st.sidebar.button("🚪 Güvenli Çıkış", use_container_width=True):
    st.session_state.kullanici = None
    st.rerun()

st.sidebar.write("---")
menu_options = []
if st.session_state.kullanici != "ALİ OSMAN YELBEY":
    menu_options.append("📝 Satış Girişi")
menu_options.extend(["📊 Aylık Raporum", "💰 Muhasebe Onayı"])

if st.session_state.kullanici in ["ALİ OSMAN YELBEY", "DENİZ TELLİ GÜRLEYENDAĞ"]:
    menu_options.append("📊 Performans Raporu")
    menu_options.append("👥 Personel Yönetimi")

menu = st.sidebar.radio("Menü", menu_options)
df = load_data()

# --- MODÜLLER ---
if menu == "📝 Satış Girişi":
    st.header("📝 Yeni Satış Girişi")
    # ... (Satış giriş kodunuz) ...
    pass 

elif menu == "📊 Performans Raporu":
    st.header("📊 Kurumsal Performans Paneli")
    # ... (Rapor kodunuz) ...
    pass

elif menu == "👥 Personel Yönetimi":
    st.header("👥 Personel Yönetimi")
    users_df = pd.read_csv(USER_FILE)
    st.dataframe(users_df, use_container_width=True)
    
    # Sekmeli Yapı
    tab1, tab2, tab3 = st.tabs(["➕ Ekle", "🔑 Şifre Değiştir", "❌ Sil"])
    
    with tab1:
        yeni_ad = st.text_input("Personel Adı", key="yeni_ad")
        yeni_sifre = st.text_input("Şifre Belirle", type="password", key="yeni_sifre")
        if st.button("Personel Ekle"):
            pd.concat([users_df, pd.DataFrame({"İsim": [yeni_ad], "Şifre": [yeni_sifre]})], ignore_index=True).to_csv(USER_FILE, index=False)
            st.rerun()
            
    with tab2:
        secilen_p = st.selectbox("Personel Seçin", users_df["İsim"].tolist(), key="guncelle_sec")
        yeni_sifre_g = st.text_input("Yeni Şifre", type="password", key="guncelle_sifre")
        if st.button("Şifreyi Güncelle"):
            users_df.loc[users_df["İsim"] == secilen_p, "Şifre"] = yeni_sifre_g
            users_df.to_csv(USER_FILE, index=False)
            st.success("Şifre güncellendi.")
            st.rerun()
            
    with tab3:
        silinecek = st.selectbox("Silinecek Personel", users_df["İsim"].tolist(), key="sil_sec")
        if st.button("Personeli Sil"):
            users_df[users_df["İsim"] != silinecek].to_csv(USER_FILE, index=False)
            st.rerun()
