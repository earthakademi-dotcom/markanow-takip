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

# Başlangıç Kullanıcı Listesi (Eğer dosya yoksa oluştur)
if not os.path.exists(USER_FILE):
    pd.DataFrame({
        "İsim": ["ALİ OSMAN YELBEY", "DENİZ TELLİ GÜRLEYENDAĞ", "MERVE YURTLU", "SELEN AKCAN", "OPERASYON YETKİLİSİ"],
        "Şifre": ["12", "12", "12", "12", "12"]
    }).to_csv(USER_FILE, index=False)

def load_data():
    if os.path.exists(DATA_FILE): return pd.read_csv(DATA_FILE)
    return pd.DataFrame(columns=["ID", "Marka Adı", "Ad Soyad", "TC", "Telefon", "Doğum Tarihi", "İl", "Sınıf", "Ödeme", "Satış Tarihi", "Tutar", "Durum", "Danışman", "Fatura No"])

# --- GİRİŞ VE OTURUM ---
if "kullanici" not in st.session_state: st.session_state.kullanici = None

if not st.session_state.kullanici:
    st.markdown("<h1 style='text-align: center; color: #1f77b4;'>Markanow Patent Satış Takip ERP</h1>", unsafe_allow_html=True)
    
    user_df = pd.read_csv(USER_FILE)
    user_df.columns = user_df.columns.str.strip() # Sütun isimlerindeki boşlukları temizle
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        secili_kullanici = st.selectbox("Kullanıcı Seçiniz", user_df["İsim"].tolist())
        girilen_sifre = st.text_input("Şifre", type="password")
        
        if st.button("Giriş Yap", use_container_width=True):
            # Seçilen kullanıcının satırını bul
            user_row = user_df[user_df["İsim"] == secili_kullanici]
            if not user_row.empty:
                sifre_dogru = str(user_row.iloc[0]["Şifre"])
                if str(girilen_sifre).strip() == sifre_dogru.strip():
                    st.session_state.kullanici = secili_kullanici
                    st.rerun()
                else:
                    st.error("Hatalı şifre!")
    st.stop()

# --- MENÜ SİSTEMİ ---
st.sidebar.title("Markanow ERP")
st.sidebar.write(f"👤 Aktif: **{st.session_state.kullanici}**")
if st.sidebar.button("🚪 Güvenli Çıkış", use_container_width=True):
    st.session_state.kullanici = None
    st.rerun()

st.sidebar.write("---")
menu_options = ["📝 Satış Girişi", "📊 Aylık Raporum", "💰 Muhasebe Onayı"]
if st.session_state.kullanici in ["ALİ OSMAN YELBEY", "DENİZ TELLİ GÜRLEYENDAĞ"]:
    menu_options.append("👥 Personel Yönetimi")
menu = st.sidebar.radio("Menü", menu_options)
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
                pd.concat([df, pd.DataFrame([new_row])], ignore_index=True).to_csv(DATA_FILE, index=False)
                st.success("Satış kaydedildi.")
            else: st.error("TC 11 hane olmalı!")

elif menu == "👥 Personel Yönetimi":
    st.header("👥 Personel Yönetimi")
    users_df = pd.read_csv(USER_FILE)
    users_df.columns = users_df.columns.str.strip() # Hata almamak için temizle
    st.dataframe(users_df)
    
    yeni_ad = st.text_input("Personel Adı")
    yeni_sifre = st.text_input("Şifre Belirle", type="password")
    if st.button("Personel Ekle"):
        new_df = pd.concat([users_df, pd.DataFrame({"İsim": [yeni_ad], "Şifre": [yeni_sifre]})], ignore_index=True)
        new_df.to_csv(USER_FILE, index=False)
        st.rerun()
        
    silinecek = st.selectbox("Silinecek Personel", users_df["İsim"].tolist())
    if st.button("Personel Sil"):
        users_df[users_df["İsim"] != silinecek].to_csv(USER_FILE, index=False)
        st.rerun()
