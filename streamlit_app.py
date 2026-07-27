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
                        if (val.length > 0) { formatted += val.substring(0, 2); }
                        if (val.length >= 3) { formatted += "/" + val.substring(2, 4); }
                        if (val.length >= 5) { formatted += "/" + val.substring(4, 8); }
                        if (el.value !== formatted) {
                            el.value = formatted;
                            el.dispatchEvent(new Event('input', { bubbles: true }));
                            el.dispatchEvent(new Event('change', { bubbles: true }));
                        }
                    };
                    input.addEventListener('input', function (e) { formatValue(e.target); });
                    input.addEventListener('blur', function (e) { formatValue(e.target); });
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

# --- TANIMLAMALAR VE DOSYA YOLLARI ---
USER_FILE = "users.csv"
DATA_FILE = "marka_takip.csv"
BACKUP_FILE = "marka_takip_yedek.csv"
HARC_CONFIG_FILE = "harc_config.csv"
EK_HARC_CONFIG_FILE = "ek_harc_config.csv"

ILLER = ["Adana", "Adıyaman", "Afyonkarahisar", "Ağrı", "Aksaray", "Amasya", "Ankara", "Antalya", "Ardahan", "Artvin", "Aydın", "Balıkesir", "Bartın", "Batman", "Bayburt", "Bilecik", "Bingöl", "Bitlis", "Bolu", "Burdur", "Bursa", "Çanakkale", "Çankırı", "Çorum", "Denizli", "Diyarbakır", "Düzce", "Edirne", "Elazığ", "Erzincan", "Erzurum", "Eskişehir", "Gaziantep", "Giresun", "Gümüşhane", "Hakkari", "Hatay", "Iğdır", "Isparta", "İstanbul", "İzmir", "Kahramanmaraş", "Karabük", "Karaman", "Kars", "Kastamonu", "Kayseri", "Kırıkkale", "Kırklareli", "Kırşehir", "Kilis", "Kocaeli", "Konya", "Kütahya", "Malatya", "Manisa", "Mardin", "Mersin", "Muğla", "Muş", "Nevşehir", "Niğde", "Ordu", "Osmaniye", "Rize", "Sakarya", "Samsun", "Siirt", "Sinop", "Sivas", "Şanlıurfa", "Şırnak", "Tekirdağ", "Tokat", "Trabzon", "Tunceli", "Uşak", "Van", "Yalova", "Yozgat", "Zonguldak"]
SINIFLAR = [str(i) for i in range(1, 46)] + [f"35/{i}" for i in range(1, 35)]
OPERASYON_YETKILILERI = ["SELEN", "DENİZ", "ALİ OSMAN"]

def load_users():
    default_users = pd.DataFrame({
        "İsim": ["ALİ OSMAN YELBEY", "DENİZ TELLİ GÜRLEYENDAĞ", "MERVE YURTLU", "SELEN AKCAN", "ELİF YILDIZ"],
        "Şifre": ["MARKA123", "MARKA123", "MARKA123", "MARKA123", "MARKA123"]
    })
    if not os.path.exists(USER_FILE) or os.path.getsize(USER_FILE) == 0:
        default_users.to_csv(USER_FILE, index=False, encoding='utf-8-sig', sep=';')
        return default_users
    try:
        u_df = pd.read_csv(USER_FILE, encoding='utf-8-sig', sep=';', dtype=str)
        if len(u_df.columns) <= 1:
            u_df = pd.read_csv(USER_FILE, encoding='utf-8-sig', sep=',', dtype=str)
        
        u_df.columns = [c.strip() for c in u_df.columns]
        if "İsim" not in u_df.columns or "Şifre" not in u_df.columns:
            if len(u_df.columns) == 1 and "," in u_df.columns[0]:
                u_df = pd.read_csv(USER_FILE, encoding='utf-8-sig', sep=',', dtype=str)
                u_df.columns = [c.strip() for c in u_df.columns]
            if "İsim" not in u_df.columns or "Şifre" not in u_df.columns:
                default_users.to_csv(USER_FILE, index=False, encoding='utf-8-sig', sep=';')
                return default_users
        return u_df
    except:
        default_users.to_csv(USER_FILE, index=False, encoding='utf-8-sig', sep=';')
        return default_users

def save_users(u_df):
    u_df.to_csv(USER_FILE, index=False, encoding='utf-8-sig', sep=';')

def ay_ekle(kaynak_tarih, ay_sayisi=2):
    yil = kaynak_tarih.year + (kaynak_tarih.month + ay_sayisi - 1) // 12
    ay = (kaynak_tarih.month + ay_sayisi - 1) % 12 + 1
    gun = kaynak_tarih.day
    while True:
        try:
            return datetime(yil, ay, gun)
        except ValueError:
            gun -= 1

def ay_ekle_1_ay(kaynak_tarih, ay_sayisi=1):
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
        haftanin_gunu = dt.weekday() # 0: Pzt, ..., 5: Cts, 6: Pazar
        ay_gun = (dt.day, dt.month)
        if haftanin_gunu == 5: # Cumartesi ise ilk Pazartesiye at (+2 gün)
            dt += timedelta(days=2)
        elif haftanin_gunu == 6: # Pazar ise ilk Pazartesiye at (+1 gün)
            dt += timedelta(days=1)
        elif ay_gun in resmi_tatiller:
            dt += timedelta(days=1)
        else:
            break
    return dt

def hesapla_tescil_son_odeme(tescil_tarihi_str):
    if not tescil_tarihi_str or str(tescil_tarihi_str).strip() == "" or str(tescil_tarihi_str).lower() == "nan":
        return ""
    try:
        parsed_t_tar = datetime.strptime(str(tescil_tarihi_str).strip(), "%d/%m/%Y")
        hesaplanan_bitis = ay_ekle(parsed_t_tar, 2)
        son_odeme_dt = resmi_tatil_ve_tatil_kontrol(hesaplanan_bitis)
        return son_odeme_dt.strftime("%d/%m/%Y")
    except:
        return str(tescil_tarihi_str)

def hesapla_savunma_son_gun(itiraz_tarihi_str):
    if not itiraz_tarihi_str or str(itiraz_tarihi_str).strip() == "" or str(itiraz_tarihi_str).lower() == "nan":
        return ""
    try:
        parsed_i_tar = datetime.strptime(str(itiraz_tarihi_str).strip(), "%d/%m/%Y")
        hesaplanan_bitis = ay_ekle_1_ay(parsed_i_tar, 1)
        son_gun_dt = resmi_tatil_ve_tatil_kontrol(hesaplanan_bitis)
        return son_gun_dt.strftime("%d/%m/%Y")
    except:
        return str(itiraz_tarihi_str)

def tarih_birlestir_ve_formatla(tarih_str):
    if not tarih_str: return ""
    temiz = "".join(filter(str.isdigit, str(tarih_str)))
    if len(temiz) == 8:
        return f"{temiz[:2]}/{temiz[2:4]}/{temiz[4:]}"
    return tarih_str.strip()

def veriyi_kaydet_ve_yedekle(df_to_save):
    df_to_save.to_csv(DATA_FILE, index=False, encoding='utf-8-sig', sep=';')
    try:
        df_to_save.to_csv(BACKUP_FILE, index=False, encoding='utf-8-sig', sep=';')
    except:
        pass

def load_data():
    zorunlu_kolonlar = [
        "Marka Adı", "Ad Soyad", "TC", "Telefon", "E-Mail", "Doğum Tarihi", "İl", "Sınıf", "Ödeme", 
        "Satış Tarihi", "Tutar", "Durum", "Danışman", "Fatura No", "Fatura Tarihi", 
        "Başvuru No", "Başvuru Tarihi", "Yayın Tarihi", "Yayın Bitiş Tarihi", 
        "Sonraki Aşama Seçimi", "İtiraz Tarihi", "Savunma Son Günü", "Tescil Tebliğ Tarihi", "Tescil Son Ödeme Tarihi", "Ödeme Tarihi", "Tescil Harç Tutarı", "Sabitlenen Maliyet", "Ödeme Sözü Tarihi", "Operasyon Yetkilisi", "Ödeme Sözü Güncelleme Sayısı",
        "Savunma Durumu", "Savunma Ücreti KDV Dahil", "Evrak Numarası", "Savunma Ücreti Alındı", "Savunma Yapıldı Tarihi"
    ]
    if not os.path.exists(DATA_FILE) or os.path.getsize(DATA_FILE) == 0:
        if os.path.exists(BACKUP_FILE) and os.path.getsize(BACKUP_FILE) > 0:
            d_temp = pd.read_csv(BACKUP_FILE, dtype=str, encoding='utf-8-sig', sep=';')
            if len(d_temp.columns) <= 1: d_temp = pd.read_csv(BACKUP_FILE, dtype=str, encoding='utf-8-sig', sep=',')
            veriyi_kaydet_ve_yedekle(d_temp)
        else:
            d_temp = pd.DataFrame(columns=zorunlu_kolonlar)
            veriyi_kaydet_ve_yedekle(d_temp)
    else:
        try:
            d_temp = pd.read_csv(DATA_FILE, dtype=str, encoding='utf-8-sig', sep=';')
            if len(d_temp.columns) <= 1: d_temp = pd.read_csv(DATA_FILE, dtype=str, encoding='utf-8-sig', sep=',')
        except:
            if os.path.exists(BACKUP_FILE) and os.path.getsize(BACKUP_FILE) > 0:
                d_temp = pd.read_csv(BACKUP_FILE, dtype=str, encoding='utf-8-sig', sep=';')
                if len(d_temp.columns) <= 1: d_temp = pd.read_csv(BACKUP_FILE, dtype=str, encoding='utf-8-sig', sep=',')
            else:
                d_temp = pd.DataFrame(columns=zorunlu_kolonlar)
            veriyi_kaydet_ve_yedekle(d_temp)
            
    if "ID" in d_temp.columns:
        d_temp = d_temp.drop(columns=["ID"])
    for col in zorunlu_kolonlar:
        if col not in d_temp.columns: 
            if col == "Ödeme Sözü Güncelleme Sayısı":
                d_temp[col] = "0"
            elif col == "Savunma Ücreti Alındı":
                d_temp[col] = "Hayır"
            else:
                d_temp[col] = ""
        else:
            if col == "Ödeme Sözü Güncelleme Sayısı":
                d_temp[col] = d_temp[col].fillna("0")
            elif col == "Savunma Ücreti Alındı":
                d_temp[col] = d_temp[col].fillna("Hayır")
        
    d_temp['Durum'] = d_temp['Durum'].fillna("").str.strip()
    
    degisiklik_var = False
    for idx_row, row_data in d_temp.iterrows():
        t_teblig = str(row_data.get('Tescil Tebliğ Tarihi', '')).strip()
        if t_teblig and t_teblig.lower() != 'nan':
            dogru_son_odeme = hesapla_tescil_son_odeme(t_teblig)
            if dogru_son_odeme and str(row_data.get('Tescil Son Ödeme Tarihi', '')) != dogru_son_odeme:
                d_temp.at[idx_row, 'Tescil Son Ödeme Tarihi'] = dogru_son_odeme
                degisiklik_var = True
                
        i_tar = str(row_data.get('İtiraz Tarihi', '')).strip()
        if i_tar and i_tar.lower() != 'nan':
            dogru_savunma_son = hesapla_savunma_son_gun(i_tar)
            if dogru_savunma_son and str(row_data.get('Savunma Son Günü', '')) != dogru_savunma_son:
                d_temp.at[idx_row, 'Savunma Son Günü'] = dogru_savunma_son
                degisiklik_var = True

    if degisiklik_var:
        veriyi_kaydet_ve_yedekle(d_temp)
        
    return d_temp

if "sinif_harclari" not in st.session_state:
    st.session_state.sinif_harclari = {}
    if os.path.exists(HARC_CONFIG_FILE) and os.path.getsize(HARC_CONFIG_FILE) > 0:
        try:
            h_df = pd.read_csv(HARC_CONFIG_FILE, encoding='utf-8-sig', sep=';')
            if len(h_df.columns) <= 1: h_df = pd.read_csv(HARC_CONFIG_FILE, encoding='utf-8-sig', sep=',')
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
        ek_df = pd.read_csv(EK_HARC_CONFIG_FILE, encoding='utf-8-sig', sep=';')
        if len(ek_df.columns) <= 1: ek_df = pd.read_csv(EK_HARC_CONFIG_FILE, encoding='utf-8-sig', sep=',')
        if "Tescil Harç Bedeli" in ek_df.columns and not ek_df.empty: st.session_state.tescil_harc_bedeli = float(ek_df.iloc[0]["Tescil Harç Bedeli"])
        if "Savunma Harç Bedeli" in ek_df.columns and not ek_df.empty: st.session_state.savunma_harc_bedeli = float(ek_df.iloc[0]["Savunma Harç Bedeli"])
        if "Bildirim Tescil Tutar" in ek_df.columns and not ek_df.empty: st.session_state.bildirim_tescil_tutar = float(ek_df.iloc[0]["Bildirim Tescil Tutar"])
        if "KDV Oranı" in ek_df.columns and not ek_df.empty: st.session_state.kdv_orani = float(ek_df.iloc[0]["KDV Oranı"])
    except: pass

def sinif_harci_ve_avukat_hesapla(sinif_str):
    try:
        parcalar = [p.strip() for p in str(sinif_str).split(",") if p.strip()]
        toplam_tutar = 0.0
        islenen_ana_siniflar = set()
        sirali_sayac = 0
        for p in parcalar:
            if "/" in p: continue
            if p.isdigit():
                s_int = int(p)
                if 1 <= s_int <= 45:
                    if s_int not in islenen_ana_siniflar:
                        islenen_ana_siniflar.add(s_int)
                        sirali_sayac += 1
                        kayit = st.session_state.sinif_harclari.get(sirali_sayac, {"harc": 2820.0, "avukat": 750.0})
                        toplam_tutar += kayit["harc"] + kayit["avukat"]
        return toplam_tutar
    except: return 0.0

def sinif_toplam_ucret_hesapla(sinif_str):
    try:
        parcalar = [p.strip() for p in str(sinif_str).split(",") if p.strip()]
        gorulen_ana_siniflar = set()
        for p in parcalar:
            if "/" in p: continue
            if p.isdigit():
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
        user_df = load_users()
            
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
elif is_muhasebe: st.sidebar.markdown("💰 Rol: **Muhasebe / Yönetici / Operasyon**")
else: st.sidebar.markdown("💼 Rol: **Danışman**")

if st.sidebar.button("🚪 Güvenli Çıkış", use_container_width=True):
    st.session_state.kullanici = None
    if "user" in st.query_params: del st.query_params["user"]
    st.session_state.aktif_sayfa = "Ana Sayfa"
    st.rerun()

st.sidebar.write("---")

if not is_muhasebe:
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
        if st.button("⚠️ İtiraz Savunma Bekliyor Raporu", use_container_width=True): sayfa_degistir("İtiraz Savunma Bekliyor Raporu")
        if st.button("📋 Savunma Yapıldı Raporu", use_container_width=True): sayfa_degistir("Savunma Yapıldı Raporu")
        if st.button("❌ Savunma Yapılmadı Raporu", use_container_width=True): sayfa_degistir("Savunma Yapılmadı Raporu")
        if st.button("📌 Tescil Tebliğ Beklemede Raporu", use_container_width=True): sayfa_degistir("Tescil Tebliğ Beklemede Raporu")
        if st.button("💳 Tescil Tebliğ Arandı Raporu", use_container_width=True): sayfa_degistir("Tescil Tebliğ Arandı Raporu")
        if st.button("📅 Ödeme Sözü Verenler Raporu", use_container_width=True): sayfa_degistir("Ödeme Sözü Verenler Raporu")
        if st.button("⏳ Tescil Kurum Ödemesi Bekleyen Raporu", use_container_width=True): sayfa_degistir("Tescil Kurum Ödemesi Bekleyen Raporu")
    
    with st.sidebar.expander("⚙️ Fiyatlandırma Yönetimi", expanded=True):
        if st.button("💰 Fiyatlandırma ve Harç Yönetimi", use_container_width=True): sayfa_degistir("Fiyatlandırma ve Harç Yönetimi")
    
    with st.sidebar.expander("📈 Marka Tescil Aşamaları", expanded=True):
        if st.button("📌 Muhasebe Onayı Bekliyor", use_container_width=True): sayfa_degistir("Muhasebe Onayı Bekliyor")
        if st.button("⏳ Başvuru Beklemede", use_container_width=True): sayfa_degistir("Başvuru Beklemede")
        if st.button("🔍 Kurum İncelemesinde", use_container_width=True): sayfa_degistir("Kurum İncelemesinde")
        if st.button("📰 Yayında", use_container_width=True): sayfa_degistir("Yayında")
        if st.button("⚠️ İtiraz / Savunma Bekliyor", use_container_width=True): sayfa_degistir("İtiraz Geldi - Savunma Bekliyor")
        if st.button("📋 Savunma Yapıldı", use_container_width=True): sayfa_degistir("Savunma Yapıldı")
        if st.button("❌ Savunma Yapılmadı", use_container_width=True): sayfa_degistir("Savunma Yapılmadı")
        if st.button("📄 Tescil Tebliğ Beklemede", use_container_width=True): sayfa_degistir("Tescil Tebliğ Beklemede")
        if st.button("📞 Ödeme Sözü Verenler", use_container_width=True): sayfa_degistir("Ödeme Sözü Verenler")
        if st.button("💳 Tescil Tebliğ Edildi Müşteri Arandı", use_container_width=True): sayfa_degistir("Tescil Tebliğ Edildi Müşteri Arandı")
        if st.button("⏳ Tescil Kurum Ödemesi Bekleyen", use_container_width=True): sayfa_degistir("Tescil Kurum Ödemesi Bekleyen")
        if st.button("📄 Tescil Kuruma Ödendi", use_container_width=True): sayfa_degistir("Tescil Kuruma Ödendi")
        if st.button("🎉 Tescillendi", use_container_width=True): sayfa_degistir("Tescillendi")
        if st.button("❌ Reddedildi", use_container_width=True): sayfa_degistir("Reddedildi")
    
    if st.sidebar.button("🛠️ Danışman Satışlarını Düzenle", use_container_width=True): sayfa_degistir("Danışman Satışlarını Düzenle")

if is_admin:
    st.sidebar.write("---")
    if st.sidebar.button("👥 Personel Yönetimi", use_container_width=True): sayfa_degistir("Personel Yönetimi")

df = load_data()

# --- SAYFA İÇERİKLERİ ---
if st.session_state.aktif_sayfa == "Ana Sayfa":
    st.markdown(f"<h2>Hoş Geldiniz, {aktif_kullanici_ad}</h2>", unsafe_allow_html=True)
    st.write("Sol taraftaki menüyü kullanarak işlemlerinize başlayabilirsiniz.")

elif is_muhasebe and st.session_state.aktif_sayfa == "Toplu Excel Yükleme":
    if st.button("⬅️ Geri Çık"): sayfa_degistir("Ana Sayfa")
    st.markdown("<h2>📂 Toplu Excel / CSV Veri Yükleme Paneli</h2>", unsafe_allow_html=True)
    st.write("Geçmiş tüm satışlarınızı ve durumlarını tek seferde sisteme yüklemek için aşağıdaki örnek şablonu indirebilir ve Excel'de doğrudan **sütunlara ayrılmış** şekilde açıp doldurabilirsiniz.")
    
    ornek_data = {
        "Marka Adı": ["Örnek Marka A", "Örnek Marka B"], "Ad Soyad": ["Ahmet Yılmaz", "Ayşe Demir"],
        "TC": ["11111111111", "22222222222"], "Telefon": ["05321112233", "05334445566"],
        "E-Mail": ["ahmet@ornek.com", "ayse@ornek.com"], "Doğum Tarihi": ["01/01/1990", "05/05/1985"],
        "İl": ["İstanbul", "Ankara"], "Sınıf": ["9, 35", "25"], "Ödeme": ["EFT", "Kredi Kartı"],
        "Satış Tarihi": ["10/01/2026", "15/02/2026"], "Tutar": ["15000", "20000"],
        "Durum": ["Başvuru Beklemede", "Yayında"], "Danışman": ["MERVE YURTLU", "SELEN AKCAN"],
        "Fatura No": ["ABC2026000001", "ABC2026000002"], "Fatura Tarihi": ["10/01/2026", "15/02/2026"],
        "Başvuru No": ["2026/01234", "2026/05678"], "Başvuru Tarihi": ["11/01/2026", "16/02/2026"],
        "Sonraki Aşama Seçimi": ["", ""], "İtiraz Tarihi": ["", ""], "Savunma Son Günü": ["", ""], "Tescil Tebliğ Tarihi": ["", ""],
        "Tescil Son Ödeme Tarihi": ["", ""], "Ödeme Tarihi": ["", ""], "Sabitlenen Maliyet": ["", ""], "Ödeme Sözü Tarihi": ["", ""], "Operasyon Yetkilisi": ["", ""], "Ödeme Sözü Güncelleme Sayısı": ["0", "0"],
        "Savunma Durumu": ["", ""], "Savunma Ücreti KDV Dahil": ["", ""], "Evrak Numarası": ["", ""], "Savunma Ücreti Alındı": ["Hayır", "Hayır"], "Savunma Yapıldı Tarihi": ["", ""]
    }
    ornek_df = pd.DataFrame(ornek_data)
    csv_veri = ornek_df.to_csv(index=False, encoding='utf-8-sig', sep=';').encode('utf-8-sig')

    st.download_button(
        label="📥 Sütunlu Örnek CSV Şablonunu İndir",
        data=csv_veri,
        file_name="markanow_satis_sablonu.csv",
        mime="text/csv",
        use_container_width=True
    )
    
    st.write("---")
    yuklenen_dosya = st.file_uploader("Doldurduğunuz CSV (.csv) veya Excel (.xlsx) Dosyasını Seçin", type=["csv", "xlsx"])
    
    if yuklenen_dosya is not None:
        try:
            if yuklenen_dosya.name.endswith('.csv'):
                yuklenen_df = pd.read_csv(yuklenen_dosya, dtype=str, encoding='utf-8-sig', sep=';')
                if len(yuklenen_df.columns) <= 1:
                    yuklenen_df = pd.read_csv(yuklenen_dosya, dtype=str, encoding='utf-8-sig', sep=',')
            else:
                yuklenen_df = pd.read_excel(yuklenen_dosya, dtype=str)
                
            st.success(f"✅ Dosya başarıyla okundu! Toplam {len(yuklenen_df)} adet kayıt bulundu.")
            st.dataframe(yuklenen_df.head(), use_container_width=True)
            
            if st.button("🚀 Tüm Kayıtları Sisteme Aktar ve Veritabanını Güncelle", use_container_width=True):
                zorunlu_kolonlar = list(ornek_data.keys())
                for col in zorunlu_kolonlar:
                    if col not in yuklenen_df.columns: yuklenen_df[col] = ""
                
                for idx_u, row_u in yuklenen_df.iterrows():
                    if not str(row_u.get('Sabitlenen Maliyet', '')).strip():
                        yuklenen_df.at[idx_u, 'Sabitlenen Maliyet'] = str(sinif_toplam_ucret_hesapla(row_u.get('Sınıf', '')))
                        
                yuklenen_df = yuklenen_df[zorunlu_kolonlar].fillna("")
                
                islem_turu = st.radio("İşlem Türü Seçin:", ["Mevcut Verilerin Üstüne Ekle (Append)", "Mevcut Verileri Sil ve Dosyadakileri Yükle (Sıfırdan Kur)"])
                if "Sıfırdan Kur" in islem_turu: final_df = yuklenen_df
                else: final_df = pd.concat([df, yuklenen_df], ignore_index=True)
                
                veriyi_kaydet_ve_yedekle(final_df) 
                
                st.success("🎉 Başarılı! Tüm geçmiş satışlar and durumlar sisteme aktarıldı and yedeklendi.")
                import time; time.sleep(1.5)
                st.session_state.aktif_sayfa = "Ana Sayfa"
                st.rerun()
        except Exception as e:
            st.error(f"❌ Dosya okunurken hata oluştu: {e}")

elif is_muhasebe and st.session_state.aktif_sayfa == "Marka Tescil Raporlama":
    if st.button("⬅️ Geri Çık"): sayfa_degistir("Ana Sayfa")
    st.markdown("<h2>📈 Marka Tescil Aşamaları Raporlama Paneli</h2>", unsafe_allow_html=True)
    
    aylar_secenek = {"Tümü": None, "Ocak": "01", "Şubat": "02", "Mart": "03", "Nisan": "04", "Mayıs": "05", "Haziran": "06", "Temmuz": "07", "Ağustos": "08", "Eylül": "09", "Ekim": "10", "Kasım": "11", "Aralık": "12"}
    mevcut_yil_str = str(datetime.now().year)
    yillar_kumesi = {mevcut_yil_str}
    
    if not df.empty:
        tarih_kolonlari = ['Satış Tarihi', 'Fatura Tarihi', 'Başvuru Tarihi', 'Tescil Tebliğ Tarihi', 'Ödeme Tarihi', 'Ödeme Sözü Tarihi', 'İtiraz Tarihi', 'Savunma Son Günü', 'Savunma Yapıldı Tarihi']
        for t_col in tarih_kolonlari:
            if t_col in df.columns:
                for t_str in df[t_col].dropna():
                    try:
                        dt_temp = pd.to_datetime(t_str, format='%d/%m/%Y', errors='coerce')
                        if pd.isna(dt_temp): dt_temp = pd.to_datetime(t_str, errors='coerce')
                        if not pd.isna(dt_temp): yillar_kumesi.add(str(dt_temp.year))
                    except: pass
                    
    yillar_listesi = ["Tümü"] + sorted(list(yillar_kumesi), reverse=True)

    if "genel_rapor_filtrelendi" not in st.session_state:
        st.session_state.genel_rapor_filtrelendi = False
        st.session_state.secilen_rapor_yil = "Tümü"
        st.session_state.secilen_rapor_ay_isim = "Tümü"

    f_col1, f_col2, f_col3 = st.columns([1, 1, 1])
    varsayilan_yil_idx = yillar_listesi.index(mevcut_yil_str) if mevcut_yil_str in yillar_listesi else 0
    secilen_rapor_yil = f_col1.selectbox("Yıl Seçin", options=yillar_listesi, index=varsayilan_yil_idx, key="genel_rapor_yil_sec")
    secilen_rapor_ay_isim = f_col2.selectbox("Ay Seçin", options=list(aylar_secenek.keys()), key="genel_rapor_ay_sec")
    
    with f_col3:
        st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
        filtrele_basildi = st.button("🔍 Filtrele", use_container_width=True)

    if filtrele_basildi:
        st.session_state.genel_rapor_filtrelendi = True
        st.session_state.secilen_rapor_yil = secilen_rapor_yil
        st.session_state.secilen_rapor_ay_isim = secilen_rapor_ay_isim
        st.success("✅ Filtrelendi!")

    secilen_rapor_ay_kod = aylar_secenek[st.session_state.secilen_rapor_ay_isim]
    aktif_yil = st.session_state.secilen_rapor_yil

    def genel_rapor_filtrele(row):
        try:
            if aktif_yil == "Tümü" and secilen_rapor_ay_kod is None:
                return True

            tarih_listesi = [
                row.get('Satış Tarihi', ''), row.get('Fatura Tarihi', ''), 
                row.get('Başvuru Tarihi', ''), 
                row.get('Tescil Tebliğ Tarihi', ''), row.get('Ödeme Tarihi', ''), row.get('Ödeme Sözü Tarihi', ''),
                row.get('İtiraz Tarihi', ''), row.get('Savunma Son Günü', ''), row.get('Savunma Yapıldı Tarihi', '')
            ]
            
            gecerli_dt = None
            for t_str in tarih_listesi:
                if pd.notna(t_str) and str(t_str).strip() != '' and str(t_str).lower() != 'nan':
                    dt = pd.to_datetime(t_str, format='%d/%m/%Y', errors='coerce')
                    if pd.isna(dt): dt = pd.to_datetime(t_str, errors='coerce')
                    if not pd.isna(dt):
                        gecerli_dt = dt
                        break
            
            if gecerli_dt is None:
                return True

            yil_uyusur = True if aktif_yil == "Tümü" else (str(gecerli_dt.year) == str(aktif_yil))
            ay_uyusur = True if secilen_rapor_ay_kod is None else (f"{gecerli_dt.month:02d}" == secilen_rapor_ay_kod)
            return yil_uyusur and ay_uyusur
        except: 
            return True

    if aktif_yil == "Tümü" and secilen_rapor_ay_kod is None:
        rapor_filtrelenmis_df = df.copy() if not df.empty else df.copy()
    else:
        rapor_filtrelenmis_df = df[df.apply(genel_rapor_filtrele, axis=1)].copy() if not df.empty else df.copy()

    def get_count_and_df(asama_adi):
        temiz_hedef = str(asama_adi).strip().lower()
        
        def durum_eslesiyor(d_val):
            d_str = str(d_val).strip().lower()
            if not d_str or d_str == 'nan':
                return False
            if temiz_hedef == d_str:
                return True
            if temiz_hedef in d_str or d_str in temiz_hedef:
                return True
            if "yayında" in temiz_hedef and "yayında" in d_str:
                return True
            if "muhasebe" in temiz_hedef and "muhasebe" in d_str:
                return True
            if "başvuru" in temiz_hedef and "başvuru" in d_str:
                return True
            if "kurum" in temiz_hedef and "kurum" in d_str:
                return True
            if "tescil tebliğ" in temiz_hedef and "tescil tebliğ" in d_str:
                return True
            return False

        sub_df = rapor_filtrelenmis_df[rapor_filtrelenmis_df['Durum'].apply(durum_eslesiyor)]
        return len(sub_df), sub_df
        
    rapor_kalemleri = [
        ("Muhasebe Onayı Bekliyor", "Muhasebe Onayı Bekliyor"), ("Başvuru Beklemede", "Başvuru Beklemede"),
        ("Kurum İncelemesinde", "Kurum İncelemesinde"), ("Yayında", "Yayında"),
        ("İtiraz / Savunma Bekliyor", "İtiraz Geldi - Savunma Bekliyor"), ("Savunma Yapıldı", "Savunma Yapıldı"), ("Savunma Yapılmadı", "Savunma Yapılmadı"), ("Tescil Tebliğ Beklemede", "Tescil Tebliğ Beklemede"),
        ("Ödeme Sözü Verenler", "Ödeme Sözü Verenler"), ("Tescil Tebliğ Edildi Müşteri Arandı", "Tescil Tebliğ Edildi Müşteri Arandı"), ("Tescil Kurum Ödemesi Bekleyen", "Tescil Kurum Ödemesi Bekleyen"),
        ("Tescil Kuruma Ödendi", "Tescil Kuruma Ödendi"),
        ("Tescillendi", "Tescillendi 🎉"), ("Reddedildi", "Reddedildi ❌")
    ]

    with st.expander("🔍 Sistemdeki Kayıtların Durum Özetini Görmek İçin Tıklayın (Hata Ayıklama)", expanded=False):
        if not df.empty and 'Marka Adı' in df.columns:
            st.dataframe(df[['Marka Adı', 'Durum', 'Satış Tarihi', 'Danışman', 'Operasyon Yetkilisi']], use_container_width=True)
        else:
            st.info("Kayıt bulunmuyor.")

    st.write("---")
    cols = st.columns(3)
    for idx, (gorunen_isim, durum_kod) in enumerate(rapor_kalemleri):
        adet, _ = get_count_and_df(durum_kod)
        with cols[idx % 3]: st.metric(label=gorunen_isim, value=f"{adet} Adet")

elif is_muhasebe and st.session_state.aktif_sayfa == "Aylık Net Kar / Zarar Raporu":
    if st.button("⬅️ Geri Çık"): sayfa_degistir("Ana Sayfa")
    st.markdown("<h2>📊 Aylık Net Kar / Zarar ve Personel Ciro Raporu</h2>", unsafe_allow_html=True)
    aylar = {"Tümü": None, "Ocak": "01", "Şubat": "02", "Mart": "03", "Nisan": "04", "Mayıs": "05", "Haziran": "06", "Temmuz": "07", "Ağustos": "08", "Eylül": "09", "Ekim": "10", "Kasım": "11", "Aralık": "12"}
    mevcut_yil_str = str(datetime.now().year)
    yillar_kumesi = {mevcut_yil_str}
    if 'Satış Tarihi' in df.columns:
        for t_str in df['Satış Tarihi'].dropna():
            try:
                dt_temp = pd.to_datetime(t_str, format='%d/%m/%Y', errors='coerce')
                if pd.isna(dt_temp): dt_temp = pd.to_datetime(t_str, errors='coerce')
                if not pd.isna(dt_temp): yillar_kumesi.add(str(dt_temp.year))
            except: pass
    
    yillar_listesi = ["Tümü"] + sorted(list(yillar_kumesi), reverse=True)

    personel_listesi = ["Tümü"]
    unik_personel = set()
    if 'Danışman' in df.columns:
        unik_personel.update(df['Danışman'].dropna().astype(str).str.strip().str.upper().tolist())
    if 'Operasyon Yetkilisi' in df.columns:
        unik_personel.update(df['Operasyon Yetkilisi'].dropna().astype(str).str.strip().str.upper().tolist())
    personel_listesi.extend(sorted([p for p in unik_personel if p]))

    if "kar_zarar_filtrelendi" not in st.session_state:
        st.session_state.kar_zarar_filtrelendi = False
        st.session_state.secilen_kz_ay = "Tümü"
        st.session_state.secilen_kz_yil = mevcut_yil_str if mevcut_yil_str in yillar_listesi else "Tümü"
        st.session_state.secilen_kz_personel = "Tümü"

    if "secilen_kz_personel" not in st.session_state:
        st.session_state.secilen_kz_personel = "Tümü"

    col_f1, col_f2, col_f3, col_f4 = st.columns([1, 1, 1, 1])
    varsayilan_yil_index = yillar_listesi.index(st.session_state.secilen_kz_yil) if st.session_state.secilen_kz_yil in yillar_listesi else 0
    varsayilan_ay_index = list(aylar.keys()).index(st.session_state.secilen_kz_ay) if st.session_state.secilen_kz_ay in aylar else 0
    varsayilan_personel_index = personel_listesi.index(st.session_state.secilen_kz_personel) if st.session_state.secilen_kz_personel in personel_listesi else 0

    secilen_ay_isim = col_f1.selectbox("Ay Seçin", list(aylar.keys()), index=varsayilan_ay_index, key="kar_zarar_ay_sec")
    secilen_yil = col_f2.selectbox("Yıl", options=yillar_listesi, index=varsayilan_yil_index, key="kar_zarar_yil_sec")
    secilen_personel_filtre = col_f3.selectbox("Danışman / Operasyon Yetkilisi Seçin", personel_listesi, index=varsayilan_personel_index, key="kar_zarar_personel_sec")
    
    with col_f4:
        st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
        kz_filtrele_basildi = st.button("🔍 Filtrele", key="kz_filtre_btn", use_container_width=True)

    if kz_filtrele_basildi:
        st.session_state.kar_zarar_filtrelendi = True
        st.session_state.secilen_kz_ay = secilen_ay_isim
        st.session_state.secilen_kz_yil = secilen_yil
        st.session_state.secilen_kz_personel = secilen_personel_filtre
        st.success("✅ Filtrelendi!")

    secilen_ay_kod = aylar[st.session_state.secilen_kz_ay]
    aktif_kz_yil = st.session_state.secilen_kz_yil
    aktif_kz_personel = st.session_state.secilen_kz_personel

    rapor_df = df.copy()
    def net_kar_filtrele(row):
        try:
            if aktif_kz_personel != "Tümü":
                dan = str(row.get('Danışman', '')).strip().upper()
                op = str(row.get('Operasyon Yetkilisi', '')).strip().upper()
                if dan != aktif_kz_personel and op != aktif_kz_personel: return False
            s_tarih = row.get('Satış Tarihi', '')
            if pd.isna(s_tarih) or str(s_tarih).strip() == '': return False
            dt = pd.to_datetime(s_tarih, format='%d/%m/%Y', errors='coerce')
            if pd.isna(dt): dt = pd.to_datetime(s_tarih, errors='coerce')
            if pd.isna(dt): return False
            ay_eslesir = True if secilen_ay_kod is None else (f"{dt.month:02d}" == secilen_ay_kod)
            yil_eslesir = True if aktif_kz_yil == "Tümü" else (str(dt.year) == str(aktif_kz_yil).strip())
            return ay_eslesir and yil_eslesir
        except: return False
        
    if not rapor_df.empty: rapor_df = rapor_df[rapor_df.apply(net_kar_filtrele, axis=1)]
    
    toplam_ciro_dahil, toplam_kdv_haric_ciro, toplam_kdv_tutari, toplam_harc_maliyeti = 0.0, 0.0, 0.0, 0.0
    tablo_satirlari = []
    kdv_orani = st.session_state.kdv_orani
    
    for idx_r, row in rapor_df.iterrows():
        tutar_dahil = float(str(row.get('Tutar', '0')).replace(',', '.')) if str(row.get('Tutar', '0')).strip() else 0.0
        kdv_haric = tutar_dahil / (1 + (kdv_orani / 100.0))
        kdv_tutari = tutar_dahil - kdv_haric
        
        sabit_maliyet_val = row.get('Sabitlenen Maliyet', '')
        if pd.notna(sabit_maliyet_val) and str(sabit_maliyet_val).strip() != '' and str(sabit_maliyet_val).lower() != 'nan':
            try:
                harc_maliyeti = float(str(sabit_maliyet_val).replace(',', '.'))
            except:
                harc_maliyeti = sinif_toplam_ucret_hesapla(row.get('Sınıf', ''))
        else:
            harc_maliyeti = sinif_toplam_ucret_hesapla(row.get('Sınıf', ''))
            df.at[idx_r, 'Sabitlenen Maliyet'] = str(harc_maliyeti)
            veriyi_kaydet_ve_yedekle(df)

        net_durum = kdv_haric - harc_maliyeti
        toplam_ciro_dahil += tutar_dahil
        toplam_kdv_haric_ciro += kdv_haric
        toplam_kdv_tutari += kdv_tutari
        toplam_harc_maliyeti += harc_maliyeti
        
        sinif_degeri = row.get('Sınıf', '')
        kac_sinif_sayisi = sinif_adedi_hesapla(sinif_degeri)
        kac_sinif_metin = f"{kac_sinif_sayisi} Sınıf" if kac_sinif_sayisi > 0 else "0 Sınıf"

        tablo_satirlari.append({
            "Marka Adı": row.get('Marka Adı', ''), "Danışman": row.get('Danışman', ''), "Operasyon Yetkilisi": row.get('Operasyon Yetkilisi', ''), "Satış Tarihi": row.get('Satış Tarihi', ''),
            "Sınıf": sinif_degeri, "Kaç Sınıf": kac_sinif_metin, "KDV Dahil Tutar (TL)": f"{tutar_dahil:,.2f} TL", "KDV Hariç Tutar (TL)": f"{kdv_haric:,.2f} TL",
            "KDV (TL)": f"{kdv_tutari:,.2f} TL", "Sınıf Toplam Harç (TL)": f"{harc_maliyeti:,.2f} TL", "Net Rakam (TL)": f"{net_durum:,.2f} TL"
        })
    genel_net_kar = toplam_kdv_haric_ciro - toplam_harc_maliyeti
    
    st.write("---")
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Toplam Ciro (KDV Dahil)", f"{toplam_ciro_dahil:,.2f} TL")
    c2.metric("Toplam KDV Hariç Ciro", f"{toplam_kdv_haric_ciro:,.2f} TL")
    c3.metric("Toplam KDV", f"{toplam_kdv_tutari:,.2f} TL")
    c4.metric("Toplam Sınıf Harç Maliyeti", f"{toplam_harc_maliyeti:,.2f} TL")
    c5.metric("Toplam Net Kar / Zarar", f"{genel_net_kar:,.2f} TL")
    st.write("---")
    if not tablo_satirlari: st.info("Seçilen kriterlere uygun kayıt bulunamadı.")
    else: st.dataframe(pd.DataFrame(tablo_satirlari), use_container_width=True)

elif is_muhasebe and st.session_state.aktif_sayfa == "Muhasebe Bekleyen Raporu":
    if st.button("⬅️ Geri Çık"): sayfa_degistir("Ana Sayfa")
    st.markdown("<h2>📌 Muhasebe Bekleyen Raporu</h2>", unsafe_allow_html=True)
    muhasebe_bekleyen_df = df[df['Durum'].astype(str).str.strip() == "Muhasebe Onayı Bekliyor"]
    toplam_marka_sayisi = muhasebe_bekleyen_df['Marka Adı'].nunique()
    toplam_sinif_adedi = sum([sinif_adedi_hesapla(s) for s in muhasebe_bekleyen_df['Sınıf'].dropna()])
    toplam_tutar = sum([sinif_toplam_ucret_hesapla(row.get('Sınıf', '')) for _, row in muhasebe_bekleyen_df.iterrows()])

    c1, c2, c3 = st.columns(3)
    c1.metric("Toplam Bekleyen Marka Adedi", f"{toplam_marka_sayisi} Adet")
    c2.metric("Toplam Bekleyen Sınıf Adedi", f"{toplam_sinif_adedi} Sınıf")
    c3.metric("Toplam Bekleyen Tutar", f"{toplam_tutar:,.2f} TL")
    st.write("---")
    
    ozet_df = muhasebe_bekleyen_df[['Marka Adı', 'Sınıf', 'Satış Tarihi']].copy()
    if not ozet_df.empty:
        ozet_df.insert(ozet_df.columns.get_loc('Sınıf') + 1, 'Sınıf Adedi', [f"{sinif_adedi_hesapla(s)} Sınıf" for s in ozet_df['Sınıf']])
        ozet_df['Sınıf Toplam Harç Ücreti'] = [f"{sinif_toplam_ucret_hesapla(s):,.2f} TL" for s in ozet_df['Sınıf']]
        gosterge_df = ozet_df[['Marka Adı', 'Sınıf', 'Sınıf Adedi', 'Satış Tarihi', 'Sınıf Toplam Harç Ücreti']]
    else:
        gosterge_df = pd.DataFrame(columns=['Marka Adı', 'Sınıf', 'Sınıf Adedi', 'Satış Tarihi', 'Sınıf Toplam Harç Ücreti'])
    st.dataframe(gosterge_df, use_container_width=True)

elif is_muhasebe and st.session_state.aktif_sayfa == "Başvuru Beklemede Raporu":
    if st.button("⬅️ Geri Çık"): sayfa_degistir("Ana Sayfa")
    st.markdown("<h2>⏳ Başvuru Beklemede Raporu</h2>", unsafe_allow_html=True)
    basvuru_bekleyen_df = df[df['Durum'].astype(str).str.strip() == "Başvuru Beklemede"]
    toplam_marka_sayisi = basvuru_bekleyen_df['Marka Adı'].nunique()
    toplam_sinif_adedi = sum([sinif_adedi_hesapla(s) for s in basvuru_bekleyen_df['Sınıf'].dropna()])
    toplam_tutar = sum([sinif_toplam_ucret_hesapla(row.get('Sınıf', '')) for _, row in basvuru_bekleyen_df.iterrows()])

    c1, c2, c3 = st.columns(3)
    c1.metric("Toplam Başvuru Marka Adedi", f"{toplam_marka_sayisi} Adet")
    c2.metric("Toplam Başvuru Sınıf Adedi", f"{toplam_sinif_adedi} Sınıf")
    c3.metric("Toplam Başvuru Ücret Tutarı", f"{toplam_tutar:,.2f} TL")
    st.write("---")
    
    ozet_df = basvuru_bekleyen_df[['Marka Adı', 'Sınıf', 'Satış Tarihi']].copy()
    if not ozet_df.empty:
        ozet_df['Sınıf Adedi'] = [f"{sinif_adedi_hesapla(row.get('Sınıf', ''))} Sınıf" for _, row in basvuru_bekleyen_df.iterrows()]
        ozet_df['Sınıf Toplam Harç Ücreti'] = [f"{sinif_toplam_ucret_hesapla(row.get('Sınıf', ''))}:,.2f TL" for _, row in basvuru_bekleyen_df.iterrows()]
        gosterge_df = ozet_df
    else:
        gosterge_df = pd.DataFrame(columns=['Marka Adı', 'Sınıf', 'Satış Tarihi', 'Sınıf Adedi', 'Sınıf Toplam Harç Ücreti'])
    st.dataframe(gosterge_df, use_container_width=True)

elif is_muhasebe and st.session_state.aktif_sayfa == "Kurum İncelemesinde Raporu":
    if st.button("⬅️ Geri Çık"): sayfa_degistir("Ana Sayfa")
    st.markdown("<h2>🔍 Kurum İncelemesinde Raporu</h2>", unsafe_allow_html=True)
    kurum_inceleme_df = df[df['Durum'].astype(str).str.strip() == "Kurum İncelemesinde"]
    st.metric("Toplam Marka Adedi", f"{kurum_inceleme_df['Marka Adı'].nunique()} Adet")
    st.write("---")
    
    kurum_ozet_df = kurum_inceleme_df[['Marka Adı', 'Sınıf', 'Satış Tarihi', 'Başvuru Tarihi', 'Başvuru No']].copy()
    if not kurum_ozet_df.empty:
        kurum_ozet_df.insert(kurum_ozet_df.columns.get_loc('Sınıf') + 1, 'Sınıf Adedi', [f"{sinif_adedi_hesapla(s)} Sınıf" for s in kurum_ozet_df['Sınıf']])
        gosterge_df = kurum_ozet_df.rename(columns={'Başvuru No': 'Başvuru Numarası'})
    else:
        gosterge_df = pd.DataFrame(columns=['Marka Adı', 'Sınıf', 'Sınıf Adedi', 'Satış Tarihi', 'Başvuru Tarihi', 'Başvuru Numarası'])
    st.dataframe(gosterge_df, use_container_width=True)

elif is_muhasebe and st.session_state.aktif_sayfa == "Yayında Raporu":
    if st.button("⬅️ Geri Çık"): sayfa_degistir("Ana Sayfa")
    st.markdown("<h2>📰 Yayında Raporu</h2>", unsafe_allow_html=True)
    yayinda_df = df[df['Durum'].astype(str).str.strip() == "Yayında"].copy()
    st.metric("Toplam Marka Adedi", f"{yayinda_df['Marka Adı'].nunique()} Adet")
    st.write("---")
    
    bugun = datetime.now().date()
    kalan_gunler = []
    for _, r_item in yayinda_df.iterrows():
        try:
            dt_bitis = pd.to_datetime(str(r_item.get('Yayın Bitiş Tarihi', '')).strip(), format='%d/%m/%Y').date()
            fark_gun = (dt_bitis - bugun).days
            if fark_gun < 0: kalan_gunler.append(f"Süresi Doldu ({abs(fark_gun)} gün önce)")
            elif fark_gun == 0: kalan_gunler.append("Bugün Son Gün! ⚠️")
            else: kalan_gunler.append(f"{fark_gun} Gün Kaldı")
        except: kalan_gunler.append("Bilinmiyor")
    ozet_df = yayinda_df[['Marka Adı', 'Satış Tarihi', 'Başvuru No']].copy()
    ozet_df['Kalan Süre'] = kalan_gunler
    if not ozet_df.empty:
        gosterge_df = ozet_df.rename(columns={'Başvuru No': 'Başvuru Numarası'})[['Marka Adı', 'Satış Tarihi', 'Kalan Süre', 'Başvuru Numarası']]
    else:
        gosterge_df = pd.DataFrame(columns=['Marka Adı', 'Satış Tarihi', 'Kalan Süre', 'Başvuru Numarası'])
    st.dataframe(gosterge_df, use_container_width=True)

elif is_muhasebe and st.session_state.aktif_sayfa == "İtiraz Savunma Bekliyor Raporu":
    if st.button("⬅️ Geri Çık"): sayfa_degistir("Ana Sayfa")
    st.markdown("<h2>⚠️ İtiraz Savunma Bekliyor Raporu</h2>", unsafe_allow_html=True)
    itiraz_bekleyen_df = df[df['Durum'].astype(str).str.strip() == "İtiraz Geldi - Savunma Bekliyor"].copy()
    st.metric("Toplam Marka Adedi", f"{itiraz_bekleyen_df['Marka Adı'].nunique()} Adet")
    st.write("---")
    
    bugun = datetime.now().date()
    kalan_gunler_listesi = []
    for _, r_item in itiraz_bekleyen_df.iterrows():
        savunma_son_str = str(r_item.get('Savunma Son Günü', '')).strip()
        try:
            dt_son = pd.to_datetime(savunma_son_str, format='%d/%m/%Y').date()
            fark_gun = (dt_son - bugun).days
            if fark_gun < 0: kalan_gunler_listesi.append(f"Süresi Doldu ({abs(fark_gun)} gün önce)")
            elif fark_gun == 0: kalan_gunler_listesi.append("Bugün Son Gün! ⚠️")
            else: kalan_gunler_listesi.append(f"{fark_gun} Gün Kaldı")
        except:
            kalan_gunler_listesi.append("Bilinmiyor")

    rapor_goruntule_df = itiraz_bekleyen_df[['Marka Adı', 'Danışman', 'Operasyon Yetkilisi', 'İtiraz Tarihi', 'Savunma Son Günü', 'Savunma Durumu', 'Savunma Ücreti KDV Dahil', 'Evrak Numarası', 'Savunma Ücreti Alındı', 'Başvuru No']].copy() if not itiraz_bekleyen_df.empty else pd.DataFrame(columns=['Marka Adı', 'Danışman', 'Operasyon Yetkilisi', 'İtiraz Tarihi', 'Savunma Son Günü', 'Savunma Durumu', 'Savunma Ücreti KDV Dahil', 'Evrak Numarası', 'Savunma Ücreti Alındı', 'Başvuru No'])
    rapor_goruntule_df['Kalan Süre'] = kalan_gunler_listesi
    
    kolon_sirasi = ['Marka Adı', 'Danışman', 'Operasyon Yetkilisi', 'İtiraz Tarihi', 'Savunma Son Günü', 'Kalan Süre', 'Savunma Durumu', 'Savunma Ücreti KDV Dahil', 'Evrak Numarası', 'Savunma Ücreti Alındı', 'Başvuru No']
    rapor_goruntule_df = rapor_goruntule_df[[c for c in kolon_sirasi if c in rapor_goruntule_df.columns]]
    
    st.dataframe(rapor_goruntule_df.rename(columns={'Başvuru No': 'Başvuru Numarası', 'Savunma Ücreti KDV Dahil': 'Savunma Ücreti (KDV Dahil)'}), use_container_width=True)

elif is_muhasebe and st.session_state.aktif_sayfa == "Savunma Yapıldı Raporu":
    if st.button("⬅️ Geri Çık"): sayfa_degistir("Ana Sayfa")
    st.markdown("<h2>📋 Savunma Yapıldı Raporu</h2>", unsafe_allow_html=True)
    savunma_yapildi_df = df[df['Durum'].astype(str).str.strip() == "Savunma Yapıldı"].copy()
    st.metric("Toplam Marka Adedi", f"{savunma_yapildi_df['Marka Adı'].nunique()} Adet")
    st.write("---")
    
    rapor_goruntule_df = savunma_yapildi_df[['Marka Adı', 'Danışman', 'Operasyon Yetkilisi', 'İtiraz Tarihi', 'Savunma Son Günü', 'Savunma Yapıldı Tarihi', 'Savunma Durumu', 'Savunma Ücreti KDV Dahil', 'Evrak Numarası', 'Savunma Ücreti Alındı', 'Başvuru No']].copy() if not savunma_yapildi_df.empty else pd.DataFrame(columns=['Marka Adı', 'Danışman', 'Operasyon Yetkilisi', 'İtiraz Tarihi', 'Savunma Son Günü', 'Savunma Yapıldı Tarihi', 'Savunma Durumu', 'Savunma Ücreti KDV Dahil', 'Evrak Numarası', 'Savunma Ücreti Alındı', 'Başvuru No'])
    
    kolon_sirasi = ['Marka Adı', 'Danışman', 'Operasyon Yetkilisi', 'İtiraz Tarihi', 'Savunma Son Günü', 'Savunma Yapıldı Tarihi', 'Savunma Durumu', 'Savunma Ücreti KDV Dahil', 'Evrak Numarası', 'Savunma Ücreti Alındı', 'Başvuru No']
    rapor_goruntule_df = rapor_goruntule_df[[c for c in kolon_sirasi if c in rapor_goruntule_df.columns]]
    
    st.dataframe(rapor_goruntule_df.rename(columns={'Başvuru No': 'Başvuru Numarası', 'Savunma Ücreti KDV Dahil': 'Savunma Ücreti (KDV Dahil)'}), use_container_width=True)

elif is_muhasebe and st.session_state.aktif_sayfa == "Savunma Yapılmadı Raporu":
    if st.button("⬅️ Geri Çık"): sayfa_degistir("Ana Sayfa")
    st.markdown("<h2>❌ Savunma Yapılmadı Raporu</h2>", unsafe_allow_html=True)
    savunma_yapilmadi_df = df[df['Durum'].astype(str).str.strip() == "Savunma Yapılmadı"].copy()
    st.metric("Toplam Marka Adedi", f"{savunma_yapilmadi_df['Marka Adı'].nunique()} Adet")
    st.write("---")
    
    rapor_goruntule_df = savunma_yapilmadi_df[['Marka Adı', 'Danışman', 'Operasyon Yetkilisi', 'İtiraz Tarihi', 'Savunma Son Günü', 'Savunma Durumu', 'Savunma Ücreti KDV Dahil', 'Evrak Numarası', 'Savunma Ücreti Alındı', 'Başvuru No']].copy() if not savunma_yapilmadi_df.empty else pd.DataFrame(columns=['Marka Adı', 'Danışman', 'Operasyon Yetkilisi', 'İtiraz Tarihi', 'Savunma Son Günü', 'Savunma Durumu', 'Savunma Ücreti KDV Dahil', 'Evrak Numarası', 'Savunma Ücreti Alındı', 'Başvuru No'])
    
    kolon_sirasi = ['Marka Adı', 'Danışman', 'Operasyon Yetkilisi', 'İtiraz Tarihi', 'Savunma Son Günü', 'Savunma Durumu', 'Savunma Ücreti KDV Dahil', 'Evrak Numarası', 'Savunma Ücreti Alındı', 'Başvuru No']
    rapor_goruntule_df = rapor_goruntule_df[[c for c in kolon_sirasi if c in rapor_goruntule_df.columns]]
    
    st.dataframe(rapor_goruntule_df.rename(columns={'Başvuru No': 'Başvuru Numarası', 'Savunma Ücreti KDV Dahil': 'Savunma Ücreti (KDV Dahil)'}), use_container_width=True)

elif is_muhasebe and st.session_state.aktif_sayfa == "Tescil Tebliğ Beklemede Raporu":
    if st.button("⬅️ Geri Çık"): sayfa_degistir("Ana Sayfa")
    st.markdown("<h2>📌 Tescil Tebliğ Beklemede Raporu</h2>", unsafe_allow_html=True)
    tescil_bekleyen_df = df[df['Durum'].astype(str).str.strip() == "Tescil Tebliğ Beklemede"].copy()
    st.metric("Toplam Marka Adedi", f"{tescil_bekleyen_df['Marka Adı'].nunique()} Adet")
    st.write("---")
    gosterge_df = tescil_bekleyen_df[['Marka Adı', 'Satış Tarihi', 'Başvuru No']].rename(columns={'Başvuru No': 'Başvuru Numarası'}) if not tescil_bekleyen_df.empty else pd.DataFrame(columns=['Marka Adı', 'Satış Tarihi', 'Başvuru Numarası'])
    st.dataframe(gosterge_df, use_container_width=True)

elif is_muhasebe and st.session_state.aktif_sayfa == "Tescil Tebliğ Arandı Raporu":
    if st.button("⬅️ Geri Çık"): sayfa_degistir("Ana Sayfa")
    st.markdown("<h2>💳 Tescil Tebliğ Arandı Raporu</h2>", unsafe_allow_html=True)
    arandi_df = df[df['Durum'].astype(str).str.strip() == "Tescil Tebliğ Edildi Müşteri Arandı"].copy()
    st.metric("Toplam Marka Adedi", f"{arandi_df['Marka Adı'].nunique()} Adet")
    st.write("---")
    rapor_goruntule_df = arandi_df[['Marka Adı', 'Danışman', 'Operasyon Yetkilisi', 'Tescil Tebliğ Tarihi', 'Tescil Son Ödeme Tarihi', 'Fatura No', 'Fatura Tarihi', 'Tescil Harç Tutarı', 'Ödeme Tarihi']].copy() if not arandi_df.empty else pd.DataFrame(columns=['Marka Adı', 'Danışman', 'Operasyon Yetkilisi', 'Tescil Tebliğ Tarihi', 'Tescil Son Ödeme Tarihi', 'Fatura No', 'Fatura Tarihi', 'Tescil Harç Tutarı', 'Ödeme Tarihi'])
    st.dataframe(rapor_goruntule_df.rename(columns={'Tescil Harç Tutarı': 'Harç Tutarı (TL)'}), use_container_width=True)

elif is_muhasebe and st.session_state.aktif_sayfa == "Ödeme Sözü Verenler Raporu":
    if st.button("⬅️ Geri Çık"): sayfa_degistir("Ana Sayfa")
    st.markdown("<h2>📅 Ödeme Sözü Verenler Raporu</h2>", unsafe_allow_html=True)
    sozu_verenler_df = df[df['Durum'].astype(str).str.strip() == "Ödeme Sözü Verenler"].copy()
    st.metric("Toplam Marka Adedi", f"{sozu_verenler_df['Marka Adı'].nunique()} Adet")
    st.write("---")
    
    bugun = datetime.now().date()
    kalan_gunler_listesi = []
    for _, r_item in sozu_verenler_df.iterrows():
        son_odeme_str = str(r_item.get('Tescil Son Ödeme Tarihi', '')).strip()
        try:
            dt_son = pd.to_datetime(son_odeme_str, format='%d/%m/%Y').date()
            fark_gun = (dt_son - bugun).days
            if fark_gun < 0: kalan_gunler_listesi.append(f"Süresi Doldu ({abs(fark_gun)} gün önce)")
            elif fark_gun == 0: kalan_gunler_listesi.append("Bugün Son Gün! ⚠️")
            else: kalan_gunler_listesi.append(f"{fark_gun} Gün Kaldı")
        except:
            kalan_gunler_listesi.append("Bilinmiyor")

    rapor_goruntule_df = sozu_verenler_df[['Marka Adı', 'Danışman', 'Operasyon Yetkilisi', 'Tescil Tebliğ Tarihi', 'Tescil Son Ödeme Tarihi', 'Ödeme Sözü Tarihi', 'Fatura No', 'Fatura Tarihi', 'Tescil Harç Tutarı', 'Ödeme Sözü Güncelleme Sayısı']].copy() if not sozu_verenler_df.empty else pd.DataFrame(columns=['Marka Adı', 'Danışman', 'Operasyon Yetkilisi', 'Tescil Tebliğ Tarihi', 'Tescil Son Ödeme Tarihi', 'Ödeme Sözü Tarihi', 'Fatura No', 'Fatura Tarihi', 'Tescil Harç Tutarı', 'Ödeme Sözü Güncelleme Sayısı'])
    rapor_goruntule_df['Kalan Süre'] = kalan_gunler_listesi
    
    kolon_sirasi = ['Marka Adı', 'Danışman', 'Operasyon Yetkilisi', 'Tescil Tebliğ Tarihi', 'Tescil Son Ödeme Tarihi', 'Kalan Süre', 'Ödeme Sözü Tarihi', 'Ödeme Sözü Güncelleme Sayısı', 'Fatura No', 'Fatura Tarihi', 'Tescil Harç Tutarı']
    rapor_goruntule_df = rapor_goruntule_df[[c for c in kolon_sirasi if c in rapor_goruntule_df.columns]]
    
    st.dataframe(rapor_goruntule_df.rename(columns={'Tescil Harç Tutarı': 'Harç Tutarı (TL)', 'Ödeme Sözü Güncelleme Sayısı': 'Kaç Kez Güncellendi'}), use_container_width=True)

elif is_muhasebe and st.session_state.aktif_sayfa == "Tescil Kurum Ödemesi Bekleyen Raporu":
    if st.button("⬅️ Geri Çık"): sayfa_degistir("Ana Sayfa")
    st.markdown("<h2>⏳ Tescil Kurum Ödemesi Bekleyen Raporu</h2>", unsafe_allow_html=True)
    kurum_odeme_bekleyen_df = df[df['Durum'].astype(str).str.strip() == "Tescil Kurum Ödemesi Bekleyen"].copy()
    st.metric("Toplam Marka Adedi", f"{kurum_odeme_bekleyen_df['Marka Adı'].nunique()} Adet")
    st.write("---")
    
    bugun = datetime.now().date()
    kalan_gunler_listesi = []
    for _, r_item in kurum_odeme_bekleyen_df.iterrows():
        son_odeme_str = str(r_item.get('Tescil Son Ödeme Tarihi', '')).strip()
        try:
            dt_son = pd.to_datetime(son_odeme_str, format='%d/%m/%Y').date()
            fark_gun = (dt_son - bugun).days
            if fark_gun < 0: kalan_gunler_listesi.append(f"Süresi Doldu ({abs(fark_gun)} gün önce)")
            elif fark_gun == 0: kalan_gunler_listesi.append("Bugün Son Gün! ⚠️")
            else: kalan_gunler_listesi.append(f"{fark_gun} Gün Kaldı")
        except:
            kalan_gunler_listesi.append("Bilinmiyor")

    rapor_goruntule_df = kurum_odeme_bekleyen_df[['Marka Adı', 'Danışman', 'Operasyon Yetkilisi', 'Tescil Tebliğ Tarihi', 'Tescil Son Ödeme Tarihi', 'Fatura No', 'Fatura Tarihi']].copy() if not kurum_odeme_bekleyen_df.empty else pd.DataFrame(columns=['Marka Adı', 'Danışman', 'Operasyon Yetkilisi', 'Tescil Tebliğ Tarihi', 'Tescil Son Ödeme Tarihi', 'Fatura No', 'Fatura Tarihi'])
    rapor_goruntule_df['Kalan Süre'] = kalan_gunler_listesi
    
    kolon_sirasi = ['Marka Adı', 'Danışman', 'Operasyon Yetkilisi', 'Tescil Tebliğ Tarihi', 'Tescil Son Ödeme Tarihi', 'Kalan Süre', 'Fatura No', 'Fatura Tarihi']
    rapor_goruntule_df = rapor_goruntule_df[[c for c in kolon_sirasi if c in rapor_goruntule_df.columns]]

    st.dataframe(rapor_goruntule_df, use_container_width=True)

elif is_muhasebe and st.session_state.aktif_sayfa == "Fiyatlandırma and Harç Yönetimi":
    if st.button("⬅️ Geri Çık"): sayfa_degistir("Ana Sayfa")
    st.markdown("<h2>⚙️ Profesyonel Fiyatlandırma and Harç Yönetimi (1 - 45 Sınıf)</h2>", unsafe_allow_html=True)
    
    mevcut_h1 = float(st.session_state.sinif_harclari.get(1, {"harc": 2820.0})["harc"])
    mevcut_h3_bedel = float(st.session_state.sinif_harclari.get(4, {"harc": 3150.0})["harc"] - st.session_state.sinif_harclari.get(3, {"harc": 3150.0})["harc"]) if len(st.session_state.sinif_harclari) >= 4 else 3150.0
    mevcut_ortak_avukat = float(list(st.session_state.sinif_harclari.values())[0]["avukat"]) if st.session_state.sinif_harclari else 750.0

    col_k1, col_k2, col_k3 = st.columns(3)
    giris_h1 = col_k1.number_input("1. Sınıf Bedeli (TL)", value=float(mevcut_h1), step=50.0, format="%.2f")
    giris_h3_bedel = col_k2.number_input("3. Sınıf Bedeli (TL)", value=float(mevcut_h3_bedel), step=50.0, format="%.2f")
    ortak_avukat_input = col_k3.number_input("Tüm Sınıflar İçin Ortak Avukat Ücreti (TL)", value=float(mevcut_ortak_avukat), step=50.0, format="%.2f")

    col_e1, col_e2, col_e3, col_e4 = st.columns(4)
    tescil_harc_input = col_e1.number_input("Tescil Harç Bedeli (TL)", value=float(st.session_state.tescil_harc_bedeli), step=50.0, format="%.2f")
    savunma_harc_input = col_e2.number_input("Savunma Harç Bedeli (TL)", value=float(st.session_state.savunma_harc_bedeli), step=50.0, format="%.2f")
    bildirim_tutar_input = col_e3.number_input("Bildirim Tescil Ödemesi (TL)", value=float(st.session_state.bildirim_tescil_tutar), step=100.0, format="%.2f")
    kdv_orani_input = col_e4.number_input("KDV Oranı (%)", value=float(st.session_state.kdv_orani), step=1.0, format="%.2f")

    st.write("---")
    tablo_verileri = []
    h1 = giris_h1
    tablo_verileri.append({"Sınıf Adedi": 1, "Harç (TL)": h1, "Avukat (TL)": ortak_avukat_input, "Sınıf Toplam Harç Ücreti": h1 + ortak_avukat_input})
    h2 = giris_h1 + giris_h1
    tablo_verileri.append({"Sınıf Adedi": 2, "Harç (TL)": h2, "Avukat (TL)": ortak_avukat_input, "Sınıf Toplam Harç Ücreti": h2 + ortak_avukat_input})
    h3 = giris_h1 + giris_h1 + giris_h3_bedel
    tablo_verileri.append({"Sınıf Adedi": 3, "Harç (TL)": h3, "Avukat (TL)": ortak_avukat_input, "Sınıf Toplam Harç Ücreti": h3 + ortak_avukat_input})
    onceki_h = h3
    for i in range(4, 46):
        onceki_h += giris_h3_bedel
        tablo_verileri.append({"Sınıf Adedi": i, "Harç (TL)": onceki_h, "Avukat (TL)": ortak_avukat_input, "Sınıf Toplam Harç Ücreti": onceki_h + ortak_avukat_input})
    
    st.data_editor(pd.DataFrame(tablo_verileri), disabled=True, hide_index=True, use_container_width=True)

    if st.button("💾 Tüm Sınıf Fiyatlarını and Ücretleri Kaydet", use_container_width=True):
        yeni_sozluk, save_list = {}, []
        calc_h1, calc_h2, calc_h3 = giris_h1, giris_h1 + giris_h1, giris_h1 + giris_h1 + giris_h3_bedel
        cur_h = calc_h3
        for i in range(1, 46):
            if i == 1: h_fiyat = calc_h1
            elif i == 2: h_fiyat = calc_h2
            elif i == 3: h_fiyat = calc_h3
            else:
                cur_h += giris_h3_bedel
                h_fiyat = cur_h
            yeni_sozluk[i] = {"harc": h_fiyat, "avukat": float(ortak_avukat_input)}
            save_list.append({"Sınıf Adedi": i, "Harç": h_fiyat, "Avukat": float(ortak_avukat_input)})
            
        st.session_state.sinif_harclari = yeni_sozluk
        pd.DataFrame(save_list).to_csv(HARC_CONFIG_FILE, index=False, encoding='utf-8-sig', sep=';')
        
        st.session_state.tescil_harc_bedeli = float(tescil_harc_input)
        st.session_state.savunma_harc_bedeli = float(savunma_harc_input)
        st.session_state.bildirim_tescil_tutar = float(bildirim_tutar_input)
        st.session_state.kdv_orani = float(kdv_orani_input)
        
        pd.DataFrame({
            "Tescil Harç Bedeli": [st.session_state.tescil_harc_bedeli], "Savunma Harç Bedeli": [st.session_state.savunma_harc_bedeli],
            "Bildirim Tescil Tutar": [st.session_state.bildirim_tescil_tutar], "KDV Oranı": [st.session_state.kdv_orani]
        }).to_csv(EK_HARC_CONFIG_FILE, index=False, encoding='utf-8-sig', sep=';')
        
        st.success("🎉 Başarıyla kaydedildi!")
        import time; time.sleep(1.2)
        st.rerun()

elif not is_muhasebe and st.session_state.aktif_sayfa == "Yeni Satış Giriş":
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
        
        if tutar_input.strip():
            try:
                kdv_haric_gosterge = float(tutar_input.strip().replace(",", ".")) / (1 + (st.session_state.kdv_orani / 100.0))
                c2.markdown(f"💡 **KDV Hariç Tutar:** `{kdv_haric_gosterge:,.2f} TL`")
            except: pass

        st.write("")
        guncel_bildirim_tutar_str = f"{st.session_state.bildirim_tescil_tutar:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        bilgilendirme_onayi = st.checkbox(f"4 ila 6 ay sonra tescil ödemesinin {guncel_bildirim_tutar_str} TL + KDV olduğunu müşteriye bildirdim.")
        
        if st.form_submit_button("Satışı Kaydet"):
            dogru_tarihi = tarih_birlestir_ve_formatla(dogru_tarihi_ham)
            s_tarihi = tarih_birlestir_ve_formatla(s_tarihi_ham)
            if not m_adi.strip() or not ad_soyad.strip() or not sinif or not tutar_input.strip():
                st.error("❌ Lütfen zorunlu alanları doldurunuz.")
            elif not bilgilendirme_onayi:
                st.error("❌ Lütfen müşteriye tescil ödemesini bildirdiğinizi onaylayın.")
            else:
                anlik_hesaplanan_maliyet = sinif_toplam_ucret_hesapla(",".join(sinif))
                
                new_row = {
                    "Marka Adı": m_adi.strip(), "Ad Soyad": ad_soyad.strip(), "TC": tc.strip(), "Telefon": tel.strip(), "E-Mail": email.strip(),
                    "Doğum Tarihi": dogru_tarihi, "İl": il, "Sınıf": ",".join(sinif), "Ödeme": odeme, 
                    "Satış Tarihi": s_tarihi, "Tutar": tutar_input.strip(), "Durum": "Muhasebe Onayı Bekliyor", 
                    "Danışman": aktif_kullanici_ad, "Fatura No": "", "Fatura Tarihi": "", "Başvuru No": "", "Başvuru Tarihi": "", "Sonraki Aşama Seçimi": "", "İtiraz Tarihi": "", "Savunma Son Günü": "", "Tescil Tebliğ Tarihi": "", "Tescil Son Ödeme Tarihi": "", "Ödeme Tarihi": "", "Sabitlenen Maliyet": str(anlik_hesaplanan_maliyet), "Ödeme Sözü Tarihi": "", "Operasyon Yetkilisi": "", "Ödeme Sözü Güncelleme Sayısı": "0",
                    "Savunma Durumu": "", "Savunma Ücreti KDV Dahil": "", "Evrak Numarası": "", "Savunma Ücreti Alındı": "Hayır", "Savunma Yapıldı Tarihi": ""
                }
                guncel_df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                veriyi_kaydet_ve_yedekle(guncel_df)
                
                st.success("✅ Satış başarıyla kaydedildi and yedeklendi!")
                import time; time.sleep(1.5)
                st.session_state.aktif_sayfa = "Ana Sayfa"
                st.rerun()

elif not is_muhasebe and st.session_state.aktif_sayfa == "Satışlarım":
    if st.button("⬅️ Geri Çık"): sayfa_degistir("Ana Sayfa")
    mevcut_ay, mevcut_yil = datetime.now().strftime("%m"), str(datetime.now().year)
    st.markdown(f"<h2>📅 Satışlarım (Bu Ay: {mevcut_ay}/{mevcut_yil})</h2>", unsafe_allow_html=True)
    
    df['Danisman_Temp'] = df['Danışman'].astype(str).str.strip().str.upper()
    danisman_df = df[df['Danisman_Temp'] == aktif_kullanici_ad].copy()
    
    def guvenli_bu_ay_filtrele(row):
        try:
            f_tar = row.get('Fatura Tarihi', '')
            if pd.isna(f_tar) or str(f_tar).strip() == '' or str(f_tar).lower() == 'nan':
                return False
            dt = pd.to_datetime(str(f_tar).strip(), format='%d/%m/%Y', errors='coerce')
            if pd.isna(dt):
                dt = pd.to_datetime(str(f_tar).strip(), errors='coerce')
            if pd.isna(dt):
                return False
            return f"{dt.month:02d}" == mevcut_ay and str(dt.year) == mevcut_yil
        except:
            return False

    if not danisman_df.empty:
        danisman_df = danisman_df[danisman_df.apply(guvenli_bu_ay_filtrele, axis=1)]
        
    danisman_df = danisman_df.drop(columns=['Danisman_Temp'], errors='ignore')
    
    toplam_ciro = pd.to_numeric(danisman_df['Tutar'], errors='coerce').fillna(0).sum()
    c1, c2 = st.columns(2)
    c1.metric("Bu Ay Satış Adedi", len(danisman_df))
    c2.metric("Bu Ay Toplam Ciro (TL)", f"{toplam_ciro:,.2f} TL")
    st.write("---")
    
    if not danisman_df.empty and 'Sınıf' in danisman_df.columns:
        sinif_adedi_listesi = [f"{sinif_adedi_hesapla(s)} Sınıf" for s in danisman_df['Sınıf']]
        danisman_df.insert(danisman_df.columns.get_loc('Sınıf') + 1, 'Sınıf Adedi', sinif_adedi_listesi)

    st.dataframe(danisman_df, use_container_width=True)

elif not is_muhasebe and st.session_state.aktif_sayfa == "Genel Satışlarım":
    if st.button("⬅️ Geri Çık"): sayfa_degistir("Ana Sayfa")
    st.markdown(f"<h2>📊 Genel Satışlarım</h2>", unsafe_allow_html=True)
    df['Danisman_Temp'] = df['Danışman'].astype(str).str.strip().str.upper()
    danisman_df = df[df['Danisman_Temp'] == aktif_kullanici_ad].copy()
    danisman_df = danisman_df.drop(columns=['Danisman_Temp'], errors='ignore')
    st.dataframe(danisman_df, use_container_width=True)

elif is_muhasebe and st.session_state.aktif_sayfa == "Danışman Satışlarını Düzenle":
    if st.button("⬅️ Geri Çık"): sayfa_degistir("Ana Sayfa")
    st.markdown("<h2>🛠️ Danışman Satışlarını Düzenleme Paneli</h2>", unsafe_allow_html=True)
    if df.empty:
        st.info("Sistemde kayıtlı hiç satış bulunmuyor.")
    else:
        arama_input = st.text_input("🔍 Marka Adı ile Ara", placeholder="Marka adı yazın...")
        filtrelenmis_df = df.copy()
        if arama_input.strip(): filtrelenmis_df = filtrelenmis_df[filtrelenmis_df['Marka Adı'].astype(str).str.contains(arama_input.strip(), case=False, na=False)]
        marka_listesi_tum = filtrelenmis_df['Marka Adı'].astype(str).tolist()
        
        if not marka_listesi_tum: st.warning("Aramanızla eşleşen marka bulunamadı.")
        else:
            secilen_duzenle_marka = st.selectbox("Düzenlenecek Markayı Seçin", options=marka_listesi_tum)
            if secilen_duzenle_marka:
                d_row = df[df['Marka Adı'].astype(str) == secilen_duzenle_marka].iloc[0]
                with st.form("admin_satis_duzenle_form"):
                    st.markdown(f"### Marka: {d_row['Marka Adı']}")
                    c1, c2 = st.columns(2)
                    y_ad_soyad = c1.text_input("İsim Soyisim", value=str(d_row.get('Ad Soyad', '')))
                    y_tc = c1.text_input("TC", value=str(d_row.get('TC', '')))
                    y_tel = c1.text_input("Telefon", value=str(d_row.get('Telefon', '')))
                    y_email = c1.text_input("E-Mail", value=str(d_row.get('E-Mail', '')))
                    y_dogum = c1.text_input("Doğum Tarihi", value=str(d_row.get('Doğum Tarihi', '')))
                    
                    y_il = c2.text_input("İl", value=str(d_row.get('İl', '')))
                    y_sinif = c2.text_input("Sınıf", value=str(d_row.get('Sınıf', '')))
                    y_odeme = c2.text_input("Ödeme Türü", value=str(d_row.get('Ödeme', '')))
                    y_s_tarih = c2.text_input("Satış Tarihi", value=str(d_row.get('Satış Tarihi', '')))
                    y_tutar = c2.text_input("Tutar (TL)", value=str(d_row.get('Tutar', '')))
                    y_danisman = c2.text_input("Danışman", value=str(d_row.get('Danışman', '')))
                    
                    mevcut_kayitli_op = str(d_row.get('Operasyon Yetkilisi', '')).strip().upper()
                    varsayilan_op_secim = mevcut_kayitli_op if mevcut_kayitli_op in OPERASYON_YETKILILERI else (aktif_kullanici_ad if aktif_kullanici_ad in OPERASYON_YETKILILERI else OPERASYON_YETKILILERI[0])
                    y_operasyon = c2.selectbox("Operasyon Yetkilisi", options=OPERASYON_YETKILILERI, index=OPERASYON_YETKILILERI.index(varsayilan_op_secim))
                    
                    b_col1, b_col2, b_col3 = st.columns([1, 1, 2])
                    submitted_admin_edit = b_col1.form_submit_button("💾 Bilgileri Güncelle")
                    submitted_delete = b_col2.form_submit_button("🗑️ Kaydı Sil", type="primary")
                    
                    if submitted_admin_edit:
                        idx = df.index[df['Marka Adı'].astype(str) == secilen_duzenle_marka][0]
                        df.at[idx, 'Ad Soyad'] = y_ad_soyad.strip()
                        df.at[idx, 'TC'] = y_tc.strip()
                        df.at[idx, 'Telefon'] = y_tel.strip()
                        df.at[idx, 'E-Mail'] = y_email.strip()
                        df.at[idx, 'Doğum Tarihi'] = y_dogum.strip()
                        df.at[idx, 'İl'] = y_il.strip()
                        df.at[idx, 'Sınıf'] = y_sinif.strip()
                        df.at[idx, 'Ödeme'] = y_odeme.strip()
                        df.at[idx, 'Satış Tarihi'] = tarih_birlestir_ve_formatla(y_s_tarih)
                        df.at[idx, 'Tutar'] = y_tutar.strip()
                        df.at[idx, 'Danışman'] = y_danisman.strip().upper()
                        df.at[idx, 'Operasyon Yetkilisi'] = y_operasyon.strip().upper()
                        
                        yeni_maliyet = sinif_toplam_ucret_hesapla(y_sinif.strip())
                        df.at[idx, 'Sabitlenen Maliyet'] = str(yeni_maliyet)
                        
                        veriyi_kaydet_ve_yedekle(df)
                        st.session_state["success_msg"] = f"Başarılı! '{secilen_duzenle_marka}' bilgileri güncellendi and yedeklendi."
                        st.rerun()
                        
                    if submitted_delete:
                        df_yeni = df[df['Marka Adı'].astype(str) != secilen_duzenle_marka]
                        veriyi_kaydet_ve_yedekle(df_yeni)
                        st.session_state["success_msg"] = f"🗑️ '{secilen_duzenle_marka}' markasına ait kayıt silindi!"
                        st.rerun()
                        
                if "success_msg" in st.session_state:
                    st.success(st.session_state["success_msg"])
                    del st.session_state["success_msg"]

elif is_muhasebe and st.session_state.aktif_sayfa == "Tescil Tebliğ Edildi Müşteri Arandı":
    if st.button("⬅️ Geri Çık"): sayfa_degistir("Ana Sayfa")
    st.markdown("<h2>💳 Tescil Tebliğ Edildi Müşteri Arandı Ekranı</h2>", unsafe_allow_html=True)
    tescil_df = df[df['Durum'].astype(str).str.strip() == "Tescil Tebliğ Edildi Müşteri Arandı"]
    
    if tescil_df.empty: st.info("Bu aşamada işlem bekleyen marka bulunmuyor.")
    else:
        arama_tescil = st.text_input("🔍 Marka Ara", placeholder="Marka adı yazın...")
        if arama_tescil.strip(): tescil_df = tescil_df[tescil_df['Marka Adı'].astype(str).str.contains(arama_tescil.strip(), case=False, na=False)]
        
        if tescil_df.empty: st.warning("Aramanızla eşleşen marka bulunamadı.")
        else:
            secilen_tescil_marka = st.selectbox("İşlem Yapılacak Markayı Seçin", options=tescil_df['Marka Adı'].astype(str).tolist())
            if secilen_tescil_marka:
                t_row = tescil_df[tescil_df['Marka Adı'].astype(str) == secilen_tescil_marka].iloc[0]
                tescil_tarihi_str = t_row.get('Tescil Tebliğ Tarihi', '')
                
                son_odeme_tarihi_str = hesapla_tescil_son_odeme(tescil_tarihi_str)
                if son_odeme_tarihi_str:
                    idx_temp = df.index[df['Marka Adı'].astype(str) == str(secilen_tescil_marka)][0]
                    if str(df.at[idx_temp, 'Tescil Son Ödeme Tarihi']) != son_odeme_tarihi_str:
                        df.at[idx_temp, 'Tescil Son Ödeme Tarihi'] = son_odeme_tarihi_str
                        veriyi_kaydet_ve_yedekle(df)
                
                st.markdown(f"**Marka:** {t_row['Marka Adı']} | **Danışman:** *{t_row['Danışman']}*")
                c_op, c1, c2, c3, c4, c5 = st.columns([1, 1, 1, 1, 1, 1])
                
                otomatik_op = aktif_kullanici_ad if aktif_kullanici_ad in OPERASYON_YETKILILERI else OPERASYON_YETKILILERI[0]
                op_yetkilisi_input = c_op.text_input("Operasyon Yetkilisi*", value=otomatik_op, disabled=True)
                
                c1.markdown(f"**Tescil Tebliğ Tarihi**\n\n`{tescil_tarihi_str}`")
                c2.markdown(f"**TESCİL SON GÜNÜ**\n\n`{son_odeme_tarihi_str}`")
                tescil_fatura_no = c3.text_input("Tescil Fatura No", value="")
                odeme_gunu_ham = c4.text_input("Ödeme Günü", value="")
                odeme_sozu_tarihi_ham = c5.text_input("Ödeme Sözü Tarihi", value=str(t_row.get('Ödeme Sözü Tarihi', '')) if pd.notna(t_row.get('Ödeme Sözü Tarihi')) else "")
                
                b_col1, b_col2 = st.columns(2)
                with b_col1:
                    if st.button("⏳ Tescil Kurum Ödemesi Bekleyen Yap", use_container_width=True):
                        odeme_gunu = tarih_birlestir_ve_formatla(odeme_gunu_ham)
                        if not odeme_gunu.strip():
                            st.warning("⚠️ Lütfen Ödeme Günü alanını doldurunuz.")
                        else:
                            idx = df.index[df['Marka Adı'].astype(str) == str(secilen_tescil_marka)][0]
                            df.at[idx, 'Durum'] = "Tescil Kurum Ödemesi Bekleyen"
                            df.at[idx, 'Operasyon Yetkilisi'] = otomatik_op
                            df.at[idx, 'Fatura No'] = tescil_fatura_no.strip()
                            df.at[idx, 'Ödeme Tarihi'] = odeme_gunu.strip()
                            if son_odeme_tarihi_str:
                                df.at[idx, 'Tescil Son Ödeme Tarihi'] = son_odeme_tarihi_str
                            
                            veriyi_kaydet_ve_yedekle(df)
                            st.success(f"✅ Başarılı! Tescil Kurum Ödemesi Bekleyen aşamasına aktarıldı.")
                            import time; time.sleep(1.2); st.session_state.aktif_sayfa = "Tescil Kurum Ödemesi Bekleyen"; st.rerun()

                with b_col2:
                    if st.button("📅 Ödeme Sözü Verildi Yap", use_container_width=True):
                        odeme_sozu_tarihi = tarih_birlestir_ve_formatla(odeme_sozu_tarihi_ham)
                        if not odeme_sozu_tarihi.strip():
                            st.warning("⚠️ Lütfen Ödeme Sözü Tarihi alanını doldurunuz.")
                        else:
                            idx = df.index[df['Marka Adı'].astype(str) == str(secilen_tescil_marka)][0]
                            df.at[idx, 'Durum'] = "Ödeme Sözü Verenler"
                            df.at[idx, 'Operasyon Yetkilisi'] = otomatik_op
                            df.at[idx, 'Fatura No'] = tescil_fatura_no.strip()
                            df.at[idx, 'Ödeme Sözü Tarihi'] = odeme_sozu_tarihi.strip()
                            if son_odeme_tarihi_str:
                                df.at[idx, 'Tescil Son Ödeme Tarihi'] = son_odeme_tarihi_str
                            
                            veriyi_kaydet_ve_yedekle(df)
                            st.success(f"✅ Başarılı! Ödeme Sözü Verenler aşamasına aktarıldı.")
                            import time; time.sleep(1.2); st.session_state.aktif_sayfa = "Ödeme Sözü Verenler"; st.rerun()

elif is_muhasebe and st.session_state.aktif_sayfa in [
    "Muhasebe Onayı Bekliyor", "Başvuru Beklemede", "Kurum İncelemesinde", 
    "Yayında", "İtiraz Geldi - Savunma Bekliyor", "Savunma Yapıldı", "Savunma Yapılmadı", "Tescil Tebliğ Beklemede", 
    "Ödeme Sözü Verenler", "Tescil Tebliğ Edildi Müşteri Arandı", "Tescil Kurum Ödemesi Bekleyen", "Tescil Kuruma Ödendi", "Tescillendi 🎉", "Reddedildi ❌"
]:
    secilen_asama = st.session_state.aktif_sayfa
    if st.button("⬅️ Geri Çık"): sayfa_degistir("Ana Sayfa")
    
    top_col1, top_col2 = st.columns([2, 1])
    with top_col1: st.markdown(f"<h2>📂 Aşama: {secilen_asama}</h2>", unsafe_allow_html=True)
    with top_col2: arama_metni = st.text_input("🔍 Marka Ara", placeholder="Marka adı yazın...")
    
    asama_df = df[df['Durum'].astype(str).str.strip() == secilen_asama]
        
    if arama_metni.strip(): asama_df = asama_df[asama_df['Marka Adı'].astype(str).str.contains(arama_metni.strip(), case=False, na=False)]
    
    st.dataframe(asama_df, use_container_width=True)
    st.write("---")
    
    if secilen_asama == "Muhasebe Onayı Bekliyor":
        st.subheader("✅ Onay Bekleyen Satışları Faturalandır")
        if asama_df.empty:
            st.info("Bu aşamada kayıt bulunmuyor.")
        else:
            for i, row in asama_df.iterrows():
                with st.container():
                    st.markdown(f"Marka: **{row['Marka Adı']}** | Danışman: *{row['Danışman']}* | Tutar: **{row['Tutar']} TL**")
                    c1, c2, c3 = st.columns([1.5, 1.5, 1])
                    f_no = c1.text_input("Fatura No", key=f"f_no_{row['Marka Adı']}_{i}")
                    f_tarih_ham = c2.text_input("Fatura Tarihi", value=datetime.now().strftime("%d/%m/%Y"), key=f"f_tar_{row['Marka Adı']}_{i}")
                    with c3:
                        st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
                        if st.button("✅ Onayla", key=f"onay_btn_{row['Marka Adı']}_{i}"):
                            f_tarih = tarih_birlestir_ve_formatla(f_tarih_ham)
                            if f_no.strip() and f_tarih.strip():
                                idx = df.index[df['Marka Adı'].astype(str) == str(row['Marka Adı'])][0]
                                df.at[idx, 'Durum'] = "Başvuru Beklemede"
                                df.at[idx, 'Fatura No'] = f_no.strip()
                                df.at[idx, 'Fatura Tarihi'] = f_tarih.strip()
                                
                                veriyi_kaydet_ve_yedekle(df)
                                
                                st.success(f"✅ Onaylandı and yedeklendi.")
                                import time; time.sleep(1.2); st.rerun()
                            else: st.warning("Lütfen alanları doldurun.")
    elif secilen_asama == "Başvuru Beklemede":
        st.subheader("✏️ Başvuru Bilgilerini Girin and Kurum İncelemesine Aktarın")
        marka_listesi = asama_df['Marka Adı'].astype(str).tolist() if not asama_df.empty else []
        secilen_marka = st.selectbox("İşlem Yapılacak Markayı Seçin", options=marka_listesi) if marka_listesi else None
        if secilen_marka:
            s_row = df[(df['Durum'].astype(str).str.strip() == secilen_asama) & (df['Marka Adı'].astype(str) == secilen_marka)].iloc[0]
            with st.form(f"form_guncelle_{secilen_marka}"):
                c1, c2 = st.columns(2)
                c2.text_input("Danışman", value=str(s_row.get('Danışman', '')), disabled=True)
                
                b_no = c1.text_input("Başvuru No", value=str(s_row.get('Başvuru No', '')) if pd.notna(s_row.get('Başvuru No')) else "")
                b_tarih_ham = c2.text_input("Başvuru Tarihi", value=str(s_row.get('Başvuru Tarihi', '')) if pd.notna(s_row.get('Başvuru Tarihi')) else "")
                
                if st.form_submit_button("💾 Kaydı Güncelle"):
                    idx = df.index[(df['Durum'].astype(str).str.strip() == secilen_asama) & (df['Marka Adı'].astype(str) == secilen_marka)][0]
                    df.at[idx, 'Başvuru No'] = b_no.strip()
                    df.at[idx, 'Başvuru Tarihi'] = tarih_birlestir_ve_formatla(b_tarih_ham)
                    df.at[idx, 'Durum'] = "Kurum İncelemesinde"
                    
                    veriyi_kaydet_ve_yedekle(df)
                    
                    st.success(f"Başarılı! Kayıt güncellendi and yedeklendi.")
                    import time; time.sleep(1.2)
                    st.session_state.aktif_sayfa = "Kurum İncelemesinde"
                    st.rerun()
    elif secilen_asama == "Kurum İncelemesinde":
        st.subheader("✏️ Yayın Tarihini Girin and Yayına Aktarın")
        marka_listesi = asama_df['Marka Adı'].astype(str).tolist() if not asama_df.empty else []
        secilen_marka = st.selectbox("İşlem Yapılacak Markayı Seçin", options=marka_listesi) if marka_listesi else None
        if secilen_marka:
            s_row = df[(df['Durum'].astype(str).str.strip() == secilen_asama) & (df['Marka Adı'].astype(str) == secilen_marka)].iloc[0]
            with st.form(f"form_guncelle_kurum_{secilen_marka}"):
                c1, c2 = st.columns(2)
                c2.text_input("Danışman", value=str(s_row.get('Danışman', '')), disabled=True)
                c1.text_input("Başvuru No", value=str(s_row.get('Başvuru No', '')), disabled=True)
                
                yayin_tar_ham = c2.text_input("Yayın Tarihi (GG/AA/YYYY)", value="")
                
                if st.form_submit_button("💾 Kaydı Güncelle"):
                    yayin_tar = tarih_birlestir_ve_formatla(yayin_tar_ham)
                    if yayin_tar.strip():
                        try:
                            dt_yayin = datetime.strptime(yayin_tar, "%d/%m/%Y")
                            dt_bitis = ay_ekle(dt_yayin, 2)
                            dt_bitis_kontrol = resmi_tatil_ve_tatil_kontrol(dt_bitis)
                            yayin_bitis_str = dt_bitis_kontrol.strftime("%d/%m/%Y")
                            
                            idx = df.index[(df['Durum'].astype(str).str.strip() == secilen_asama) & (df['Marka Adı'].astype(str) == secilen_marka)][0]
                            df.at[idx, 'Yayın Tarihi'] = yayin_tar
                            df.at[idx, 'Yayın Bitiş Tarihi'] = yayin_bitis_str
                            df.at[idx, 'Durum'] = "Yayında"
                            
                            veriyi_kaydet_ve_yedekle(df)
                            
                            st.success("Güncellendi!")
                            import time; time.sleep(1.2)
                            st.session_state.aktif_sayfa = "Yayında"
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Tarih hesaplanırken hata oluştu: {e}")
                    else:
                        st.warning("Lütfen Yayın Tarihi alanını doldurunuz.")
    elif secilen_asama == "Yayında":
        st.subheader("✏️ Sonraki Aşamayı Seçin and Güncelleyin")
        marka_listesi = asama_df['Marka Adı'].astype(str).tolist() if not asama_df.empty else []
        secilen_marka = st.selectbox("İşlem Yapılacak Markayı Seçin", options=marka_listesi) if marka_listesi else None
        if secilen_marka:
            s_row = df[(df['Durum'].astype(str).str.strip() == secilen_asama) & (df['Marka Adı'].astype(str) == secilen_marka)].iloc[0]
            with st.form(f"form_guncelle_yayinda_{secilen_marka}"):
                c1, c2 = st.columns(2)
                c2.text_input("Danışman", value=str(s_row.get('Danışman', '')), disabled=True)
                c1.text_input("Başvuru No", value=str(s_row.get('Başvuru No', '')), disabled=True)
                
                sonraki_asama_secenekleri = ["İtiraz Geldi - Savunma Bekliyor", "Tescil Tebliğ Beklemede"]
                secilen_sonraki_asama = c1.selectbox("Sonraki Aşama Seçimi", options=sonraki_asama_secenekleri)
                
                if st.form_submit_button("💾 Kaydı Güncelle"):
                    idx = df.index[(df['Durum'].astype(str).str.strip() == secilen_asama) & (df['Marka Adı'].astype(str) == secilen_marka)][0]
                    df.at[idx, 'Durum'] = secilen_sonraki_asama
                    
                    veriyi_kaydet_ve_yedekle(df)
                    
                    st.success("Güncellendi!")
                    import time; time.sleep(1.2)
                    st.session_state.aktif_sayfa = secilen_sonraki_asama
                    st.rerun()
    elif secilen_asama == "İtiraz Geldi - Savunma Bekliyor":
        st.subheader("✏️ İtiraz and Savunma Bilgilerini Girin")
        marka_listesi = asama_df['Marka Adı'].astype(str).tolist() if not asama_df.empty else []
        secilen_marka = st.selectbox("İşlem Yapılacak Markayı Seçin", options=marka_listesi) if marka_listesi else None
        if secilen_marka:
            s_row = df[(df['Durum'].astype(str).str.strip() == secilen_asama) & (df['Marka Adı'].astype(str) == secilen_marka)].iloc[0]
            
            mevcut_itiraz_tar = str(s_row.get('İtiraz Tarihi', '')) if pd.notna(s_row.get('İtiraz Tarihi')) and str(s_row.get('İtiraz Tarihi')).lower() != 'nan' else ""
            hesaplanan_savunma_son = hesapla_savunma_son_gun(mevcut_itiraz_tar)
            
            otomatik_op = aktif_kullanici_ad if aktif_kullanici_ad in OPERASYON_YETKILILERI else OPERASYON_YETKILILERI[0]
            
            with st.form(f"form_guncelle_itiraz_teblig_{secilen_marka}"):
                c_op, c1, c2, c3 = st.columns(4)
                op_yetkilisi_input = c_op.text_input("Operasyon Yetkilisi*", value=otomatik_op, disabled=True)
                c1.text_input("Danışman", value=str(s_row.get('Danışman', '')), disabled=True)
                c2.text_input("Başvuru No", value=str(s_row.get('Başvuru No', '')) if pd.notna(s_row.get('Başvuru No')) else "", disabled=True)
                
                savunma_durumu_secim = c3.selectbox("Savunma Durumu", options=["Seçiniz...", "Savunma Yapıldı", "Savunma Yapılmadı"])
                
                itiraz_tar_ham = c_op.text_input("İtiraz Tebliğ Tarihi (GG/AA/YYYY)*", value=mevcut_itiraz_tar)
                c1.text_input("Savunma Son Günü", value=hesaplanan_savunma_son, disabled=True)
                
                mevcut_ucret = str(s_row.get('Savunma Ücreti KDV Dahil', '')) if pd.notna(s_row.get('Savunma Ücreti KDV Dahil')) else ""
                savunma_ucret_input = c2.text_input("Savunma Ücreti (KDV Dahil, TL)", value=mevcut_ucret)
                
                if savunma_ucret_input.strip():
                    try:
                        kdv_haric_savunma = float(savunma_ucret_input.strip().replace(",", ".")) / (1 + (st.session_state.kdv_orani / 100.0))
                        c2.markdown(f"💡 KDV Hariç: `{kdv_haric_savunma:,.2f} TL`")
                    except: pass

                mevcut_evrak = str(s_row.get('Evrak Numarası', '')) if pd.notna(s_row.get('Evrak Numarası')) else ""
                evrak_no_input = c3.text_input("Evrak Numarası", value=mevcut_evrak)
                
                mevcut_ucret_alindi = str(s_row.get('Savunma Ücreti Alındı', 'Hayri')).strip().lower() == 'evet'
                savunma_ucreti_alindi_check = c_op.checkbox("Savunma Ücreti Alındı", value=mevcut_ucret_alindi)
                
                st.write("")
                btn_col1, btn_col2, btn_col3 = st.columns(3)
                submitted_update = btn_col1.form_submit_button("💾 Kaydı Güncelle and Savunma Son Gününü Hesapla")
                submitted_savunmayapildi = btn_col2.form_submit_button("📋 Savunma Ücret Alındı")
                submitted_savunmayapilmadi = btn_col3.form_submit_button("❌ Savunma Yapılmadı Yap")
                
                if submitted_update:
                    itiraz_tar = tarih_birlestir_ve_formatla(itiraz_tar_ham)
                    if not op_yetkilisi_input.strip():
                        st.warning("⚠️ Lütfen Operasyon Yetkilisi seçiniz.")
                    elif not itiraz_tar.strip():
                        st.warning("⚠️ Lütfen İtiraz Tebliğ Tarihini giriniz.")
                    else:
                        try:
                            savunma_son_str = hesapla_savunma_son_gun(itiraz_tar)

                            idx = df.index[(df['Durum'].astype(str).str.strip() == secilen_asama) & (df['Marka Adı'].astype(str) == secilen_marka)][0]
                            df.at[idx, 'Operasyon Yetkilisi'] = otomatik_op
                            df.at[idx, 'İtiraz Tarihi'] = itiraz_tar
                            df.at[idx, 'Savunma Son Günü'] = savunma_son_str
                            df.at[idx, 'Savunma Durumu'] = savunma_durumu_secim if savunma_durumu_secim != "Seçiniz..." else "Savunma Yapıldı"
                            df.at[idx, 'Savunma Ücreti KDV Dahil'] = savunma_ucret_input.strip()
                            df.at[idx, 'Evrak Numarası'] = evrak_no_input.strip()
                            df.at[idx, 'Savunma Ücreti Alındı'] = "Evet" if savunma_ucreti_alindi_check else "Hayır"
                            
                            veriyi_kaydet_ve_yedekle(df)
                            
                            st.success(f"✅ Başarılı! İtiraz Tebliğ Tarihi kaydedildi. Savunma Son Günü: {savunma_son_str}")
                            import time; time.sleep(1.5)
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Tarih hesaplanırken hata oluştu: {e}")

                if submitted_savunmayapildi:
                    itiraz_tar = tarih_birlestir_ve_formatla(itiraz_tar_ham)
                    if not itiraz_tar.strip():
                        st.warning("⚠️ Lütfen İtiraz Tebliğ Tarihini giriniz.")
                    else:
                        try:
                            savunma_son_str = hesapla_savunma_son_gun(itiraz_tar)
                            bugunku_tarih = datetime.now().strftime("%d/%m/%Y")
                            idx = df.index[(df['Durum'].astype(str).str.strip() == secilen_asama) & (df['Marka Adı'].astype(str) == secilen_marka)][0]
                            df.at[idx, 'Durum'] = "Savunma Yapıldı"
                            df.at[idx, 'Operasyon Yetkilisi'] = otomatik_op
                            df.at[idx, 'İtiraz Tarihi'] = itiraz_tar
                            df.at[idx, 'Savunma Son Günü'] = savunma_son_str
                            df.at[idx, 'Savunma Durumu'] = "Savunma Yapıldı"
                            df.at[idx, 'Savunma Ücreti KDV Dahil'] = savunma_ucret_input.strip()
                            df.at[idx, 'Evrak Numarası'] = evrak_no_input.strip()
                            df.at[idx, 'Savunma Ücreti Alındı'] = "Evet" if savunma_ucreti_alindi_check else "Hayır"
                            df.at[idx, 'Savunma Yapıldı Tarihi'] = bugunku_tarih
                            
                            veriyi_kaydet_ve_yedekle(df)
                            st.success("✅ Başarılı! Savunma Yapıldı aşamasına aktarıldı.")
                            import time; time.sleep(1.2)
                            st.session_state.aktif_sayfa = "Savunma Yapıldı"
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Hata oluştu: {e}")

                if submitted_savunmayapilmadi:
                    itiraz_tar = tarih_birlestir_ve_formatla(itiraz_tar_ham)
                    if not itiraz_tar.strip():
                        st.warning("⚠️ Lütfen İtiraz Tebliğ Tarihini giriniz.")
                    else:
                        try:
                            savunma_son_str = hesapla_savunma_son_gun(itiraz_tar)
                            idx = df.index[(df['Durum'].astype(str).str.strip() == secilen_asama) & (df['Marka Adı'].astype(str) == secilen_marka)][0]
                            df.at[idx, 'Durum'] = "Savunma Yapılmadı"
                            df.at[idx, 'Operasyon Yetkilisi'] = otomatik_op
                            df.at[idx, 'İtiraz Tarihi'] = itiraz_tar
                            df.at[idx, 'Savunma Son Günü'] = savunma_son_str
                            df.at[idx, 'Savunma Durumu'] = "Savunma Yapılmadı"
                            df.at[idx, 'Savunma Ücreti KDV Dahil'] = savunma_ucret_input.strip()
                            df.at[idx, 'Evrak Numarası'] = evrak_no_input.strip()
                            df.at[idx, 'Savunma Ücreti Alındı'] = "Evet" if savunma_ucreti_alindi_check else "Hayır"
                            
                            veriyi_kaydet_ve_yedekle(df)
                            st.success("✅ Başarılı! Savunma Yapılmadı aşamasına aktarıldı.")
                            import time; time.sleep(1.2)
                            st.session_state.aktif_sayfa = "Savunma Yapılmadı"
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Hata oluştu: {e}")
    elif secilen_asama == "Savunma Yapıldı":
        st.subheader("✏️ Savunma Yapıldı Bilgilerini Güncelle")
        marka_listesi = asama_df['Marka Adı'].astype(str).tolist() if not asama_df.empty else []
        secilen_marka = st.selectbox("İşlem Yapılacak Markayı Seçin", options=marka_listesi) if marka_listesi else None
        if secilen_marka:
            s_row = df[(df['Durum'].astype(str).str.strip() == secilen_asama) & (df['Marka Adı'].astype(str) == secilen_marka)].iloc[0]
            
            mevcut_itiraz_tar = str(s_row.get('İtiraz Tarihi', '')) if pd.notna(s_row.get('İtiraz Tarihi')) and str(s_row.get('İtiraz Tarihi')).lower() != 'nan' else ""
            mevcut_savunma_son = str(s_row.get('Savunma Son Günü', '')) if pd.notna(s_row.get('Savunma Son Günü')) and str(s_row.get('Savunma Son Günü')).lower() != 'nan' else ""
            mevcut_savunma_yapildi_tar = str(s_row.get('Savunma Yapıldı Tarihi', '')) if pd.notna(s_row.get('Savunma Yapıldı Tarihi')) and str(s_row.get('Savunma Yapıldı Tarihi')).lower() != 'nan' else datetime.now().strftime("%d/%m/%Y")
            
            with st.form(f"form_guncelle_savunma_yapildi_{secilen_marka}"):
                c1, c2, c3 = st.columns(3)
                c1.text_input("Danışman", value=str(s_row.get('Danışman', '')), disabled=True)
                c2.text_input("Başvuru No", value=str(s_row.get('Başvuru No', '')) if pd.notna(s_row.get('Başvuru No')) else "", disabled=True)
                c3.text_input("İtiraz Tebliğ Tarihi", value=mevcut_itiraz_tar, disabled=True)
                
                c1.text_input("Savunma Son Günü", value=mevcut_savunma_son, disabled=True)
                savunma_yapildi_tar_ham = c2.text_input("Savunma Yapıldı Tarihi (GG/AA/YYYY)", value=mevcut_savunma_yapildi_tar)
                
                if st.form_submit_button("💾 Kaydı Güncelle"):
                    yeni_savunma_yapildi_tar = tarih_birlestir_ve_formatla(savunma_yapildi_tar_ham)
                    idx = df.index[(df['Durum'].astype(str).str.strip() == secilen_asama) & (df['Marka Adı'].astype(str) == secilen_marka)][0]
                    df.at[idx, 'Savunma Yapıldı Tarihi'] = yeni_savunma_yapildi_tar
                    
                    veriyi_kaydet_ve_yedekle(df)
                    st.success("✅ Başarılı! Kayıt güncellendi.")
                    import time; time.sleep(1.2)
                    st.rerun()
    elif secilen_asama == "Tescil Tebliğ Beklemede":
        st.subheader("✏️ Tescil Tebliğ Tarihini Girin")
        marka_listesi = asama_df['Marka Adı'].astype(str).tolist() if not asama_df.empty else []
        secilen_marka = st.selectbox("İşlem Yapılacak Markayı Seçin", options=marka_listesi) if marka_listesi else None
        if secilen_marka:
            s_row = df[(df['Durum'].astype(str).str.strip() == secilen_asama) & (df['Marka Adı'].astype(str) == secilen_marka)].iloc[0]
            with st.form(f"form_guncelle_tescil_teblig_{secilen_marka}"):
                c1, c2 = st.columns(2)
                c2.text_input("Danışman", value=str(s_row.get('Danışman', '')), disabled=True)
                c1.text_input("Başvuru No", value=str(s_row.get('Başvuru No', '')) if pd.notna(s_row.get('Başvuru No')) else "", disabled=True)
                c2.text_input("Başvuru Tarihi", value=str(s_row.get('Başvuru Tarihi', '')) if pd.notna(s_row.get('Başvuru Tarihi')) else "", disabled=True)
                
                tescil_tar_ham = c1.text_input("Tescil Tebliğ Tarihi (GG/AA/YYYY)*", value=str(s_row.get('Tescil Tebliğ Tarihi', '')) if pd.notna(s_row.get('Tescil Tebliğ Tarihi')) else "")
                
                if st.form_submit_button("💾 Kaydet and Müşteri Arandı Aşamasına Geç"):
                    tescil_tar = tarih_birlestir_ve_formatla(tescil_tar_ham)
                    if not tescil_tar.strip():
                        st.warning("⚠️ Lütfen Tescil Tebliğ Tarihini giriniz.")
                    else:
                        try:
                            son_odeme_str = hesapla_tescil_son_odeme(tescil_tar)

                            idx = df.index[(df['Durum'].astype(str).str.strip() == secilen_asama) & (df['Marka Adı'].astype(str) == secilen_marka)][0]
                            df.at[idx, 'Tescil Tebliğ Tarihi'] = tescil_tar
                            df.at[idx, 'Tescil Son Ödeme Tarihi'] = son_odeme_str
                            df.at[idx, 'Durum'] = "Tescil Tebliğ Edildi Müşteri Arandı"
                            
                            veriyi_kaydet_ve_yedekle(df)
                            
                            st.success("✅ Başarılı! Tescil Tebliğ Edildi Müşteri Arandı aşamasına aktarıldı.")
                            import time; time.sleep(1.2)
                            st.session_state.aktif_sayfa = "Tescil Tebliğ Edildi Müşteri Arandı"
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Tarih hesaplanırken hata oluştu: {e}")
    elif secilen_asama == "Ödeme Sözü Verenler":
        st.subheader("✏️ Ödeme Sözü Tarihini Güncelle veya Ödeme Alındı İşlemi Yap")
        marka_listesi = asama_df['Marka Adı'].astype(str).tolist() if not asama_df.empty else []
        secilen_marka = st.selectbox("İşlem Yapılacak Markayı Seçin", options=marka_listesi) if marka_listesi else None
        if secilen_marka:
            s_row = df[(df['Durum'].astype(str).str.strip() == secilen_asama) & (df['Marka Adı'].astype(str) == secilen_marka)].iloc[0]
            
            mevcut_tescil_teblig = str(s_row.get('Tescil Tebliğ Tarihi', '')).strip()
            hesaplanan_son_odeme = hesapla_tescil_son_odeme(mevcut_tescil_teblig)
            
            with st.form(f"form_guncelle_odeme_sozu_{secilen_marka}"):
                c1, c2, c3 = st.columns(3)
                c1.text_input("Danışman", value=str(s_row.get('Danışman', '')), disabled=True)
                c2.text_input("Başvuru No", value=str(s_row.get('Başvuru No', '')) if pd.notna(s_row.get('Başvuru No')) else "", disabled=True)
                c3.text_input("Başvuru Tarihi", value=str(s_row.get('Başvuru Tarihi', '')) if pd.notna(s_row.get('Başvuru Tarihi')) else "", disabled=True)
                
                c1.text_input("Tescil Tebliğ Tarihi", value=mevcut_tescil_teblig, disabled=True)
                c2.text_input("Tescil Ödeme Son Günü", value=hesaplanan_son_odeme, disabled=True)
                
                mevcut_odeme_sozu = str(s_row.get('Ödeme Sözü Tarihi', '')) if pd.notna(s_row.get('Ödeme Sözü Tarihi')) else ""
                odeme_sozu_ham = c3.text_input("Ödeme Sözü Tarihi (GG/AA/YYYY)", value=mevcut_odeme_sozu)
                
                mevcut_fatura_no = str(s_row.get('Fatura No', '')) if pd.notna(s_row.get('Fatura No')) else ""
                fatura_no_input = c1.text_input("Fatura No*", value=mevcut_fatura_no)
                
                mevcut_fatura_tarihi = str(s_row.get('Fatura Tarihi', '')) if pd.notna(s_row.get('Fatura Tarihi')) else ""
                fatura_tarihi_ham = c2.text_input("Fatura Tarihi (GG/AA/YYYY)", value=mevcut_fatura_tarihi)
                
                mevcut_sayac = str(s_row.get('Ödeme Sözü Güncelleme Sayısı', '0'))
                c3.markdown(f"<div style='margin-top: 24px; color: #FFFFFF !important;'>ℹ️ Güncelleme: <b style='color: #FFFFFF !important;'>{mevcut_sayac}</b> kez</div>", unsafe_allow_html=True)

                btn_col1, btn_col2 = st.columns(2)
                submitted_update = btn_col1.form_submit_button("💾 Ödeme Tarihi Güncelle")
                submitted_odemepap = btn_col2.form_submit_button("💳 Ödeme Yap (Tescil Kurum Ödemesi Bekleyen Yap)")
                
                if submitted_update:
                    yeni_sozu_tarihi = tarih_birlestir_ve_formatla(odeme_sozu_ham)
                    yeni_fatura_tarihi = tarih_birlestir_ve_formatla(fatura_tarihi_ham)
                    idx = df.index[(df['Durum'].astype(str).str.strip() == secilen_asama) & (df['Marka Adı'].astype(str) == secilen_marka)][0]
                    
                    try:
                        eski_sayac = int(str(df.at[idx, 'Ödeme Sözü Güncelleme Sayısı']).strip() or "0")
                    except:
                        eski_sayac = 0
                    
                    df.at[idx, 'Ödeme Sözü Güncelleme Sayısı'] = str(eski_sayac + 1)
                    df.at[idx, 'Ödeme Sözü Tarihi'] = yeni_sozu_tarihi.strip()
                    df.at[idx, 'Fatura No'] = fatura_no_input.strip()
                    df.at[idx, 'Fatura Tarihi'] = yeni_fatura_tarihi.strip()
                    if hesaplanan_son_odeme:
                        df.at[idx, 'Tescil Son Ödeme Tarihi'] = hesaplanan_son_odeme
                    
                    veriyi_kaydet_ve_yedekle(df)
                    st.success(f"Güncellendi! Toplam güncelleme sayısı: {eski_sayac + 1}")
                    import time; time.sleep(1.0)
                    st.rerun()

                if submitted_odemepap:
                    if not fatura_no_input.strip():
                        st.warning("⚠️ Lütfen Fatura No alanını doldurunuz.")
                    else:
                        yeni_fatura_tarihi = tarih_birlestir_ve_formatla(fatura_tarihi_ham)
                        idx = df.index[(df['Durum'].astype(str).str.strip() == secilen_asama) & (df['Marka Adı'].astype(str) == secilen_marka)][0]
                        df.at[idx, 'Durum'] = "Tescil Kurum Ödemesi Bekleyen"
                        df.at[idx, 'Fatura No'] = fatura_no_input.strip()
                        df.at[idx, 'Fatura Tarihi'] = yeni_fatura_tarihi.strip()
                        if hesaplanan_son_odeme:
                            df.at[idx, 'Tescil Son Ödeme Tarihi'] = hesaplanan_son_odeme
                        
                        veriyi_kaydet_ve_yedekle(df)
                        st.success("✅ Başarılı! Tescil Kurum Ödemesi Bekleyen aşamasına aktarıldı.")
                        import time; time.sleep(1.2)
                        st.session_state.aktif_sayfa = "Tescil Kurum Ödemesi Bekleyen"
                        st.rerun()
    else:
        st.subheader("✏️ Marka Bilgilerini and Durumunu Güncelle")
        marka_listesi = asama_df['Marka Adı'].astype(str).tolist() if not asama_df.empty else []
        secilen_marka = st.selectbox("İşlem Yapılacak Markayı Seçin", options=marka_listesi) if marka_listesi else None
        if secilen_marka:
            s_row = df[(df['Durum'].astype(str).str.strip() == secilen_asama) & (df['Marka Adı'].astype(str) == secilen_marka)].iloc[0]
            
            mevcut_tescil_teblig = str(s_row.get('Tescil Tebliğ Tarihi', '')).strip()
            hesaplanan_son_odeme = hesapla_tescil_son_odeme(mevcut_tescil_teblig)
            
            with st.form(f"form_guncelle_{secilen_marka}"):
                c1, c2 = st.columns(2)
                c1.text_input("Danışman", value=str(s_row.get('Danışman', '')), disabled=True)
                c2.text_input("Başvuru No", value=str(s_row.get('Başvuru No', '')) if pd.notna(s_row.get('Başvuru No')) else "", disabled=True)
                
                b_tarih_ham = c1.text_input("Başvuru Tarihi", value=str(s_row.get('Başvuru Tarihi', '')) if pd.notna(s_row.get('Başvuru Tarihi')) else "", disabled=True)
                tescil_tar_ham = c2.text_input("Tescil Tebliğ Tarihi", value=mevcut_tescil_teblig, disabled=True)
                
                c1.text_input("Tescil Ödeme Son Günü", value=hesaplanan_son_odeme, disabled=True)
                
                if st.form_submit_button("💾 Kaydı Güncelle"):
                    idx = df.index[(df['Durum'].astype(str).str.strip() == secilen_asama) & (df['Marka Adı'].astype(str) == secilen_marka)][0]
                    if hesaplanan_son_odeme:
                        df.at[idx, 'Tescil Son Ödeme Tarihi'] = hesaplanan_son_odeme
                    
                    veriyi_kaydet_ve_yedekle(df)
                    
                    st.session_state["success_msg"] = f"Başarılı! Kayıt güncellendi and yedeklendi."
                    st.rerun()
                    
            if "success_msg" in st.session_state:
                st.success(st.session_state["success_msg"])
                del st.session_state["success_msg"]

elif is_admin and st.session_state.aktif_sayfa == "Personel Yönetimi":
    if st.button("⬅️ Geri Çık"): sayfa_degistir("Ana Sayfa")
    st.markdown("<h2>👥 Personel Yönetimi</h2>", unsafe_allow_html=True)
    
    u_df_display = load_users()
    if not u_df_display.empty:
        st.dataframe(u_df_display, use_container_width=True)
    
    t1, t2, t3 = st.tabs(["➕ Danışman Ekle", "🔑 Şifre Değiştir", "❌ Danışman Sil"])
    with t1:
        with st.form("personel_ekle_form", clear_on_submit=True):
            n, s = st.text_input("Danışman Adı"), st.text_input("Şifre", type="password")
            if st.form_submit_button("Danışman Ekle") and n.strip():
                u_df = load_users()
                if n.strip().upper() in u_df["İsim"].values:
                    st.error("Personel zaten var!")
                else:
                    yeni_satir = pd.DataFrame({"İsim": [n.strip().upper()], "Şifre": [s.strip()]})
                    u_df = pd.concat([u_df, yeni_satir], ignore_index=True)
                    save_users(u_df)
                    st.success("Eklendi!")
                    import time; time.sleep(1.2)
                    st.rerun()
    with t2:
        u_df = load_users()
        if not u_df.empty:
            p = st.selectbox("Personel", u_df["İsim"].tolist(), key="sifre_degis_pers")
            s2 = st.text_input("Yeni Şifre", type="password", key="sifre_degis_val")
            if st.button("Şifreyi Güncelle"):
                u_df.loc[u_df["İsim"] == p, "Şifre"] = s2.strip()
                save_users(u_df)
                st.success("Güncellendi!")
                import time; time.sleep(1.2)
                st.rerun()
    with t3:
        u_df = load_users()
        if not u_df.empty:
            s3 = st.selectbox("Silinecek", u_df["İsim"].tolist(), key="sil_pers")
            if st.button("Sil"):
                u_df = u_df[u_df["İsim"] != s3]
                save_users(u_df)
                st.success("Silindi!")
                import time; time.sleep(1.2)
                st.rerun()
