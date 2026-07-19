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
    try: adet = int(float(adet))
    except: return 0.0
    if adet >= 49: return float(adet * table.get("49", 1000))
    for k, v in table.items():
        if "-" in k:
            try:
                low, high = map(int, k.split('-'))
                if low <= adet <= high: return float(adet * v)
            except: continue
    return 0.0

# --- GİRİŞ ---
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

# --- MENÜ ---
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

elif menu == "📊 Satışlarım":
    st.header(f"📊 {st.session_state.kullanici} - Güncel Ay Satışları")
    my_df = df[df['Danışman'] == st.session_state.kullanici].copy()
    now = datetime.now()
    filtered = my_df[(my_df['Satış Tarihi_dt'].dt.month == now.month) & (my_df['Satış Tarihi_dt'].dt.year == now.year)]
    onayli = filtered[filtered['Durum'] == "Onaylandı"]
    c1, c2 = st.columns(2)
    c1.metric("Bu Ay Toplam Ciro", f"{onayli['Tutar'].sum():,.2f} TL")
    c2.metric("Bu Ay Toplam Ana Sınıf", onayli['Sınıf'].apply(say_ana_siniflar).sum())
    st.dataframe(filtered, use_container_width=True)

elif menu == "💰 Muhasebe Onayı":
    st.header("💰 Muhasebe Onay ve Düzenleme Paneli")
    # Düzenleme Bölümü
    with st.expander("✏️ Yanlış Girilen Satışı Düzenle"):
        secili_id = st.number_input("Düzenlenecek Satış ID", step=1)
        if secili_id in df['ID'].values:
            row = df[df['ID'] == secili_id].iloc[0]
            with st.form("duzenleme_formu"):
                c1, c2 = st.columns(2)
                y_marka = c1.text_input("Marka Adı", value=row['Marka Adı'])
                y_tutar = c2.number_input("Tutar (TL)", value=float(row['Tutar']))
                y_durum = c1.selectbox("Durum", ["Muhasebe Onayı Bekliyor", "Onaylandı", "Tamamlandı"], index=["Muhasebe Onayı Bekliyor", "Onaylandı", "Tamamlandı"].index(row['Durum']))
                y_fatura = c2.text_input("Fatura No", value=str(row['Fatura No']) if pd.notna(row['Fatura No']) else "")
                if st.form_submit_button("Güncelle"):
                    df.loc[df['ID'] == secili_id, ['Marka Adı', 'Tutar', 'Durum', 'Fatura No']] = [y_marka, y_tutar, y_durum, y_fatura]
                    df.to_csv(DATA_FILE, index=False); st.success("Satış güncellendi!"); st.rerun()
        else: st.info("Düzenlemek için geçerli bir ID girin.")

    st.write("---")
    bekleyen = df[df['Durum'] == "Muhasebe Onayı Bekliyor"]
    for i, row in bekleyen.iterrows():
        cols = st.columns([1, 8])
        if cols[0].button("✅ Onayla", key=f"onay_{row['ID']}"):
            df.loc[df['ID'] == row['ID'], 'Durum'] = "Onaylandı"
            df.to_csv(DATA_FILE, index=False); st.rerun()
        cols[1].write(f"ID: {row['ID']} | Marka: {row['Marka Adı']} | Tutar: {row['Tutar']} TL | Danışman: {row['Danışman']}")

elif menu == "📊 Performans Raporu":
    st.header("📊 Kurumsal Performans Paneli")
    rapor = df[df['Durum'] == "Tamamlandı"].groupby('Danışman')['Tutar'].sum()
    st.bar_chart(rapor)

elif menu == "👥 Personel Yönetimi":
    st.header("👥 Personel ve Veri Yönetimi")
    with st.expander("⚠️ YÖNETİCİ: TÜM VERİLERİ SIFIRLA"):
        st.warning("Bu işlem tüm satış, onay ve fatura verilerini KALICI olarak siler.")
        if st.button("TÜM VERİLERİ SİL"):
            if os.path.exists(DATA_FILE):
                os.remove(DATA_FILE)
                st.error("Tüm veriler temizlendi, lütfen sayfayı yenileyin.")
                st.rerun()

    users_df = pd.read_csv(USER_FILE)
    st.dataframe(users_df, use_container_width=True)
    tab1, tab2, tab3 = st.tabs(["➕ Ekle", "🔑 Şifre Değiştir", "❌ Sil"])
    with tab1:
        yeni_ad = st.text_input("Personel Adı", key="ekle_ad")
        yeni_sifre = st.text_input("Şifre Belirle", type="password", key="ekle_sifre")
        if st.button("Personel Ekle"):
            pd.concat([users_df, pd.DataFrame({"İsim": [yeni_ad], "Şifre": [yeni_sifre]})], ignore_index=True).to_csv(USER_FILE, index=False); st.rerun()
    with tab2:
        secilen_p = st.selectbox("Personel Seçin", users_df["İsim"].tolist(), key="guncelle_sec")
        yeni_sifre_g = st.text_input("Yeni Şifre", type="password", key="guncelle_sifre")
        if st.button("Şifreyi Güncelle"):
            users_df.loc[users_df["İsim"] == secilen_p, "Şifre"] = yeni_sifre_g
            users_df.to_csv(USER_FILE, index=False); st.rerun()
    with tab3:
        silinecek = st.selectbox("Silinecek Personel", users_df["İsim"].tolist(), key="sil_sec")
        if st.button("Personeli Sil"):
            users_df[users_df["İsim"] != silinecek].to_csv(USER_FILE, index=False); st.rerun()
