import streamlit as st
import pandas as pd
import os
import io
from datetime import datetime, timedelta

# --- SAYFA YAPILANDIRMASI ---
st.set_page_config(page_title="Markanow ERP", layout="wide")

# --- GLOBAL & GİRİŞ CSS & JS STİLLERİ ---
st.markdown(
    """
    <style>
    .stApp {
        background-color: #222222 !important;
    }
    h1, h2, h3, h4, h5, h6, 
    .stTextInput label, 
    .stSelectbox label, 
    .stDateInput label, 
    .stNumberInput label, 
    .stMultiSelect label,
    .stCheckbox label,
    div[data-testid="stMarkdownContainer"] p,
    .stDataFrame {
        color: #FFFFFF !important;
    }
    [data-testid="stSidebar"] {
        background-color: #800000 !important;
    }
    [data-testid="stSidebar"] span, 
    [data-testid="stSidebar"] p, 
    [data-testid="stSidebar"] label, 
    [data-testid="stSidebar"] div {
        color: #FFFFFF !important;
    }
    div[data-testid="stExpander"] details {
        background-color: #007BFF !important;
        border: 1px solid #0056b3 !important;
        border-radius: 4px;
    }
    div[data-testid="stExpander"] details summary p {
        color: #FFFFFF !important;
        font-weight: bold;
    }
    div[data-testid="stExpander"] details summary svg {
        fill: #FFFFFF !important;
    }
    div[data-testid="stExpander"] details[open] {
        background-color: #FFC107 !important;
        border: 1px solid #E0A800 !important;
    }
    div[data-testid="stExpander"] details[open] summary p {
        color: #000000 !important;
        font-weight: bold;
    }
    div[data-testid="stExpander"] details[open] summary svg {
        fill: #000000 !important;
    }
    div.stButton > button, 
    div.stFormSubmitButton > button {
        background-color: #007BFF !important;
        color: #FFFFFF !important;
        border: 1px solid #0056b3 !important;
        font-weight: bold;
        transition: background-color 0.1s ease;
    }
    div.stButton > button:hover,
    div.stButton > button:active,
    div.stButton > button:focus,
    div.stFormSubmitButton > button:hover,
    div.stFormSubmitButton > button:active,
    div.stFormSubmitButton > button:focus {
        background-color: #FFC107 !important;
        color: #000000 !important;
        border: 1px solid #E0A800 !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- TANIMLAMALAR VE VERİ YÜKLEME ---
USER_FILE = "users.csv"
DATA_FILE = "marka_takip.csv"
BACKUP_FILE = "marka_takip_yedek.csv"
HARC_CONFIG_FILE = "harc_config.csv"
EK_HARC_CONFIG_FILE = "ek_harc_config.csv"

ILLER = ["Adana", "Adıyaman", "Afyonkarahisar", "Ağrı", "Aksaray", "Amasya", "Ankara", "Antalya", "Ardahan", "Artvin", "Aydın", "Balıkesir", "Bartın", "Batman", "Bayburt", "Bilecik", "Bingöl", "Bitlis", "Bolu", "Burdur", "Bursa", "Çanakkale", "Çankırı", "Çorum", "Denizli", "Diyarbakır", "Düzce", "Edirne", "Elazığ", "Erzincan", "Erzurum", "Eskişehir", "Gaziantep", "Giresun", "Gümüşhane", "Hakkari", "Hatay", "Iğdır", "Isparta", "İstanbul", "İzmir", "Kahramanmaraş", "Karabük", "Karaman", "Kars", "Kastamonu", "Kayseri", "Kırıkkale", "Kırklareli", "Kırşehir", "Kilis", "Kocaeli", "Konya", "Kütahya", "Malatya", "Manisa", "Mardin", "Mersin", "Muğla", "Muş", "Nevşehir", "Niğde", "Ordu", "Osmaniye", "Rize", "Sakarya", "Samsun", "Siirt", "Sinop", "Sivas", "Şanlıurfa", "Şırnak", "Tekirdağ", "Tokat", "Trabzon", "Tunceli", "Uşak", "Van", "Yalova", "Yozgat", "Zonguldak"]
SINIFLAR = [str(i) for i in range(1, 46)] + [f"35/{i}" for i in range(1, 35)]

if not os.path.exists(USER_FILE):
    pd.DataFrame({
        "İsim": ["ALİ OSMAN YELBEY", "DENİZ TELLİ GÜRLEYENDAĞ", "MERVE YURTLU", "SELEN AKCAN", "ELİF YILDIZ"],
        "Şifre": ["MARKA123", "MARKA123", "MARKA123", "MARKA123", "MARKA123"]
    }).to_csv(USER_FILE, index=False)

def ay_ekle(kaynak_tarih, ay_sayisi=2):
    yil = kaynak_tarih.year + (kaynak_tarih.month + ay_sayisi - 1) // 12
    ay = (kaynak_tarih.month + ay_sayisi - 1) % 12 + 1
    gun = kaynak_tarih.day
    while True:
        try:
            return datetime(yil, ay, gun)
        except ValueError:
            gun -= 1

def resmi_tatil_ve_tatil_kontrol(dt):
    resmi_tatiller = [(1, 1), (23, 4), (1, 5), (19, 5), (15, 7), (30, 8), (29, 10)]
    while True:
        haftanin_gunu = dt.weekday()
        ay_gun = (dt.day, dt.month)
        if haftanin_gunu >= 5:
            dt += timedelta(days=(2 if haftanin_gunu == 5 else 1))
        elif ay_gun in resmi_tatiller:
            dt += timedelta(days=1)
        else:
            break
    return dt

def tarih_birlestir_ve_formatla(tarih_str):
    if not tarih_str: return ""
    temiz = "".join(filter(str.isdigit, str(tarih_str)))
    if len(temiz) == 8:
        return f"{temiz[:2]}/{temiz[2:4]}/{temiz[4:]}"
    return tarih_str.strip()

def veriyi_kaydet_ve_yedekle(df_to_save):
    df_to_save.to_csv(DATA_FILE, index=False, encoding='utf-8-sig')
    try:
        df_to_save.to_csv(BACKUP_FILE, index=False, encoding='utf-8-sig')
    except:
        pass

def load_data():
    zorunlu_kolonlar = [
        "Marka Adı", "Ad Soyad", "TC", "Telefon", "E-Mail", "Doğum Tarihi", "İl", "Sınıf", "Ödeme", 
        "Satış Tarihi", "Tutar", "Durum", "Danışman", "Fatura No", "Fatura Tarihi", 
        "Başvuru No", "Başvuru Tarihi", "Yayın Tarihi", "Yayın Bitiş Tarihi", 
        "Sonraki Aşama Seçimi", "İtiraz Tarihi", "Tescil Tebliğ Tarihi", "Tescil Son Ödeme Tarihi", "Ödeme Tarihi", "Tescil Harç Tutarı"
    ]
    if (not os.path.exists(DATA_FILE) or os.path.getsize(DATA_FILE) == 0) and os.path.exists(BACKUP_FILE) and os.path.getsize(BACKUP_FILE) > 0:
        try:
            d_temp = pd.read_csv(BACKUP_FILE, dtype=str, encoding='utf-8-sig')
            d_temp.to_csv(DATA_FILE, index=False, encoding='utf-8-sig')
        except:
            d_temp = pd.DataFrame(columns=zorunlu_kolonlar)
    elif not os.path.exists(DATA_FILE) or os.path.getsize(DATA_FILE) == 0:
        d_temp = pd.DataFrame(columns=zorunlu_kolonlar)
        veriyi_kaydet_ve_yedekle(d_temp)
    else:
        try:
            d_temp = pd.read_csv(DATA_FILE, dtype=str, encoding='utf-8-sig')
            if d_temp.empty and os.path.exists(BACKUP_FILE) and os.path.getsize(BACKUP_FILE) > 0:
                d_temp = pd.read_csv(BACKUP_FILE, dtype=str, encoding='utf-8-sig')
        except:
            d_temp = pd.DataFrame(columns=zorunlu_kolonlar)
            veriyi_kaydet_ve_yedekle(d_temp)
            
    if "ID" in d_temp.columns:
        d_temp = d_temp.drop(columns=["ID"])
    for col in zorunlu_kolonlar:
        if col not in d_temp.columns: d_temp[col] = ""
    return d_temp

if "sinif_harclari" not in st.session_state:
    st.session_state.sinif_harclari = {}
    if os.path.exists(HARC_CONFIG_FILE) and os.path.getsize(HARC_CONFIG_FILE) > 0:
        try:
            h_df = pd.read_csv(HARC_CONFIG_FILE, encoding='utf-8-sig')
            for _, row in h_df.iterrows():
                st.session_state.sinif_harclari[int(row["Sınıf Adedi"])] = {"harc": float(row["Harç"]), "avukat": float(row["Avukat"])}
        except: pass
    if not st.session_state.sinif_harclari:
        h1, h3 = 2820.0, 3150.0
        h3_hesap = h1 + h1 + h3
        st.session_state.sinif_harclari[1] = {"harc": h1, "avukat": 750.0}
        st.session_state.sinif_harclari[2] = {"harc": h1+h1, "avukat": 750.0}
        st.session_state.sinif_harclari[3] = {"harc": h3_hesap, "avukat": 750.0}
        curr_h = h3_hesap
        for i in range(4, 46):
            curr_h += h3
            st.session_state.sinif_harclari[i] = {"harc": curr_h, "avukat": 750.0}

if "tescil_harc_bedeli" not in st.session_state: st.session_state.tescil_harc_bedeli = 2500.0
if "savunma_harc_bedeli" not in st.session_state: st.session_state.savunma_harc_bedeli = 1500.0
if "bildirim_tescil_tutar" not in st.session_state: st.session_state.bildirim_tescil_tutar = 16000.0
if "kdv_orani" not in st.session_state: st.session_state.kdv_orani = 20.0

if os.path.exists(EK_HARC_CONFIG_FILE) and os.path.getsize(EK_HARC_CONFIG_FILE) > 0:
    try:
        ek_df = pd.read_csv(EK_HARC_CONFIG_FILE, encoding='utf-8-sig')
        if "Tescil Harç Bedeli" in ek_df.columns and not ek_df.empty: st.session_state.tescil_harc_bedeli = float(ek_df.iloc[0]["Tescil Harç Bedeli"])
        if "Savunma Harç Bedeli" in ek_df.columns and not ek_df.empty: st.session_state.savunma_harc_bedeli = float(ek_df.iloc[0]["Savunma Harç Bedeli"])
        if "Bildirim Tescil Tutar" in ek_df.columns and not ek_df.empty: st.session_state.bildirim_tescil_tutar = float(ek_df.iloc[0]["Bildirim Tescil Tutar"])
        if "KDV Oranı" in ek_df.columns and not ek_df.empty: st.session_state.kdv_orani = float(ek_df.iloc[0]["KDV Oranı"])
    except: pass

def sinif_toplam_ucret_hesapla(sinif_str):
    try:
        parcalar = [p.strip() for p in str(sinif_str).split(",") if p.strip()]
        gorulen_ana_siniflar = set()
        for p in parcalar:
            if "/" not in p and p.isdigit():
                s_int = int(p)
                if 1 <= s_int <= 45: gorulen_ana_siniflar.add(s_int)
                else: gorulen_ana_siniflar.add(3)
        adet = max(1, min(len(gorulen_ana_siniflar), 45))
        kayit = st.session_state.sinif_harclari.get(adet, {"harc": 2820.0, "avukat": 750.0})
        return kayit["harc"] + kayit["avukat"]
    except: return 0.0

def sinif_adedi_hesapla(sinif_str):
    try:
        parcalar = [p.strip() for p in str(sinif_str).split(",") if p.strip()]
        gercek_siniflar = set()
        for p in parcalar:
            if "/" not in p and p.isdigit():
                s_int = int(p)
                if 1 <= s_int <= 45: gercek_siniflar.add(s_int)
        return len(gercek_siniflar)
    except: return 0

if "kullanici" not in st.session_state: st.session_state.kullanici = None
query_params = st.query_params
if not st.session_state.kullanici and "user" in query_params: st.session_state.kullanici = query_params["user"]

if not st.session_state.kullanici:
    st.markdown("<h1 style='text-align: center; color: #FFFFFF;'>Markanow Patent Satış Takip ERP</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #FFFFFF;'>Lütfen sisteme giriş yapınız.</p>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        user_df = pd.read_csv(USER_FILE, encoding='utf-8-sig')
        with st.form("giris_formu"):
            secili_kullanici = st.selectbox("Kullanıcı Seçiniz", user_df["İsim"].tolist())
            sifre_input = st.text_input("Şifre", type="password")
            submitted = st.form_submit_button("Giriş Yap", use_container_width=True)
            if submitted:
                dogru_sifre = str(user_df[user_df["İsim"] == secili_kullanici].iloc[0]["Şifre"]).strip()
                if str(sifre_input).strip() == dogru_sifre:
                    st.session_state.kullanici = secili_kullanici
                    st.query_params["user"] = secili_kullanici
                    st.success("Giriş başarılı!")
                    st.rerun()
                else: st.error("❌ Hatalı Şifre!")
    st.stop()

aktif_kullanici_ad = str(st.session_state.kullanici).strip().upper()
is_admin = (aktif_kullanici_ad == "ALİ OSMAN YELBEY")
is_muhasebe = is_admin or (aktif_kullanici_ad in ["DENİZ TELLİ GÜRLEYENDAĞ", "SELEN AKCAN", "ELİF YILDIZ"])

if "aktif_sayfa" not in st.session_state: st.session_state.aktif_sayfa = "Ana Sayfa"

def sayfa_degistir(sayfa_adi):
    st.session_state.aktif_sayfa = sayfa_adi
    st.rerun()

st.sidebar.markdown(f"### 👤 Kullanıcı: {st.session_state.kullanici}")
if is_admin: st.sidebar.markdown("👑 Rol: **Admin**")
elif is_muhasebe: st.sidebar.markdown("💰 Rol: **Muhasebe / Yönetici**")
else: st.sidebar.markdown("💼 Rol: **Danışman**")

if st.sidebar.button("🚪 Güvenli Çıkış", use_container_width=True):
    st.session_state.kullanici = None
    if "user" in st.query_params: del st.query_params["user"]
    st.session_state.aktif_sayfa = "Ana Sayfa"
    st.rerun()

st.sidebar.write("---")
if st.sidebar.button("📝 Yeni Satış Giriş", use_container_width=True): sayfa_degistir("Yeni Satış Giriş")
if st.sidebar.button("📅 Satışlarım (Bu Ay)", use_container_width=True): sayfa_degistir("Satışlarım")
if st.sidebar.button("📊 Genel Satışlarım", use_container_width=True): sayfa_degistir("Genel Satışlarım")

if is_muhasebe:
    if st.sidebar.button("📂 Toplu Excel / Veri Yükleme", use_container_width=True): sayfa_degistir("Toplu Excel Yükleme")
    with st.sidebar.expander("📈 Raporlama", expanded=True):
        if st.button("📊 Genel Rapor Paneli", use_container_width=True): sayfa_degistir("Marka Tescil Raporlama")
        if st.button("📈 Aylık Net Kar / Zarar Raporu", use_container_width=True): sayfa_degistir("Aylık Net Kar / Zarar Raporu")
        if st.button("📌 Muhasebe Bekleyen Raporu", use_container_width=True): sayfa_degistir("Muhasebe Bekleyen Raporu")
        if st.button("⏳ Başvuru Beklemede Raporu", use_container_width=True): sayfa_degistir("Başvuru Beklemede Raporu")
        if st.button("🔍 Kurum İncelemesinde Raporu", use_container_width=True): sayfa_degistir("Kurum İncelemesinde Raporu")
        if st.button("📰 Yayında Raporu", use_container_width=True): sayfa_degistir("Yayında Raporu")
        if st.button("📌 Tescil Tebliğ Beklemede Raporu", use_container_width=True): sayfa_degistir("Tescil Tebliğ Beklemede Raporu")
    with st.sidebar.expander("⚙️ Fiyatlandırma Yönetimi", expanded=True):
        if st.button("💰 Fiyatlandırma ve Harç Yönetimi", use_container_width=True): sayfa_degistir("Fiyatlandırma ve Harç Yönetimi")
    with st.sidebar.expander("📈 Marka Tescil Aşamaları", expanded=True):
        if st.button("📌 Muhasebe Onayı Bekliyor", use_container_width=True): sayfa_degistir("Muhasebe Onayı Bekliyor")
        if st.button("⏳ Başvuru Beklemede", use_container_width=True): sayfa_degistir("Başvuru Beklemede")
        if st.button("🔍 Kurum İncelemesinde", use_container_width=True): sayfa_degistir("Kurum İncelemesinde")
        if st.button("📰 Yayında", use_container_width=True): sayfa_degistir("Yayında")
        if st.button("⚠️ İtiraz / Savunma Bekliyor", use_container_width=True): sayfa_degistir("İtiraz Geldi - Savunma Bekliyor")
        if st.button("📄 Tescil Tebliğ Beklemede", use_container_width=True): sayfa_degistir("Tescil Tebliğ Beklemede")
        if st.button("⚡ Tescil Tebliğ Edildi Müşteri Arandı Ekranı", use_container_width=True): sayfa_degistir("Tescil Tebliğ Edildi Müşteri Arandı Ekranı")
        if st.button("⏳ Tescil Kurum Ödemesi Bekleyen", use_container_width=True): sayfa_degistir("Tescil Kurum Ödemesi Bekleyen")
        if st.button("📞 Ödeme Sözü Verenler", use_container_width=True): sayfa_degistir("Ödeme Sözü Verenler")
        if st.button("📄 Tescil Kuruma Ödendi", use_container_width=True): sayfa_degistir("Tescil Kuruma Ödendi")
        if st.button("🎉 Tescillendi", use_container_width=True): sayfa_degistir("Tescillendi")
        if st.button("❌ Reddedildi", use_container_width=True): sayfa_degistir("Reddedildi")
    if st.sidebar.button("🛠️ Danışman Satışlarını Düzenle", use_container_width=True): sayfa_degistir("Danışman Satışlarını Düzenle")

if is_admin:
    st.sidebar.write("---")
    if st.sidebar.button("👥 Personel Yönetimi", use_container_width=True): sayfa_degistir("Personel Yönetimi")

df = load_data()

if st.session_state.aktif_sayfa == "Ana Sayfa":
    st.markdown(f"<h2>Hoş Geldiniz, {aktif_kullanici_ad}</h2>", unsafe_allow_html=True)
    st.write("Sol taraftaki menüyü kullanarak işlemlerinize başlayabilirsiniz.")

elif is_muhasebe and st.session_state.aktif_sayfa == "Toplu Excel Yükleme":
    if st.button("⬅️ Geri Çık"): sayfa_degistir("Ana Sayfa")
    st.markdown("<h2>📂 Toplu Excel / CSV Veri Yükleme Paneli</h2>", unsafe_allow_html=True)
    st.write("Geçmiş tüm satışlarınızı ve durumlarını tek seferde sisteme yüklemek için aşağıdaki şablonu indirebilir ve Excel'de doldurarak yükleyebilirsiniz.")
    
    ornek_data = {
        "Marka Adı": ["Örnek Marka A", "Örnek Marka B"],
        "Ad Soyad": ["Ahmet Yılmaz", "Ayşe Demir"],
        "TC": ["11111111111", "22222222222"],
        "Telefon": ["05321112233", "05334445566"],
        "E-Mail": ["ahmet@ornek.com", "ayse@ornek.com"],
        "Doğum Tarihi": ["01/01/1990", "05/05/1985"],
        "İl": ["İstanbul", "Ankara"],
        "Sınıf": ["9, 35", "25"],
        "Ödeme": ["EFT", "Kredi Kartı"],
        "Satış Tarihi": ["10/01/2026", "15/02/2026"],
        "Tutar": ["15000", "20000"],
        "Durum": ["Başvuru Beklemede", "Yayında"],
        "Danışman": ["MERVE YURTLU", "SELEN AKCAN"],
        "Fatura No": ["ABC2026000001", "ABC2026000002"],
        "Fatura Tarihi": ["10/01/2026", "15/02/2026"],
        "Başvuru No": ["2026/01234", "2026/05678"],
        "Başvuru Tarihi": ["11/01/2026", "16/02/2026"],
        "Yayın Tarihi": ["", "01/03/2026"],
        "Yayın Bitiş Tarihi": ["", "01/05/2026"],
        "Sonraki Aşama Seçimi": ["", ""],
        "İtiraz Tarihi": ["", ""],
        "Tescil Tebliğ Tarihi": ["", ""],
        "Tescil Son Ödeme Tarihi": ["", ""],
        "Ödeme Tarihi": ["", ""],
        "Tescil Harç Tutarı": ["", ""]
    }
    ornek_df = pd.DataFrame(ornek_data)
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        ornek_df.to_excel(writer, index=False, sheet_name='Satislar')
    excel_data = output.getvalue()

    st.download_button(
        label="📥 Örnek Excel Şablonunu İndir (.xlsx)",
        data=excel_data,
        file_name="markanow_satis_sablonu.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )
    
    st.write("---")
    yuklenen_dosya = st.file_uploader("Doldurduğunuz Excel (.xlsx) veya CSV (.csv) Dosyasını Seçin", type=["csv", "xlsx"])
    
    if yuklenen_dosya is not None:
        try:
            if yuklenen_dosya.name.endswith('.csv'):
                yuklenen_df = pd.read_csv(yuklenen_dosya, dtype=str, encoding='utf-8-sig')
            else:
                yuklenen_df = pd.read_excel(yuklenen_dosya, dtype=str)
                
            st.success(f"✅ Dosya başarıyla okundu! Toplam {len(yuklenen_df)} adet kayıt bulundu.")
            st.dataframe(yuklenen_df.head(), use_container_width=True)
            
            if st.button("🚀 Tüm Kayıtları Sisteme Aktar ve Veritabanını Güncelle", use_container_width=True):
                zorunlu_kolonlar = list(ornek_data.keys())
                for col in zorunlu_kolonlar:
                    if col not in yuklenen_df.columns: yuklenen_df[col] = ""
                yuklenen_df = yuklenen_df[zorunlu_kolonlar].fillna("")
                
                islem_turu = st.radio("İşlem Türü Seçin:", ["Mevcut Verilerin Üstüne Ekle (Append)", "Mevcut Verileri Sil ve Dosyadakileri Yükle (Sıfırdan Kur)"])
                if "Sıfırdan Kur" in islem_turu: final_df = yuklenen_df
                else: final_df = pd.concat([df, yuklenen_df], ignore_index=True)
                
                veriyi_kaydet_ve_yedekle(final_df)
                st.success("🎉 Başarılı! Tüm geçmiş satışlar ve durumlar sisteme aktarıldı.")
                import time; time.sleep(1.5)
                st.session_state.aktif_sayfa = "Ana Sayfa"
                st.rerun()
        except Exception as e:
            st.error(f"❌ Dosya okunurken hata oluştu: {e}")

elif is_muhasebe and st.session_state.aktif_sayfa == "Marka Tescil Raporlama":
    if st.button("⬅️ Geri Çık"): sayfa_degistir("Ana Sayfa")
    st.markdown("<h2>📈 Marka Tescil Aşamaları Raporlama Paneli</h2>", unsafe_allow_html=True)
    rapor_kalemleri = [
        ("Muhasebe Onayı Bekliyor", "Muhasebe Onayı Bekliyor"),
        ("Başvuru Beklemede", "Başvuru Beklemede"),
        ("Kurum İncelemesinde", "Kurum İncelemesinde"),
        ("Yayında", "Yayında"),
        ("İtiraz / Savunma Bekliyor", "İtiraz Geldi - Savunma Bekliyor"),
        ("Tescil Tebliğ Beklemede", "Tescil Tebliğ Beklemede"),
        ("Tescil Tebliğ Edildi Müşteri Arandı", "Tescil Tebliğ Edildi Müşteri Arandı"),
        ("Tescil Kurum Ödemesi Bekleyen", "Tescil Kurum Ödemesi Bekleyen"),
        ("Ödeme Sözü Verenler", "Ödeme Sözü Verenler"),
        ("Tescil Kuruma Ödendi", "Tescil Kuruma Ödendi"),
        ("Tescillendi", "Tescillendi 🎉"),
        ("Reddedildi", "Reddedildi ❌")
    ]
    cols = st.columns(3)
    for idx, (gorunen_isim, durum_kod) in enumerate(rapor_kalemleri):
        adet = len(df[df['Durum'].astype(str).str.strip() == durum_kod])
        with cols[idx % 3]: st.metric(label=gorunen_isim, value=f"{adet} Adet")

elif st.session_state.aktif_sayfa == "Yeni Satış Giriş":
    if st.button("⬅️ Geri Çık"): sayfa_degistir("Ana Sayfa")
    st.markdown("<h2>📝 Yeni Satış Girişi</h2>", unsafe_allow_html=True)
    with st.form("yeni_satis_formu", clear_on_submit=False):
        c1, c2 = st.columns(2)
        m_adi = c1.text_input("Marka Adı")
        ad_soyad = c1.text_input("İsim Soyisim")
        tc = c1.text_input("TC (11 Hane)")
        tel = c1.text_input("Telefon")
        email = c1.text_input("E-Mail")
        c1.text_input("Danışman", value=aktif_kullanici_ad, disabled=True)
        dogru_tarihi_ham = c1.text_input("Doğum Tarihi (GG/AA/YYYY)", value="")
        il = c2.selectbox("İl", ILLER)
        sinif = c2.multiselect("Sınıf Seçimi", SINIFLAR)
        odeme = c2.selectbox("Ödeme Türü", ["EFT", "Kredi Kartı"])
        s_tarihi_ham = c2.text_input("Satış Tarihi (GG/AA/YYYY)", value=datetime.now().strftime("%d/%m/%Y"))
        tutar_input = c2.text_input("Tutar (KDV Dahil, TL)", value="")
        
        submitted = st.form_submit_button("Satışı Kaydet")
        if submitted:
            dogru_tarihi = tarih_birlestir_ve_formatla(dogru_tarihi_ham)
            s_tarihi = tarih_birlestir_ve_formatla(s_tarihi_ham)
            if not m_adi.strip() or not ad_soyad.strip() or not sinif or not tutar_input.strip():
                st.error("❌ Lütfen zorunlu alanları doldurunuz.")
            else:
                new_row = {
                    "Marka Adı": m_adi.strip(), "Ad Soyad": ad_soyad.strip(), "TC": tc.strip(), "Telefon": tel.strip(), "E-Mail": email.strip(),
                    "Doğum Tarihi": dogru_tarihi, "İl": il, "Sınıf": ",".join(sinif), "Ödeme": odeme, 
                    "Satış Tarihi": s_tarihi, "Tutar": tutar_input.strip(), "Durum": "Muhasebe Onayı Bekliyor", 
                    "Danışman": aktif_kullanici_ad, "Fatura No": "", "Fatura Tarihi": "", "Başvuru No": "", "Başvuru Tarihi": "", "Yayın Tarihi": "", "Yayın Bitiş Tarihi": "", "Sonraki Aşama Seçimi": "", "İtiraz Tarihi": "", "Tescil Tebliğ Tarihi": "", "Tescil Son Ödeme Tarihi": "", "Ödeme Tarihi": "", "Tescil Harç Tutarı": ""
                }
                guncel_df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                veriyi_kaydet_ve_yedekle(guncel_df)
                st.success("✅ Satış başarıyla kaydedildi!")
                import time; time.sleep(1.5)
                st.session_state.aktif_sayfa = "Ana Sayfa"
                st.rerun()

elif st.session_state.aktif_sayfa == "Satışlarım":
    if st.button("⬅️ Geri Çık"): sayfa_degistir("Ana Sayfa")
    st.markdown("<h2>📅 Satışlarım</h2>", unsafe_allow_html=True)
    st.dataframe(df, use_container_width=True)

elif is_admin and st.session_state.aktif_sayfa == "Personel Yönetimi":
    if st.button("⬅️ Geri Çık"): sayfa_degistir("Ana Sayfa")
    st.markdown("<h2>👥 Personel ve Danışman Yönetimi</h2>", unsafe_allow_html=True)
    if os.path.exists(USER_FILE): st.dataframe(pd.read_csv(USER_FILE, encoding='utf-8-sig'), use_container_width=True)
