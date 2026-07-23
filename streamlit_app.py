import streamlit as st
import pandas as pd
import os
import json
import base64
from datetime import datetime

# --- SAYFA YAPILANDIRMASI ---
st.set_page_config(page_title="Markanow ERP", layout="wide")

# Logo dosyasını base64 formatına çevirme
logo_path = "sosyalmedya-2.jpg.jpg"
logo_base64 = ""
if os.path.exists(logo_path):
    with open(logo_path, "rb") as f:
        logo_base64 = base64.b64encode(f.read()).decode()

# --- GLOBAL CSS ---
st.markdown(
    f"""
    <style>
    .stApp {{
        background: linear-gradient(rgba(34, 34, 34, 0.85), rgba(34, 34, 34, 0.85)), url("data:image/jpeg;base64,{logo_base64}") !important;
        background-size: cover !important;
        background-position: center !important;
        background-repeat: no-repeat !important;
        background-attachment: fixed !important;
    }}

    h1, h2, h3, h4, h5, h6, 
    .stTextInput label, 
    .stSelectbox label, 
    .stDateInput label, 
    .stNumberInput label, 
    .stMultiSelect label,
    div[data-testid="stMarkdownContainer"] p {{
        color: #FFFFFF !important;
    }}
    
    [data-testid="stSidebar"] {{
        background-color: #6b1d2f !important;
        overflow-y: auto !important;
        max-height: 100vh !important;
    }}
    
    [data-testid="stSidebar"] span, 
    [data-testid="stSidebar"] p, 
    [data-testid="stSidebar"] label, 
    [data-testid="stSidebar"] div, 
    [data-testid="stSidebar"] .stRadio label {{
        color: #FFFFFF !important;
    }}

    div.stButton > button:first-child {{
        background-color: #2C3E50 !important;
        color: #FFFFFF !important;
        border: 1px solid #34495E !important;
    }}
    div.stButton > button:first-child:hover {{
        background-color: #34495E !important;
        color: #FFFFFF !important;
        border: 1px solid #3d566e !important;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# --- TANIMLAMALAR ---
DATA_FILE = "marka_takip.csv"
USER_FILE = "users.csv"
PRIM_FILE = "prim_tablosu.json"
ILLER = ["Adana", "Adıyaman", "Afyonkarahisar", "Ağrı", "Aksaray", "Amasya", "Ankara", "Antalya", "Ardahan", "Artvin", "Aydın", "Balıkesir", "Bartın", "Batman", "Bayburt", "Bilecik", "Bingöl", "Bitlis", "Bolu", "Burdur", "Bursa", "Çanakkale", "Çankırı", "Çorum", "Denizli", "Diyarbakır", "Düzce", "Edirne", "Elazığ", "Erzincan", "Erzurum", "Eskişehir", "Gaziantep", "Giresun", "Gümüşhane", "Hakkari", "Hatay", "Iğdır", "Isparta", "İstanbul", "İzmir", "Kahramanmaraş", "Karabük", "Karaman", "Kars", "Kastamonu", "Kayseri", "Kırıkkale", "Kırklareli", "Kırşehir", "Kilis", "Kocaeli", "Konya", "Kütahya", "Malatya", "Manisa", "Mardin", "Mersin", "Muğla", "Muş", "Nevşehir", "Niğde", "Ordu", "Osmaniye", "Rize", "Sakarya", "Samsun", "Siirt", "Sinop", "Sivas", "Şanlıurfa", "Şırnak", "Tekirdağ", "Tokat", "Trabzon", "Tunceli", "Uşak", "Van", "Yalova", "Yozgat", "Zonguldak"]
SINIFLAR = [str(i) for i in range(1, 46)] + [f"35/{i}" for i in range(1, 35)]

def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE, dtype=str)
    return pd.DataFrame(columns=["ID", "Marka Adı", "Ad Soyad", "TC", "Telefon", "Doğum Tarihi", "İl", "Sınıf", "Ödeme", "Satış Tarihi", "Tutar", "Durum", "Danışman", "Fatura No"])

# --- GİRİŞ ---
if "kullanici" not in st.session_state: 
    st.session_state.kullanici = None

if not st.session_state.kullanici:
    st.markdown("<h1 style='text-align: center; color: #FFFFFF;'>Markanow Patent Satış Takip ERP</h1>", unsafe_allow_html=True)
    
    if not os.path.exists(USER_FILE):
        pd.DataFrame({"İsim": ["ALİ OSMAN YELBEY", "DENİZ TELLİ GÜRLEYENDAĞ", "MERVE YURTLU", "SELEN AKCAN"],
                      "Şifre": ["MARKA123", "MARKA123", "MARKA123", "MARKA123"]}).to_csv(USER_FILE, index=False)
    
    user_df = pd.read_csv(USER_FILE)
    secili = st.selectbox("Kullanıcı Seçiniz", user_df["İsim"].tolist())
    sifre = st.text_input("Şifre", type="password")
    
    if st.button("Giriş Yap", use_container_width=True):
        if str(sifre).strip() == str(user_df[user_df["İsim"] == secili].iloc[0]["Şifre"]).strip():
            st.session_state.kullanici = secili
            st.rerun()
        else:
            st.error("Hatalı Şifre!")
            
    st.stop()

# --- MENÜ ---
st.sidebar.markdown(
    """
    <style>
    div.stButton > button {
        background-color: #2C3E50;
        color: white;
    }
    div.stButton > button:hover {
        background-color: #34495E;
        color: white;
        border-color: #34495E;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.sidebar.write(f"👤 Aktif: **{st.session_state.kullanici}**")
if st.sidebar.button("🚪 Güvenli Çıkış", use_container_width=True):
  st.session_state.kullanici = None
  st.rerun()
st.sidebar.write("---")

menu_options = ["📝 Satış Girişi", "📊 Satışlarım"]
if st.session_state.kullanici in ["SELEN AKCAN", "ALİ OSMAN YELBEY", "DENİZ TELLİ GÜRLEYENDAĞ"]:
    menu_options.extend(["📥 Excel'den Yükle", "💰 Muhasebe Onayı"])
if st.session_state.kullanici in ["ALİ OSMAN YELBEY", "DENİZ TELLİ GÜRLEYENDAĞ"]:
    menu_options.extend(["📊 Performans Raporu", "👥 Personel Yönetimi"])

menu = st.sidebar.radio("Menü", menu_options)
df = load_data()

# --- SOL MENÜ AYLIK FİLTRELEME (Göster Butonlu ve Uyarı Eklenmiş) ---
if menu == "📊 Satışlarım":
    st.sidebar.write("---")
    st.sidebar.subheader("📅 Ay Filtresi")
    aylar = {
        "Tümü": None,
        "Ocak": "01", "Şubat": "02", "Mart": "03", "Nisan": "04",
        "Mayıs": "05", "Haziran": "06", "Temmuz": "07", "Ağustos": "08",
        "Eylül": "09", "Ekim": "10", "Kasım": "11", "Aralık": "12"
    }
    secilen_ay_isim = st.sidebar.selectbox("Ay Seçin", list(aylar.keys()))
    mevcut_yil_str = str(datetime.now().year)
    secilen_yil_input = st.sidebar.text_input("Yıl (Örn: 2026)", value=mevcut_yil_str)
    
    if "aktif_ay" not in st.session_state:
        st.session_state.aktif_ay = "Tümü"
        st.session_state.aktif_ay_kod = None
        st.session_state.aktif_yil = mevcut_yil_str
        st.session_state.filtre_uyari = False

    if st.sidebar.button("🔍 Göster", use_container_width=True):
        st.session_state.aktif_ay = secilen_ay_isim
        st.session_state.aktif_ay_kod = aylar[secilen_ay_isim]
        st.session_state.aktif_yil = secilen_yil_input
        st.session_state.filtre_uyari = True
        st.rerun()

# --- MODÜLLER ---
if menu == "📝 Satış Girişi":
    st.markdown("<h2>📝 Yeni Satış Girişi</h2>", unsafe_allow_html=True)
    with st.form("yeni_satis", clear_on_submit=True):
        c1, c2 = st.columns(2)
        m_adi = c1.text_input("Marka Adı"); ad_soyad = c1.text_input("İsim Soyisim")
        tc = c1.text_input("TC (11 Hane)"); tel = c1.text_input("Telefon")
        st.markdown("<p style='color: white; font-weight: bold; margin-bottom: 0px;'>Doğum Tarihi</p>", unsafe_allow_html=True)
        d1, d2, d3 = st.columns(3)
        gun, ay, yil = d1.selectbox("Gün", range(1, 32)), d2.selectbox("Ay", range(1, 13)), d3.selectbox("Yıl", range(datetime.now().year, 1919, -1))
        il = c2.selectbox("İl", ILLER)
        sinif = c2.multiselect("Sınıf Seçimi", SINIFLAR); odeme = c2.selectbox("Ödeme", ["EFT", "Kredi Kartı"])
        s_tarihi = c2.date_input("Satış Tarihi"); tutar = c2.number_input("Tutar (TL)", min_value=0.0)
        if st.form_submit_button("Satışı Kaydet"):
            new_row = {"ID": str(int(df['ID'].astype(float).max())+1) if not df.empty and 'ID' in df.columns and not df['ID'].isna().all() else "1", 
                       "Marka Adı": m_adi, "Ad Soyad": ad_soyad, "TC": tc, "Telefon": tel, 
                       "Doğum Tarihi": f"{gun:02d}/{ay:02d}/{yil}", "İl": il, "Sınıf": ",".join(sinif), "Ödeme": odeme, 
                       "Satış Tarihi": s_tarihi.strftime("%d/%m/%Y"), "Tutar": str(tutar), 
                       "Durum": "Muhasebe Onayı Bekliyor", "Danışman": st.session_state.kullanici, "Fatura No": ""}
            pd.concat([df, pd.DataFrame([new_row])], ignore_index=True).to_csv(DATA_FILE, index=False)
            st.success("Satış kaydedildi.")

elif menu == "📊 Satışlarım":
    gosterilen_ay = st.session_state.get("aktif_ay", "Tümü")
    gosterilen_ay_kod = st.session_state.get("aktif_ay_kod", None)
    gosterilen_yil = st.session_state.get("aktif_yil", str(datetime.now().year))
    
    if st.session_state.get("filtre_uyari", False):
        st.success(f"✅ {gosterilen_ay} {gosterilen_yil} dönemi satışları başarıyla getirildi.")
        st.session_state.filtre_uyari = False

    st.header(f"📊 {st.session_state.kullanici} - Satışlarım ({gosterilen_ay} {gosterilen_yil})")
    
    # Kullanıcıya ait tüm satışları çek (Durum bağımsız)
    kullanici_df = df[df['Danışman'].astype(str).str.strip().str.upper() == str(st.session_state.kullanici).strip().upper()].copy()
    
    # Ay ve Yıl filtresi uygulama
    if not kullanici_df.empty and 'Satış Tarihi' in kullanici_df.columns:
        def tarih_filtrele(tarih_str):
            try:
                dt = pd.to_datetime(tarih_str, format='%d/%m/%Y', errors='coerce')
                if pd.isna(dt):
                    dt = pd.to_datetime(tarih_str, errors='coerce')
                if pd.isna(dt):
                    return False
                
                ay_eslesir = True if gosterilen_ay_kod is None else (f"{dt.month:02d}" == gosterilen_ay_kod)
                yil_eslesir = True if not gosterilen_yil else (str(dt.year) == str(gosterilen_yil).strip())
                return ay_eslesir and yil_eslesir
            except:
                return False
                
        mask = kullanici_df['Satış Tarihi'].apply(tarih_filtrele)
        kullanici_df = kullanici_df[mask]

    st.dataframe(kullanici_df, use_container_width=True)

elif menu == "📥 Excel'den Yükle":
    st.header("📥 Excel/CSV ile Toplu Satış Girişi (Geçmiş Satışlar)")
    st.info(
        "💡 **İpucu:** Yükleyeceğiniz dosyanın sütun başlıkları şu isimleri içerebilir: "
        "`Marka Adı`, `Ad Soyad`, `TC`, `Telefon`, `Doğum Tarihi`, `İl`, `Sınıf`, `Ödeme`, `Satış Tarihi`, `Tutar`, `Danışman`, `Fatura No`\n\n"
        "ℹ️ *Not: Dosyayı kim yüklerse yüklesin, Excel'deki 'Danışman' / 'Danoşman' sütununda kimin adı yazıyorsa satış o kişinin geçmiş satışlarına işlenecektir.*"
    )
    
    uploaded_file = st.file_uploader("Dosya Seçin", type=["csv", "xlsx"])
    if uploaded_file:
        try:
            if uploaded_file.name.endswith('.csv'):
                try:
                    yeni_data = pd.read_csv(uploaded_file, encoding='utf-8', sep=None, engine='python', dtype=str)
                except Exception:
                    uploaded_file.seek(0)
                    try:
                        yeni_data = pd.read_csv(uploaded_file, encoding='latin-1', sep=None, engine='python', dtype=str)
                    except Exception:
                        uploaded_file.seek(0)
                        yeni_data = pd.read_csv(uploaded_file, encoding='cp1254', sep=None, engine='python', dtype=str)
            else:
                yeni_data = pd.read_excel(uploaded_file, dtype=str)
            
            # Sütun isimlerindeki boşlukları temizleme
            yeni_data.columns = [str(col).strip() for col in yeni_data.columns]
            
            # Yinelenen sütun isimleri varsa benzersizleştirme (manuel)
            cols = pd.Series(yeni_data.columns)
            for dup in cols[cols.duplicated()].unique(): 
                cols[cols == dup] = [dup + '_' + str(i) if i != 0 else dup for i in range(sum(cols == dup))]
            yeni_data.columns = cols

            sutun_duzeltme = {}
            for col in yeni_data.columns:
                col_clean = col.lower()
                if 'yl' in col_clean or 'ýl' in col_clean or col_clean == 'il':
                    sutun_duzeltme[col] = 'İl'
                elif 'sýnýf' in col_clean or 'sınıf' in col_clean or col_clean == 'sinif':
                    sutun_duzeltme[col] = 'Sınıf'
                elif 'marka' in col_clean:
                    sutun_duzeltme[col] = 'Marka Adı'
                elif 'ad soyad' in col_clean or 'isim' in col_clean:
                    sutun_duzeltme[col] = 'Ad Soyad'
                elif 'tutar' in col_clean or 'fiyat' in col_clean:
                    sutun_duzeltme[col] = 'Tutar'
                elif 'tarih' in col_clean and 'satış' in col_clean:
                    sutun_duzeltme[col] = 'Satış Tarihi'
                elif 'danışman' in col_clean or 'danisman' in col_clean or 'danoşman' in col_clean:
                    sutun_duzeltme[col] = 'Danışman'
            
            if sutun_duzeltme:
                yeni_data = yeni_data.rename(columns=sutun_duzeltme)

            st.write("📋 **Önizleme:**", yeni_data.head())
            st.write(f"Toplam Satış Sayısı: **{len(yeni_data)}**")
            
            if st.button("🚀 Tümünü Sisteme Ekle", use_container_width=True):
                # ID atama
                baslangic_id = int(df['ID'].astype(float).max() + 1) if not df.empty and 'ID' in df.columns and not df['ID'].isna().all() else 1
                yeni_data['ID'] = [str(i) for i in range(baslangic_id, baslangic_id + len(yeni_data))]
                
                # Danışman sütunu tespiti ve satırdaki isimlerin atanması
                if 'Danışman' not in yeni_data.columns:
                    yeni_data['Danışman'] = st.session_state.kullanici
                else:
                    yeni_data['Danışman'] = yeni_data['Danışman'].fillna(st.session_state.kullanici)
                    yeni_data['Danışman'] = yeni_data['Danışman'].astype(str).str.strip().str.upper()
                
                if 'Durum' not in yeni_data.columns:
                    yeni_data['Durum'] = 'Tamamlandı'
                
                # Eksik olabilecek standart kolonları doldurma
                for kol in ["Marka Adı", "Ad Soyad", "TC", "Telefon", "Doğum Tarihi", "İl", "Sınıf", "Ödeme", "Satış Tarihi", "Tutar", "Fatura No"]:
                    if kol not in yeni_data.columns:
                        yeni_data[kol] = ""

                # Sadece geçerli ana sütunları dahil etme
                ana_kolonlar = ["ID", "Marka Adı", "Ad Soyad", "TC", "Telefon", "Doğum Tarihi", "İl", "Sınıf", "Ödeme", "Satış Tarihi", "Tutar", "Durum", "Danışman", "Fatura No"]
                yeni_data = yeni_data[[c for c in yeni_data.columns if c in ana_kolonlar]]

                pd.concat([df, yeni_data], ignore_index=True).to_csv(DATA_FILE, index=False)
                st.success("🎉 Tüm geçmiş satışlar Excel'deki danışman isimlerine göre başarıyla sisteme aktarıldı!")
                st.rerun()
        except Exception as e:
            st.error(f"❌ Dosya okuma hatası: {e}")

elif menu == "💰 Muhasebe Onayı":
    st.header("💰 Muhasebe Onay ve Tam Düzenleme Paneli")
    
    # --- Toplu Durum Güncelleme ve Silme Araçları ---
    with st.expander("🛠️ TOPLU İŞLEMLER (Seçilenleri Onayla / Tamamla / Sil)"):
        secenek_idleri = [int(float(x)) for x in df['ID'].dropna().tolist() if str(x).replace('.','',1).isdigit()]
        toplu_secim_idleri = st.multiselect("İşlem Yapılacak Satış ID'lerini Seçin veya Girin", options=secenek_idleri)
        col_t1, col_t2, col_t3 = st.columns(3)
        with col_t1:
            if st.button("✅ Seçilenleri 'Onayla'", use_container_width=True):
                if toplu_secim_idleri:
                    str_ids = [str(i) for i in toplu_secim_idleri]
                    df.loc[df['ID'].astype(str).isin(str_ids), 'Durum'] = "Onaylandı"
                    df.to_csv(DATA_FILE, index=False)
                    st.success("Seçilen kayıtlar Onaylandı!")
                    st.rerun()
                else:
                    st.warning("Lütfen en az bir ID seçin.")
        with col_t2:
            if st.button("🎯 Seçilenleri 'Tamamlandı' Yap", use_container_width=True):
                if toplu_secim_idleri:
                    str_ids = [str(i) for i in toplu_secim_idleri]
                    df.loc[df['ID'].astype(str).isin(str_ids), 'Durum'] = "Tamamlandı"
                    df.to_csv(DATA_FILE, index=False)
                    st.success("Seçilen kayıtlar Tamamlandı!")
                    st.rerun()
                else:
                    st.warning("Lütfen en az bir ID seçin.")
        with col_t3:
            if st.button("❌ Seçilenleri Kalıcı Olarak Sil", use_container_width=True):
                if toplu_secim_idleri:
                    str_ids = [str(i) for i in toplu_secim_idleri]
                    df = df[~df['ID'].astype(str).isin(str_ids)]
                    df.to_csv(DATA_FILE, index=False)
                    st.success("Seçilen kayıtlar silindi!")
                    st.rerun()
                else:
                    st.warning("Lütfen en az bir ID seçin.")

    with st.expander("✏️ TÜM SATIŞ BİLGİLERİNİ TAM DÜZENLE"):
        secili_id = st.number_input("Düzenlenecek Satış ID", step=1)
        secili_id_str = str(int(secili_id))
        if secili_id_str in df['ID'].astype(str).values:
            row = df[df['ID'].astype(str) == secili_id_str].iloc[0]
            with st.form("tam_duzenleme_formu"):
                c1, c2 = st.columns(2)
                v_m = c1.text_input("Marka", value=str(row['Marka Adı']) if pd.notna(row['Marka Adı']) else "")
                v_a = c1.text_input("İsim", value=str(row['Ad Soyad']) if pd.notna(row['Ad Soyad']) else "")
                v_t = c1.text_input("TC", value=str(row['TC']) if pd.notna(row['TC']) else "")
                v_tl = c1.text_input("Tel", value=str(row['Telefon']) if pd.notna(row['Telefon']) else "")
                
                v_d = c2.text_input("Doğum", value=str(row['Doğum Tarihi']) if pd.notna(row['Doğum Tarihi']) else "")
                
                mevcut_il = str(row['İl']).strip() if pd.notna(row['İl']) else ""
                il_index = ILLER.index(mevcut_il) if mevcut_il in ILLER else 0
                v_i = c2.selectbox("İl", ILLER, index=il_index)
                
                mevcut_sinif = str(row['Sınıf']) if pd.notna(row['Sınıf']) and str(row['Sınıf']).lower() != 'nan' else ""
                v_s = c2.text_input("Sınıf", value=mevcut_sinif)
                
                mevcut_odeme = str(row['Ödeme']).strip() if pd.notna(row['Ödeme']) else "EFT"
                odeme_secenekleri = ["EFT", "Kredi Kartı"]
                odeme_index = odeme_secenekleri.index(mevcut_odeme) if mevcut_odeme in odeme_secenekleri else 0
                v_o = c2.selectbox("Ödeme", odeme_secenekleri, index=odeme_index)
                
                try:
                    def_tutar = float(row['Tutar']) if pd.notna(row['Tutar']) and str(row['Tutar']).replace('.','',1).isdigit() else 0.0
                except:
                    def_tutar = 0.0
                v_tu = c2.number_input("Tutar", value=def_tutar)
                
                durum_secenekleri = ["Muhasebe Onayı Bekliyor", "Onaylandı", "Tamamlandı"]
                mevcut_durum = str(row['Durum']).strip() if pd.notna(row['Durum']) else "Muhasebe Onayı Bekliyor"
                durum_index = durum_secenekleri.index(mevcut_durum) if mevcut_durum in durum_secenekleri else 0
                v_du = c1.selectbox("Durum", durum_secenekleri, index=durum_index)
                
                v_f = c2.text_input("Fatura No", value=str(row['Fatura No']) if pd.notna(row['Fatura No']) and str(row['Fatura No']).lower() != 'nan' else "")
                
                if st.form_submit_button("TÜMÜNÜ GÜNCELLE"):
                    idx = df.index[df['ID'].astype(str) == secili_id_str][0]
                    df.at[idx, 'Marka Adı'] = str(v_m)
                    df.at[idx, 'Ad Soyad'] = str(v_a)
                    df.at[idx, 'TC'] = str(v_t)
                    df.at[idx, 'Telefon'] = str(v_tl)
                    df.at[idx, 'Doğum Tarihi'] = str(v_d)
                    df.at[idx, 'İl'] = str(v_i)
                    df.at[idx, 'Sınıf'] = str(v_s)
                    df.at[idx, 'Ödeme'] = str(v_o)
                    df.at[idx, 'Tutar'] = str(v_tu)
                    df.at[idx, 'Durum'] = str(v_du)
                    df.at[idx, 'Fatura No'] = str(v_f)
                    df.to_csv(DATA_FILE, index=False)
                    st.success("Güncellendi!")
                    st.rerun()
                    
    st.write("---")
    st.subheader("📋 Tüm Satış Listesi ve Onay Bekleyenler")
    st.dataframe(df, use_container_width=True)
    
    col_onay1, col_onay2 = st.columns(2)
    with col_onay1:
        for i, row in df[df['Durum'] == "Muhasebe Onayı Bekliyor"].iterrows():
            if st.button(f"✅ Onayla: {row['Marka Adı']} ({row['Tutar']} TL)", key=f"onay_{row['ID']}"):
                df.loc[df['ID'].astype(str) == str(row['ID']), 'Durum'] = "Onaylandı"
                df.to_csv(DATA_FILE, index=False)
                st.success(f"'{row['Marka Adı']}' satış onaylandı!")
                st.rerun()
    with col_onay2:
        for i, row in df[df['Durum'] == "Onaylandı"].iterrows():
            if st.button(f"🎯 Tamamla: {row['Marka Adı']} ({row['Tutar']} TL)", key=f"tamamla_{row['ID']}"):
                df.loc[df['ID'].astype(str) == str(row['ID']), 'Durum'] = "Tamamlandı"
                df.to_csv(DATA_FILE, index=False)
                st.success(f"'{row['Marka Adı']}' satış tamamlandı!")
                st.rerun()

elif menu == "📊 Performans Raporu":
    st.header("📊 Performans")
    temp_df = df.copy()
    temp_df['Tutar'] = pd.to_numeric(temp_df['Tutar'], errors='coerce').fillna(0)
    st.bar_chart(temp_df[temp_df['Durum'] == "Tamamlandı"].groupby('Danışman')['Tutar'].sum())

elif menu == "👥 Personel Yönetimi":
    st.header("👥 Personel ve Veri Yönetimi")
    st.dataframe(pd.read_csv(USER_FILE), use_container_width=True)
    t1, t2, t3 = st.tabs(["➕ Ekle", "🔑 Şifre Değiştir", "❌ Sil"])
    with t1:
        n, s = st.text_input("Personel Adı", key="ekle"), st.text_input("Şifre", type="password", key="sifre")
        if st.button("Ekle"): pd.concat([pd.read_csv(USER_FILE), pd.DataFrame({"İsim": [n], "Şifre": [s]})], ignore_index=True).to_csv(USER_FILE, index=False); st.rerun()
    with t2:
        p = st.selectbox("Personel", pd.read_csv(USER_FILE)["İsim"].tolist(), key="sel"); s2 = st.text_input("Yeni Şifre", type="password", key="new")
        if st.button("Güncelle"): u = pd.read_csv(USER_FILE); u.loc[u["İsim"] == p, "Şifre"] = s2; u.to_csv(USER_FILE, index=False); st.rerun()
    with t3:
        s3 = st.selectbox("Silinecek", pd.read_csv(USER_FILE)["İsim"].tolist(), key="del")
        if st.button("Sil"): u = pd.read_csv(USER_FILE); u[u["İsim"] != s3].to_csv(USER_FILE, index=False); st.rerun()
