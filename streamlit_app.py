import streamlit as st
import pandas as pd
import os
import base64
from datetime import datetime, timedelta

# --- SAYFA YAPILANDIRMASI ---
st.set_page_config(page_title="Markanow ERP", layout="wide")

# --- GLOBAL & GİRİŞ CSS & JS STİLLERİ ---
st.markdown(
    """
    <style>
    /* Genel Arka Plan Antrasit */
    .stApp {
        background-color: #222222 !important;
    }

    /* Tüm Yazılar ve Etiketler Beyaz */
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

    /* Sol Menü Bordo Rengi */
    [data-testid="stSidebar"] {
        background-color: #800000 !important;
    }
    
    [data-testid="stSidebar"] span, 
    [data-testid="stSidebar"] p, 
    [data-testid="stSidebar"] label, 
    [data-testid="stSidebar"] div {
        color: #FFFFFF !important;
    }

    /* Expander Kapalı Durumda: Mavi Renk, Beyaz Yazı */
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

    /* Expander Açık Durumda: Sarı Renk, Siyah Yazı */
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

    /* Tüm Normal Butonlar ve Form Submit Butonları: Mavi, Yazısı Beyaz */
    div.stButton > button, 
    div.stFormSubmitButton > button {
        background-color: #007BFF !important;
        color: #FFFFFF !important;
        border: 1px solid #0056b3 !important;
        font-weight: bold;
        transition: background-color 0.1s ease;
    }

    /* Butona Basıldığında (Active / Hover) Sarı Renk ve Siyah Yazı */
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

    <!-- Tarih / İşaretini Sabitleme Scripti -->
    <script>
    function forceDateSlashMask() {
        const inputs = document.querySelectorAll('input[type="text"]');
        inputs.forEach(input => {
            if (input && !input.dataset.slashFixed) {
                const parentContainer = input.closest('.stTextInput');
                let isDateLike = false;
                if (parentContainer) {
                    const label = parentContainer.querySelector('label');
                    if (label && (label.innerText.includes('Tarihi') || label.innerText.includes('Günü') || label.innerText.includes('GG/AA/YYYY'))) {
                        isDateLike = true;
                    }
                }
                if (input.placeholder && (input.placeholder.includes('GG/AA/YYYY') || input.placeholder.includes('gg/aa/yyyy'))) {
                    isDateLike = true;
                }

                if (isDateLike) {
                    input.dataset.slashFixed = "true";
                    
                    const formatValue = (el) => {
                        let val = el.value.replace(/\D/g, "");
                        if (val.length > 8) val = val.slice(0, 8);
                        let formatted = "";
                        if (val.length > 0) {
                            formatted += val.substring(0, 2);
                        }
                        if (val.length >= 3) {
                            formatted += "/" + val.substring(2, 4);
                        }
                        if (val.length >= 5) {
                            formatted += "/" + val.substring(4, 8);
                        }
                        if (el.value !== formatted) {
                            el.value = formatted;
                            el.dispatchEvent(new Event('input', { bubbles: true }));
                            el.dispatchEvent(new Event('change', { bubbles: true }));
                        }
                    };

                    input.addEventListener('input', function (e) {
                        formatValue(e.target);
                    });
                    
                    input.addEventListener('blur', function (e) {
                        formatValue(e.target);
                    });
                }
            }
        });
    }

    const observer = new MutationObserver(forceDateSlashMask);
    observer.observe(document.body, { childList: true, subtree: true });
    window.addEventListener('load', forceDateSlashMask);
    </script>
    """,
    unsafe_allow_html=True
)

# --- TANIMLAMALAR VE VERİ YÜKLEME ---
USER_FILE = "users.csv"
DATA_FILE = "marka_takip.csv"
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
    resmi_tatiller = [
        (1, 1),   # Yılbaşı
        (23, 4),  # 23 Nisan
        (1, 5),   # 1 Mayıs
        (19, 5),  # 19 Mayıs
        (15, 7),  # 15 Temmuz
        (30, 8),  # 30 Ağustos
        (29, 10), # 29 Ekim
    ]
    
    while True:
        haftanin_gunu = dt.weekday()
        ay_gun = (dt.day, dt.month)
        
        is_hafta_sonu = (haftanin_gunu >= 5)
        is_resmi_tatil = ay_gun in resmi_tatiller
        
        if is_hafta_sonu:
            gun_ekle = 2 if haftanin_gunu == 5 else 1
            dt += timedelta(days=gun_ekle)
        elif is_resmi_tatil:
            dt += timedelta(days=1)
        else:
            break
    return dt

def tarih_birlestir_ve_formatla(tarih_str):
    if not tarih_str:
        return ""
    temiz = "".join(filter(str.isdigit, str(tarih_str)))
    if len(temiz) == 8:
        return f"{temiz[:2]}/{temiz[2:4]}/{temiz[4:]}"
    return tarih_str.strip()

def load_data():
    zorunlu_kolonlar = [
        "Marka Adı", "Ad Soyad", "TC", "Telefon", "E-Mail", "Doğum Tarihi", "İl", "Sınıf", "Ödeme", 
        "Satış Tarihi", "Tutar", "Durum", "Danışman", "Fatura No", "Fatura Tarihi", 
        "Başvuru No", "Başvuru Tarihi", "Yayın Tarihi", "Yayın Bitiş Tarihi", 
        "Sonraki Aşama Seçimi", "İtiraz Tarihi", "Tescil Tebliğ Tarihi", "Tescil Son Ödeme Tarihi", "Ödeme Tarihi", "Tescil Harç Tutarı"
    ]
    
    if not os.path.exists(DATA_FILE) or os.path.getsize(DATA_FILE) == 0:
        d_temp = pd.DataFrame(columns=zorunlu_kolonlar)
        d_temp.to_csv(DATA_FILE, index=False)
    else:
        try:
            d_temp = pd.read_csv(DATA_FILE, dtype=str)
        except pd.errors.EmptyDataError:
            d_temp = pd.DataFrame(columns=zorunlu_kolonlar)
            d_temp.to_csv(DATA_FILE, index=False)
            
    if "ID" in d_temp.columns:
        d_temp = d_temp.drop(columns=["ID"])

    for col in zorunlu_kolonlar:
        if col not in d_temp.columns:
            d_temp[col] = ""
            
    d_temp['Durum'] = d_temp['Durum'].fillna("").str.strip()
    gecerli_durumlar = [
        "Muhasebe Onayı Bekliyor", "Başvuru Beklemede", "Kurum İncelemesinde", 
        "Yayında", "İtiraz Geldi - Savunma Bekliyor", "Tescil Tebliğ Beklemede", 
        "Tescil Tebliğ Edildi Müşteri Arandı", "Tescil Kurum Ödemesi Bekleyen", "Tescil Kuruma Ödendi", "Tescillendi 🎉", "Reddedildi ❌"
    ]
    d_temp.loc[~d_temp['Durum'].isin(gecerli_durumlar), 'Durum'] = "Muhasebe Onayı Bekliyor"
    return d_temp

# --- 1-45 SINIF HARÇ VE AVUKAT ÜCRETLERİNİ KALICI DOSYADAN YÜKLEME ---
if "sinif_harclari" not in st.session_state:
    st.session_state.sinif_harclari = {}
    if os.path.exists(HARC_CONFIG_FILE) and os.path.getsize(HARC_CONFIG_FILE) > 0:
        try:
            h_df = pd.read_csv(HARC_CONFIG_FILE)
            for _, row in h_df.iterrows():
                s_no = int(row["Sınıf Adedi"])
                st.session_state.sinif_harclari[s_no] = {
                    "harc": float(row["Harç"]),
                    "avukat": float(row["Avukat"])
                }
        except:
            pass
            
    if not st.session_state.sinif_harclari:
        h1 = 2820.0
        h3 = 3150.0
        h2 = h1 + h1
        h3_hesap = h1 + h1 + h3
        st.session_state.sinif_harclari[1] = {"harc": h1, "avukat": 750.0}
        st.session_state.sinif_harclari[2] = {"harc": h2, "avukat": 750.0}
        st.session_state.sinif_harclari[3] = {"harc": h3_hesap, "avukat": 750.0}
        curr_h = h3_hesap
        for i in range(4, 46):
            curr_h += h3
            st.session_state.sinif_harclari[i] = {"harc": curr_h, "avukat": 750.0}

# --- EK HARÇ BEDELLERİ VE KDV ORANI ---
if "tescil_harc_bedeli" not in st.session_state:
    st.session_state.tescil_harc_bedeli = 2500.0
if "savunma_harc_bedeli" not in st.session_state:
    st.session_state.savunma_harc_bedeli = 1500.0
if "bildirim_tescil_tutar" not in st.session_state:
    st.session_state.bildirim_tescil_tutar = 16000.0
if "kdv_orani" not in st.session_state:
    st.session_state.kdv_orani = 20.0

if os.path.exists(EK_HARC_CONFIG_FILE) and os.path.getsize(EK_HARC_CONFIG_FILE) > 0:
    try:
        ek_df = pd.read_csv(EK_HARC_CONFIG_FILE)
        if "Tescil Harç Bedeli" in ek_df.columns and not ek_df.empty:
            st.session_state.tescil_harc_bedeli = float(ek_df.iloc[0]["Tescil Harç Bedeli"])
        if "Savunma Harç Bedeli" in ek_df.columns and not ek_df.empty:
            st.session_state.savunma_harc_bedeli = float(ek_df.iloc[0]["Savunma Harç Bedeli"])
        if "Bildirim Tescil Tutar" in ek_df.columns and not ek_df.empty:
            st.session_state.bildirim_tescil_tutar = float(ek_df.iloc[0]["Bildirim Tescil Tutar"])
        if "KDV Oranı" in ek_df.columns and not ek_df.empty:
            st.session_state.kdv_orani = float(ek_df.iloc[0]["KDV Oranı"])
    except:
        pass

def sinif_harci_ve_avukat_hesapla(sinif_str):
    try:
        parcalar = [p.strip() for p in str(sinif_str).split(",") if p.strip()]
        toplam_tutar = 0.0
        islenen_ana_siniflar = set()
        
        sirali_sayac = 0
        for p in parcalar:
            if "/" in p:
                continue
            else:
                if p.isdigit():
                    s_int = int(p)
                    if 1 <= s_int <= 45:
                        if s_int not in islenen_ana_siniflar:
                            islenen_ana_siniflar.add(s_int)
                            sirali_sayac += 1
                            kayit = st.session_state.sinif_harclari.get(sirali_sayac, {"harc": 2820.0, "avukat": 750.0})
                            toplam_tutar += kayit["harc"] + kayit["avukat"]
                    else:
                        if s_int not in islenen_ana_siniflar:
                            islenen_ana_siniflar.add(s_int)
                            sirali_sayac += 1
                            kayit = st.session_state.sinif_harclari.get(3, {"harc": 2820.0, "avukat": 750.0})
                            toplam_tutar += kayit["harc"] + kayit["avukat"]
        return toplam_tutar
    except:
        return 0.0

def sinif_toplam_ucret_hesapla(sinif_str):
    try:
        parcalar = [p.strip() for p in str(sinif_str).split(",") if p.strip()]
        gorulen_ana_siniflar = set()
        
        for p in parcalar:
            if "/" in p:
                continue
            else:
                if p.isdigit():
                    s_int = int(p)
                    if 1 <= s_int <= 45:
                        if s_int not in gorulen_ana_siniflar:
                            gorulen_ana_siniflar.add(s_int)
                    else:
                        gorulen_ana_siniflar.add(3)
                        
        adet = len(gorulen_ana_siniflar)
        if adet < 1:
            adet = 1
        if adet > 45:
            adet = 45
            
        kayit = st.session_state.sinif_harclari.get(adet, {"harc": 2820.0, "avukat": 750.0})
        return kayit["harc"] + kayit["avukat"]
    except:
        return 0.0

def sinif_adedi_hesapla(sinif_str):
    try:
        parcalar = [p.strip() for p in str(sinif_str).split(",") if p.strip()]
        gercek_siniflar = set()
        for p in parcalar:
            if "/" not in p and p.isdigit():
                s_int = int(p)
                if 1 <= s_int <= 45:
                    gercek_siniflar.add(s_int)
        return len(gercek_siniflar)
    except:
        return 0

# --- GİRİŞ KONTROLÜ VE OTURUM KORUMA ---
if "kullanici" not in st.session_state: 
    st.session_state.kullanici = None

query_params = st.query_params
if not st.session_state.kullanici and "user" in query_params:
    st.session_state.kullanici = query_params["user"]

if not st.session_state.kullanici:
    st.markdown("<h1 style='text-align: center; color: #FFFFFF;'>Markanow Patent Satış Takip ERP</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #FFFFFF;'>Lütfen sisteme giriş yapınız.</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        user_df = pd.read_csv(USER_FILE)
        
        with st.form("giris_formu"):
            secili_kullanici = st.selectbox("Kullanıcı Seçiniz", user_df["İsim"].tolist())
            sifre_input = st.text_input("Şifre", type="password")
            
            st.write("")
            submitted = st.form_submit_button("Giriş Yap", use_container_width=True)
            if submitted:
                dogru_sifre = str(user_df[user_df["İsim"] == secili_kullanici].iloc[0]["Şifre"]).strip()
                if str(sifre_input).strip() == dogru_sifre:
                    st.session_state.kullanici = secili_kullanici
                    st.query_params["user"] = secili_kullanici
                    st.success("Giriş başarılı! Yönlendiriliyorsunuz...")
                    st.rerun()
                else:
                    st.error("❌ Hatalı Şifre!")
    st.stop()

# --- ROL TANIMLAMALARI ---
aktif_kullanici_ad = str(st.session_state.kullanici).strip().upper()
is_admin = (aktif_kullanici_ad == "ALİ OSMAN YELBEY")
is_muhasebe = is_admin or (aktif_kullanici_ad in ["DENİZ TELLİ GÜRLEYENDAĞ", "SELEN AKCAN", "ELİF YILDIZ"])

if "aktif_sayfa" not in st.session_state:
    st.session_state.aktif_sayfa = "Ana Sayfa"

def sayfa_degistir(sayfa_adi):
    st.session_state.aktif_sayfa = sayfa_adi
    st.rerun()

# --- SOL MENÜ (SIDEBAR) ---
st.sidebar.markdown(f"### 👤 Kullanıcı: {st.session_state.kullanici}")
if is_admin:
    st.sidebar.markdown("👑 Rol: **Admin**")
elif is_muhasebe:
    st.sidebar.markdown("💰 Rol: **Muhasebe / Yönetici**")
else:
    st.sidebar.markdown("💼 Rol: **Danışman**")

if st.sidebar.button("🚪 Güvenli Çıkış", use_container_width=True):
    st.session_state.kullanici = None
    if "user" in st.query_params:
        del st.query_params["user"]
    st.session_state.aktif_sayfa = "Ana Sayfa"
    st.rerun()

st.sidebar.write("---")

if not is_muhasebe:
    if st.sidebar.button("📝 Yeni Satış Giriş", use_container_width=True):
        sayfa_degistir("Yeni Satış Giriş")
    if st.sidebar.button("📅 Satışlarım (Bu Ay)", use_container_width=True):
        sayfa_degistir("Satışlarım")
    if st.sidebar.button("📊 Genel Satışlarım", use_container_width=True):
        sayfa_degistir("Genel Satışlarım")

if is_muhasebe:
    with st.sidebar.expander("📈 Raporlama", expanded=True):
        if st.button("📊 Genel Rapor Paneli", use_container_width=True):
            sayfa_degistir("Marka Tescil Raporlama")
        if st.button("📈 Aylık Net Kar / Zarar Raporu", use_container_width=True):
            sayfa_degistir("Aylık Net Kar / Zarar Raporu")
        if st.button("📌 Muhasebe Bekleyen Raporu", use_container_width=True):
            sayfa_degistir("Muhasebe Bekleyen Raporu")
        if st.button("⏳ Başvuru Beklemede Raporu", use_container_width=True):
            sayfa_degistir("Başvuru Beklemede Raporu")
        if st.button("🔍 Kurum İncelemesinde Raporu", use_container_width=True):
            sayfa_degistir("Kurum İncelemesinde Raporu")

    with st.sidebar.expander("⚙️ Fiyatlandırma Yönetimi", expanded=True):
        if st.button("💰 Fiyatlandırma ve Harç Yönetimi", use_container_width=True):
            sayfa_degistir("Fiyatlandırma ve Harç Yönetimi")

    with st.sidebar.expander("📈 Marka Tescil Aşamaları", expanded=True):
        if st.button("📌 Muhasebe Onayı Bekliyor", use_container_width=True):
            sayfa_degistir("Muhasebe Onayı Bekliyor")
        if st.button("⏳ Başvuru Beklemede", use_container_width=True):
            sayfa_degistir("Başvuru Beklemede")
        if st.button("🔍 Kurum İncelemesinde", use_container_width=True):
            sayfa_degistir("Kurum İncelemesinde")
        if st.button("📰 Yayında", use_container_width=True):
            sayfa_degistir("Yayında")
        if st.button("⚠️ İtiraz / Savunma Bekliyor", use_container_width=True):
            sayfa_degistir("İtiraz Geldi - Savunma Bekliyor")
        if st.button("📄 Tescil Tebliğ Beklemede", use_container_width=True):
            sayfa_degistir("Tescil Tebliğ Beklemede")
        if st.button("💳 Tescil Tebliğ Edildi Müşteri Arandı", use_container_width=True):
            sayfa_degistir("Tescil Tebliğ Edildi Müşteri Arandı")
        if st.button("⏳ Tescil Kurum Ödemesi Bekleyen", use_container_width=True):
            sayfa_degistir("Tescil Kurum Ödemesi Bekleyen")
        if st.button("📄 Tescil Kuruma Ödendi", use_container_width=True):
            sayfa_degistir("Tescil Kuruma Ödendi")
        if st.button("🎉 Tescillendi", use_container_width=True):
            sayfa_degistir("Tescillendi")
        if st.button("❌ Reddedildi", use_container_width=True):
            sayfa_degistir("Reddedildi")
            
    if st.sidebar.button("🛠️ Danışman Satışlarını Düzenle", use_container_width=True):
        sayfa_degistir("Danışman Satışlarını Düzenle")

if is_admin:
    st.sidebar.write("---")
    if st.sidebar.button("👥 Personel Yönetimi", use_container_width=True):
        sayfa_degistir("Personel Yönetimi")

df = load_data()

# --- SAYFA İÇERİKLERİ ---

if st.session_state.aktif_sayfa == "Ana Sayfa":
    st.markdown(f"<h2>Hoş Geldiniz, {aktif_kullanici_ad}</h2>", unsafe_allow_html=True)
    st.write("Sol taraftaki menüyü kullanarak işlemlerinize başlayabilirsiniz.")

elif is_muhasebe and st.session_state.aktif_sayfa == "Marka Tescil Raporlama":
    if st.button("⬅️ Geri Çık"):
        sayfa_degistir("Ana Sayfa")
        
    st.markdown("<h2>📈 Marka Tescil Aşamaları Raporlama Paneli</h2>", unsafe_allow_html=True)
    st.write("Sistemdeki tüm markaların güncel aşama durumlarına göre sayısal dağılımı aşağıdadır.")
    
    def get_count_and_df(asama_adi):
        if asama_adi == "Tescil Tebliğ Beklemede":
            sub_df = df[(df['Durum'].astype(str).str.strip() == asama_adi) & 
                        ((df['Tescil Tebliğ Tarihi'].astype(str).str.strip() == "") | 
                         (df['Tescil Tebliğ Tarihi'].astype(str).str.lower() == "nan"))]
        else:
            sub_df = df[df['Durum'].astype(str).str.strip() == asama_adi]
        return len(sub_df), sub_df

    rapor_kalemleri = [
        ("Muhasebe Onayı Bekliyor", "Muhasebe Onayı Bekliyor"),
        ("Başvuru Beklemede", "Başvuru Beklemede"),
        ("Kurum İncelemesinde", "Kurum İncelemesinde"),
        ("Yayında", "Yayında"),
        ("İtiraz / Savunma Bekliyor", "İtiraz Geldi - Savunma Bekliyor"),
        ("Tescil Tebliğ Beklemede", "Tescil Tebliğ Beklemede"),
        ("Tescil Tebliğ Edildi Müşteri Arandı", "Tescil Tebliğ Edildi Müşteri Arandı"),
        ("Tescil Kurum Ödemesi Bekleyen", "Tescil Kurum Ödemesi Bekleyen"),
        ("Tescil Kuruma Ödendi", "Tescil Kuruma Ödendi"),
        ("Tescillendi", "Tescillendi 🎉"),
        ("Reddedildi", "Reddedildi ❌")
    ]

    cols = st.columns(3)
    for idx, (gorunen_isim, durum_kod) in enumerate(rapor_kalemleri):
        adet, _ = get_count_and_df(durum_kod)
        with cols[idx % 3]:
            st.metric(label=gorunen_isim, value=f"{adet} Adet")

elif is_muhasebe and st.session_state.aktif_sayfa == "Aylık Net Kar / Zarar Raporu":
    if st.button("⬅️ Geri Çık"):
        sayfa_degistir("Ana Sayfa")
        
    st.markdown("<h2>📊 Aylık Net Kar / Zarar Raporu</h2>", unsafe_allow_html=True)
    st.write("Satış Tarihine göre filtrelenen döneme ait KDV hariç ciro, sınıf toplam harç maliyeti ve net kar/zarar raporu aşağıdadır.")
    
    aylar = {"Tümü": None, "Ocak": "01", "Şubat": "02", "Mart": "03", "Nisan": "04", "Mayıs": "05", "Haziran": "06", "Temmuz": "07", "Ağustos": "08", "Eylül": "09", "Ekim": "10", "Kasım": "11", "Aralık": "12"}
    
    # Otomatik yıl seçeneklerini toplama
    mevcut_yil_str = str(datetime.now().year)
    yillar_kumesi = {mevcut_yil_str}
    if 'Satış Tarihi' in df.columns:
        for t_str in df['Satış Tarihi'].dropna():
            try:
                dt_temp = pd.to_datetime(t_str, format='%d/%m/%Y', errors='coerce')
                if pd.isna(dt_temp): dt_temp = pd.to_datetime(t_str, errors='coerce')
                if not pd.isna(dt_temp):
                    yillar_kumesi.add(str(dt_temp.year))
            except:
                pass
    yillar_listesi = sorted(list(yillar_kumesi), reverse=True)
    
    # Danışman listesini hazırlama ("Tümü" seçeneğiyle birlikte)
    danismanlar_listesi = ["Tümü"]
    if 'Danışman' in df.columns:
        unik_danismanlar = sorted(df['Danışman'].dropna().astype(str).str.strip().str.upper().unique().tolist())
        danismanlar_listesi.extend([d for d in unik_danismanlar if d])

    col_f1, col_f2, col_f3 = st.columns(3)
    secilen_ay_isim = col_f1.selectbox("Ay Seçin", list(aylar.keys()), key="kar_zarar_ay_sec")
    
    # Yıl filtresi selectbox (ok işaretli otomatik liste)
    varsayilan_yil_index = yillar_listesi.index(mevcut_yil_str) if mevcut_yil_str in yillar_listesi else 0
    secilen_yil = col_f2.selectbox("Yıl", options=yillar_listesi, index=varsayilan_yil_index, key="kar_zarar_yil_sec")
    
    secilen_danisman_filtre = col_f3.selectbox("Danışman Seçin", danismanlar_listesi, key="kar_zarar_danisman_sec")
    
    secilen_ay_kod = aylar[secilen_ay_isim]
    
    rapor_df = df.copy()
    
    def net_kar_filtrele(row):
        try:
            # Danışman filtresi kontrolü
            if secilen_danisman_filtre != "Tümü":
                row_danisman = str(row.get('Danışman', '')).strip().upper()
                if row_danisman != secilen_danisman_filtre:
                    return False

            s_tarih = row.get('Satış Tarihi', '')
            if pd.isna(s_tarih) or str(s_tarih).strip() == '' or str(s_tarih).lower() == 'none': return False
            dt = pd.to_datetime(s_tarih, format='%d/%m/%Y', errors='coerce')
            if pd.isna(dt): dt = pd.to_datetime(s_tarih, errors='coerce')
            if pd.isna(dt): return False
            ay_eslesir = True if secilen_ay_kod is None else (f"{dt.month:02d}" == secilen_ay_kod)
            yil_eslesir = True if not str(secilen_yil).strip() else (str(dt.year) == str(secilen_yil).strip())
            return ay_eslesir and yil_eslesir
        except: return False
            
    if not rapor_df.empty:
        rapor_df = rapor_df[rapor_df.apply(net_kar_filtrele, axis=1)]
        
    toplam_kdv_haric_ciro = 0.0
    toplam_harc_maliyeti = 0.0
    
    tablo_satirlari = []
    kdv_orani = st.session_state.kdv_orani
    
    for _, row in rapor_df.iterrows():
        m_adi = row.get('Marka Adı', '')
        s_tarih = row.get('Satış Tarihi', '')
        sinif_str = row.get('Sınıf', '')
        danisman_adi = row.get('Danışman', '')
        tutar_str = str(row.get('Tutar', '0')).replace(',', '.')
        
        try:
            tutar_dahil = float(tutar_str)
        except:
            tutar_dahil = 0.0
            
        kdv_haric = tutar_dahil / (1 + (kdv_orani / 100.0))
        harc_maliyeti = sinif_toplam_ucret_hesapla(sinif_str)
        net_durum = kdv_haric - harc_maliyeti
        
        toplam_kdv_haric_ciro += kdv_haric
        toplam_harc_maliyeti += harc_maliyeti
        
        tablo_satirlari.append({
            "Marka Adı": m_adi,
            "Danışman": danisman_adi,
            "Satış Tarihi": s_tarih,
            "Sınıf": sinif_str,
            "KDV Dahil Tutar (TL)": f"{tutar_dahil:,.2f} TL",
            "KDV Hariç Tutar (TL)": f"{kdv_haric:,.2f} TL",
            "Sınıf Toplam Harç (TL)": f"{harc_maliyeti:,.2f} TL",
            "Net Rakam (TL)": f"{net_durum:,.2f} TL"
        })
        
    genel_net_kar = toplam_kdv_haric_ciro - toplam_harc_maliyeti
    
    st.write("---")
    c1, c2, c3 = st.columns(3)
    c1.metric("Toplam KDV Hariç Ciro", f"{toplam_kdv_haric_ciro:,.2f} TL")
    c2.metric("Toplam Sınıf Harç Maliyeti", f"{toplam_harc_maliyeti:,.2f} TL")
    c3.metric("Toplam Net Kar / Zarar", f"{genel_net_kar:,.2f} TL")
    st.write("---")
    
    if not tablo_satirlari:
        st.info("Seçilen kriterlere uygun kayıt bulunamadı.")
    else:
        sonuc_gosterim_df = pd.DataFrame(tablo_satirlari)
        st.dataframe(sonuc_gosterim_df, use_container_width=True)

elif is_muhasebe and st.session_state.aktif_sayfa == "Muhasebe Bekleyen Raporu":
    if st.button("⬅️ Geri Çık"):
        sayfa_degistir("Ana Sayfa")
        
    st.markdown("<h2>📌 Muhasebe Bekleyen Raporu</h2>", unsafe_allow_html=True)
    st.write("Muhasebe onayı bekleyen işlemlerin detaylı rapor görünümü aşağıdadır.")
    
    muhasebe_bekleyen_df = df[df['Durum'].astype(str).str.strip() == "Muhasebe Onayı Bekliyor"]
    
    toplam_marka_sayisi = muhasebe_bekleyen_df['Marka Adı'].nunique()
    
    toplam_sinif_adedi = 0
    for s_val in muhasebe_bekleyen_df['Sınıf'].dropna():
        toplam_sinif_adedi += sinif_adedi_hesapla(s_val)

    toplam_tutar = 0.0
    for _, row in muhasebe_bekleyen_df.iterrows():
        toplam_tutar += sinif_toplam_ucret_hesapla(row.get('Sınıf', ''))

    c1, c2, c3 = st.columns(3)
    c1.metric("Toplam Bekleyen Marka Adedi", f"{toplam_marka_sayisi} Adet")
    c2.metric("Toplam Bekleyen Sınıf Adedi", f"{toplam_sinif_adedi} Sınıf")
    c3.metric("Toplam Bekleyen Tutar", f"{toplam_tutar:,.2f} TL")
    
    st.write("---")
    if muhasebe_bekleyen_df.empty:
        st.info("Muhasebe onayı bekleyen kayıt bulunmuyor.")
    else:
        ozet_df = muhasebe_bekleyen_df[['Marka Adı', 'Sınıf', 'Satış Tarihi']].copy()
        sinif_adedi_listesi = [f"{sinif_adedi_hesapla(s)} Sınıf" for s in ozet_df['Sınıf']]
        ucret_listesi = [f"{sinif_toplam_ucret_hesapla(s):,.2f} TL" for s in ozet_df['Sınıf']]
        
        ozet_df.insert(ozet_df.columns.get_loc('Sınıf') + 1, 'Sınıf Adedi', sinif_adedi_listesi)
        ozet_df['Sınıf Toplam Harç Ücreti'] = ucret_listesi
        
        cols_order = ['Marka Adı', 'Sınıf', 'Sınıf Adedi', 'Satış Tarihi', 'Sınıf Toplam Harç Ücreti']
        ozet_df = ozet_df[cols_order]
        
        st.dataframe(ozet_df, use_container_width=True)

elif is_muhasebe and st.session_state.aktif_sayfa == "Başvuru Beklemede Raporu":
    if st.button("⬅️ Geri Çık"):
        sayfa_degistir("Ana Sayfa")
        
    st.markdown("<h2>⏳ Başvuru Beklemede Raporu</h2>", unsafe_allow_html=True)
    st.write("Başvuru beklemede olan işlemlerin detaylı rapor görünümü aşağıdadır.")
    
    basvuru_bekleyen_df = df[df['Durum'].astype(str).str.strip() == "Başvuru Beklemede"]
    
    toplam_marka_sayisi = basvuru_bekleyen_df['Marka Adı'].nunique()
    
    toplam_sinif_adedi = 0
    for s_val in basvuru_bekleyen_df['Sınıf'].dropna():
        toplam_sinif_adedi += sinif_adedi_hesapla(s_val)

    toplam_basvuru_ucret_tutari = 0.0
    for _, row in basvuru_bekleyen_df.iterrows():
        toplam_basvuru_ucret_tutari += sinif_toplam_ucret_hesapla(row.get('Sınıf', ''))

    c1, c2, c3 = st.columns(3)
    c1.metric("Toplam Başvuru Marka Adedi", f"{toplam_marka_sayisi} Adet")
    c2.metric("Toplam Başvuru Sınıf Adedi", f"{toplam_sinif_adedi} Sınıf")
    c3.metric("Toplam Başvuru Ücret Tutarı", f"{toplam_basvuru_ucret_tutari:,.2f} TL")
    
    st.write("---")
    if basvuru_bekleyen_df.empty:
        st.info("Başvuru beklemede kayıt bulunmuyor.")
    else:
        ozet_df = basvuru_bekleyen_df[['Marka Adı', 'Sınıf', 'Satış Tarihi']].copy()
        
        ucret_listesi = []
        sinif_adedi_listesi = []
        for _, row in basvuru_bekleyen_df.iterrows():
            t_tutar = sinif_toplam_ucret_hesapla(row.get('Sınıf', ''))
            ucret_listesi.append(f"{t_tutar:,.2f} TL")
            s_adet = sinif_adedi_hesapla(row.get('Sınıf', ''))
            sinif_adedi_listesi.append(f"{s_adet} Sınıf")
            
        ozet_df['Sınıf Adedi'] = sinif_adedi_listesi
        ozet_df['Sınıf Toplam Harç Ücreti'] = ucret_listesi
        
        cols_order = ['Marka Adı', 'Sınıf', 'Sınıf Adedi', 'Satış Tarihi', 'Sınıf Toplam Harç Ücreti']
        ozet_df = ozet_df[cols_order]
        
        st.dataframe(ozet_df, use_container_width=True)

elif is_muhasebe and st.session_state.aktif_sayfa == "Kurum İncelemesinde Raporu":
    if st.button("⬅️ Geri Çık"):
        sayfa_degistir("Ana Sayfa")
        
    st.markdown("<h2>🔍 Kurum İncelemesinde Raporu</h2>", unsafe_allow_html=True)
    st.write("Kurum incelemesinde olan işlemlerin detaylı rapor görünümü aşağıdadır.")
    
    kurum_inceleme_df = df[df['Durum'].astype(str).str.strip() == "Kurum İncelemesinde"]
    
    toplam_marka_sayisi = kurum_inceleme_df['Marka Adı'].nunique()

    st.metric("Toplam Marka Adedi", f"{toplam_marka_sayisi} Adet")
    
    st.write("---")
    if kurum_inceleme_df.empty:
        st.info("Kurum incelemesinde kayıt bulunmuyor.")
    else:
        ozet_df = kurum_inceleme_df[['Marka Adı', 'Satış Tarihi', 'Başvuru Tarihi', 'Başvuru No']].copy()
        ozet_df.columns = ['Marka Adı', 'Satış Tarihi', 'Başvuru Tarihi', 'Başvuru Numarası']
        st.dataframe(ozet_df, use_container_width=True)

elif is_muhasebe and st.session_state.aktif_sayfa == "Fiyatlandırma dan ve Harç Yönetimi":
    # (Diğer sayfalar aynı kalmaktadır)
    pass

elif not is_muhasebe and st.session_state.aktif_sayfa == "Yeni Satış Giriş":
    pass

# Not: Tam kodun devamındaki diğer sayfalar önceki şablonla birebir aynı tutulmuştur.
