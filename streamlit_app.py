import streamlit as st
import pandas as pd
import os
import json
from datetime import datetime

# --- SAYFA YAPILANDIRMASI ---
st.set_page_config(page_title="Markanow ERP", layout="wide")

# --- TANIMLAMALAR ---
DATA_FILE = "marka_takip.csv"
USER_FILE = "kullanicilar.csv"
PRIM_FILE = "prim_tablosu.json"
ILLER = ["Adana", "Adıyaman", "Afyonkarahisar", "Ağrı", "Aksaray", "Amasya", "Ankara", "Antalya", "Ardahan", "Artvin", "Aydın", "Balıkesir", "Bartın", "Batman", "Bayburt", "Bilecik", "Bingöl", "Bitlis", "Bolu", "Burdur", "Bursa", "Çanakkale", "Çankırı", "Çorum", "Denizli", "Diyarbakır", "Düzce", "Edirne", "Elazığ", "Erzincan", "Erzurum", "Eskişehir", "Gaziantep", "Giresun", "Gümüşhane", "Hakkari", "Hatay", "Iğdır", "Isparta", "İstanbul", "İzmir", "Kahramanmaraş", "Karabük", "Karaman", "Kars", "Kastamonu", "Kayseri", "Kırıkkale", "Kırklareli", "Kırşehir", "Kilis", "Kocaeli", "Konya", "Kütahya", "Malatya", "Manisa", "Mardin", "Mersin", "Muğla", "Muş", "Nevşehir", "Niğde", "Ordu", "Osmaniye", "Rize", "Sakarya", "Samsun", "Siirt", "Sinop", "Sivas", "Şanlıurfa", "Şırnak", "Tekirdağ", "Tokat", "Trabzon", "Tunceli", "Uşak", "Van", "Yalova", "Yozgat", "Zonguldak"]
SINIFLAR = [str(i) for i in range(1, 46)] + [f"35/{i}" for i in range(1, 35)]

def load_data():
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
        df['Satış Tarihi_dt'] = pd.to_datetime(df['Satış Tarihi'], dayfirst=True, errors='coerce')
        return df
    return pd.DataFrame(columns=["ID", "Marka Adı", "Ad Soyad", "TC", "Telefon", "Doğum Tarihi", "İl", "Sınıf", "Ödeme", "Satış Tarihi", "Tutar", "Durum", "Danışman", "Fatura No"])

def load_prim_table():
    default_table = {"20-23": 100, "24-28": 200, "29-33": 300, "34-38": 550, "39-43": 700, "44-48": 850, "49": 1000}
    if os.path.exists(PRIM_FILE):
        try:
            with open(PRIM_FILE, "r") as f: return json.load(f)
        except: return default_table
    return default_table

def say_ana_siniflar(sinif_listesi_str):
    if pd.isna(sinif_listesi_str): return 0
    siniflar = str(sinif_listesi_str).split(',')
    return len([s for s in siniflar if not s.startswith('35/')])

def hesapla_prim(adet):
    table = load_prim_table()
    adet = int(adet)
    if adet >= 49: return float(table.get("49", 1000))
    for k, v in table.items():
        if "-" in k:
            try:
                low, high = map(int, k.split('-'))
                if low <= adet <= high: return float(v)
            except: continue
    return 0.0

# --- GİRİŞ VE OTURUM ---
if "kullanici" not in st.session_state: st.session_state.kullanici = None
if not st.session_state.kullanici:
    st.markdown("<h1 style='text-align: center; color: #1f77b4;'>Markanow Patent Satış Takip ERP</h1>", unsafe_allow_html=True)
    if not os.path.exists(USER_FILE):
        pd.DataFrame({"İsim": ["ALİ OSMAN YELBEY", "DENİZ TELLİ GÜRLEYENDAĞ", "MERVE YURTLU", "SELEN AKCAN"],
                      "Şifre": ["MARKA123", "MARKA123", "MARKA123", "MARKA123"]}).to_csv(USER_FILE, index=False)
    user_df = pd.read_csv(USER_FILE)
    secili = st.selectbox("Kullanıcı Seçiniz", user_df["İsim"].tolist())
    sifre = st.text_input("Şifre", type="password")
    if st.button("Giriş Yap", use_container_width=True):
        user_row = user_df[user_df["İsim"] == secili]
        if str(sifre).strip() == str(user_row.iloc[0]["Şifre"]).strip():
            st.session_state.kullanici = secili
            st.rerun()
    st.stop()

# --- MENÜ SİSTEMİ ---
st.sidebar.write(f"👤 Aktif: **{st.session_state.kullanici}**")
if st.sidebar.button("🚪 Güvenli Çıkış", use_container_width=True):
    st.session_state.kullanici = None; st.rerun()
st.sidebar.write("---")

menu_options = []
if st.session_state.kullanici not in ["ALİ OSMAN YELBEY", "SELEN AKCAN", "DENİZ TELLİ GÜRLEYENDAĞ"]:
    menu_options.extend(["📝 Satış Girişi", "📊 Satışlarım", "📊 Aylık Raporum"])
if st.session_state.kullanici in ["SELEN AKCAN", "ALİ OSMAN YELBEY", "DENİZ TELLİ GÜRLEYENDAĞ"]:
    menu_options.extend(["💰 Muhasebe Onayı", "💰 Satış Danışmanları Prim"])
if st.session_state.kullanici in ["ALİ OSMAN YELBEY", "DENİZ TELLİ GÜRLEYENDAĞ"]:
    menu_options.extend(["📊 Performans Raporu", "👥 Personel Yönetimi"])

menu = st.sidebar.radio("Menü", menu_options)
df = load_data()

# --- MODÜLLER ---
if menu == "📝 Satış Girişi":
    st.header("📝 Yeni Satış Girişi")
    with st.form("yeni_satis", clear_on_submit=True):
        c1, c2 = st.columns(2)
        m_adi = c1.text_input("Marka Adı"); ad_soyad = c1.text_input("İsim Soyisim")
        tc = c1.text_input("TC (11 Hane)"); tel = c1.text_input("Telefon")
        dogum = c2.date_input("Doğum Tarihi"); il = c2.selectbox("İl", ILLER)
        sinif = c2.multiselect("Sınıf Seçimi", SINIFLAR); odeme = c2.selectbox("Ödeme", ["EFT", "Kredi Kartı"])
        s_tarihi = c2.date_input("Satış Tarihi"); tutar = c2.number_input("Tutar (TL)", min_value=0.0)
        if st.form_submit_button("Satışı Kaydet"):
            new_row = {"ID": len(df)+1, "Marka Adı": m_adi, "Ad Soyad": ad_soyad, "TC": tc, "Telefon": tel, 
                       "Doğum Tarihi": dogum.strftime("%d/%m/%Y"), "İl": il, "Sınıf": ",".join(sinif),
                       "Ödeme": odeme, "Satış Tarihi": s_tarihi.strftime("%d/%m/%Y"), 
                       "Tutar": tutar, "Durum": "Muhasebe Onayı Bekliyor", "Danışman": st.session_state.kullanici, "Fatura No": ""}
            pd.concat([df, pd.DataFrame([new_row])], ignore_index=True).to_csv(DATA_FILE, index=False)
            st.success("Satış kaydedildi.")

elif menu == "💰 Satış Danışmanları Prim":
    st.header("💰 Satış Danışmanı Prim Yönetimi")
    tab1, tab2 = st.tabs(["📊 Prim Raporu", "⚙️ Prim Tablosu Düzenle"])
    with tab1:
        danismanlar = df['Danışman'].unique()
        secilen_danisman = st.selectbox("Prim Raporu İçin Danışman Seçin", danismanlar)
        c1, c2 = st.columns(2)
        ay_prim = c1.selectbox("Ay", range(1, 13), index=datetime.now().month-1)
        yil_prim = c2.selectbox("Yıl", sorted(df['Satış Tarihi_dt'].dt.year.dropna().unique(), reverse=True))
        prim_df = df[(df['Danışman'] == secilen_danisman) & (df['Satış Tarihi_dt'].dt.month == ay_prim) & (df['Satış Tarihi_dt'].dt.year == yil_prim) & (df['Durum'] == "Tamamlandı")]
        adet = prim_df['Sınıf'].apply(say_ana_siniflar).sum()
        st.info(f"Danışman: **{secilen_danisman}** | Dönem: **{ay_prim}/{yil_prim}** | Toplam Ana Sınıf: **{adet}**")
        c1, c2 = st.columns(2)
        c1.metric("Toplam Ciro", f"{prim_df['Tutar'].sum():,.2f} TL")
        c2.metric("Hak Edilen Prim", f"{hesapla_prim(adet):,.2f} TL")
        st.dataframe(prim_df)
    with tab2:
        if st.session_state.kullanici in ["ALİ OSMAN YELBEY", "SELEN AKCAN"]:
            prim_table = load_prim_table()
            new_table = {}
            for k, v in prim_table.items():
                new_table[k] = st.number_input(f"{k} Sınıf Prim Değeri (TL)", value=v)
            if st.button("Prim Tablosunu Kaydet"):
                with open(PRIM_FILE, "w") as f: json.dump(new_table, f)
                st.success("Tablo güncellendi!")
        else: st.warning("Prim tablosunu sadece Admin ve Muhasebe düzenleyebilir.")
