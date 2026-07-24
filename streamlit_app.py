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

ILLER = ["Adana", "Adıyaman", "Afyonkarahisar", "Ağrı", "Aksaray", "Amasya", "Ankara", "Antalya", "Ardahan", "Artvin", "Aydın", "Balıkesir", "Bartın", "Batman", "Bayburt", "Bilecik", "Bingöl", "Bitlis", "Bolu", "Burdur", "Bursa", "Çanakkale", "Çankırı", "Çorum", "Denizli", "Diyarbakır", "Düzce", "Edirne", "Elazığ", "Erzincan", "Erzurum", "Eskişehir", "Gaziantep", "Giresun", "Gümüşhane", "Hakkari", "Hatay", "Iğdır", "Isparta", "İstanbul", "İzmir", "Kahramanmaraş", "Karabük", "Karaman", "Kars", "Kastamonu", "Kayseri", "Kırıkkale", "Kırklareli", "Kırşehir", "Kilis", "Kocaeli", "Konya", "Kütahya", "Malatya", "Manisa", "Mardin", "Mersin", "Muğla", "Muş", "Nevşehir", "Niğde", "Ordu", "Osmaniye", "Rize", "Sakarya", "Samsun", "Siirt", "Sinop", "Sivas", "Şanlıurfa", "Şırnak", "Tekirdağ", "Tokat", "Trabzon", "Tunceli", "Uşak", "Van", "Yalova", "Yozgat", "Zonguldak"]
SINIFLAR = [str(i) for i in range(1, 46)] + [f"35/{i}" for i in range(1, 35)]

if not os.path.exists(USER_FILE):
    pd.DataFrame({
        "İsim": ["ALİ OSMAN YELBEY", "DENİZ TELLİ GÜRLEYENDAĞ", "MERVE YURTLU", "SELEN AKCAN"],
        "Şifre": ["MARKA123", "MARKA123", "MARKA123", "MARKA123"]
    }).to_csv(USER_FILE, index=False)

def ay_ekle(kaynak_tarih, ay_sayisi=2):
    """Verilen tarihe tam ay ekler (Örn: 10.02.2026 -> 10.04.2026)"""
    yil = kaynak_tarih.year + (kaynak_tarih.month + ay_sayisi - 1) // 12
    ay = (kaynak_tarih.month + ay_sayisi - 1) % 12 + 1
    gun = kaynak_tarih.day
    while True:
        try:
            return datetime(yil, ay, gun)
        except ValueError:
            gun -= 1

def resmi_tatil_ve_tatil_kontrol(dt):
    """Hafta sonu veya resmi tatil kontrolü yapar, iş günü değilse kaydırır."""
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

# --- GİRİŞ KONTROLÜ ---
if "kullanici" not in st.session_state: 
    st.session_state.kullanici = None

if not st.session_state.kullanici:
    st.markdown("<h1 style='text-align: center; color: #FFFFFF;'>Markanow Patent Satış Takip ERP</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #FFFFFF;'>Lütfen sisteme giriş yapınız.</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        user_df = pd.read_csv(USER_FILE)
        secili_kullanici = st.selectbox("Kullanıcı Seçiniz", user_df["İsim"].tolist())
        sifre_input = st.text_input("Şifre", type="password")
        
        st.write("")
        if st.button("Giriş Yap", use_container_width=True):
            dogru_sifre = str(user_df[user_df["İsim"] == secili_kullanici].iloc[0]["Şifre"]).strip()
            if str(sifre_input).strip() == dogru_sifre:
                st.session_state.kullanici = secili_kullanici
                st.success("Giriş başarılı! Yönlendiriliyorsunuz...")
                st.rerun()
            else:
                st.error("❌ Hatalı Şifre!")
    st.stop()

# --- ROL TANIMLAMALARI ---
aktif_kullanici_ad = str(st.session_state.kullanici).strip().upper()
is_admin = (aktif_kullanici_ad == "ALİ OSMAN YELBEY")
is_muhasebe = is_admin or (aktif_kullanici_ad in ["DENİZ TELLİ GÜRLEYENDAĞ", "SELEN AKCAN"])

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
    st.session_state.aktif_sayfa = "Ana Sayfa"
    st.rerun()

st.sidebar.write("---")

# Menü Yönlendirmeleri
if not is_muhasebe:
    if st.sidebar.button("📝 Yeni Satış Giriş", use_container_width=True):
        sayfa_degistir("Yeni Satış Giriş")
    if st.sidebar.button("📅 Satışlarım (Bu Ay)", use_container_width=True):
        sayfa_degistir("Satışlarım")
    if st.sidebar.button("📊 Genel Satışlarım", use_container_width=True):
        sayfa_degistir("Genel Satışlarım")

if is_muhasebe:
    with st.sidebar.expander("📄 Marka Tescil Aşamaları", expanded=True):
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

elif not is_muhasebe and st.session_state.aktif_sayfa == "Yeni Satış Giriş":
    if st.button("⬅️ Geri Çık"):
        sayfa_degistir("Ana Sayfa")
        
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
        tutar = c2.text_input("Tutar (TL)", value="")
        
        submitted = st.form_submit_button("Satışı Kaydet")
        if submitted:
            dogru_tarihi = tarih_birlestir_ve_formatla(dogru_tarihi_ham)
            s_tarihi = tarih_birlestir_ve_formatla(s_tarihi_ham)

            eksik_alanlar = []
            if not m_adi.strip(): eksik_alanlar.append("Marka Adı")
            if not ad_soyad.strip(): eksik_alanlar.append("İsim Soyisim")
            if not tc.strip(): eksik_alanlar.append("TC")
            if not tel.strip(): eksik_alanlar.append("Telefon")
            if not email.strip(): eksik_alanlar.append("E-Mail")
            if not dogru_tarihi.strip(): eksik_alanlar.append("Doğum Tarihi")
            if not sinif: eksik_alanlar.append("Sınıf Seçimi")
            if not s_tarihi.strip(): eksik_alanlar.append("Satış Tarihi")
            if not tutar.strip(): eksik_alanlar.append("Tutar")
            
            if eksik_alanlar:
                st.error(f"❌ Lütfen boş bırakılan zorunlu alanları doldurunuz: {', '.join(eksik_alanlar)}")
            else:
                new_row = {
                    "Marka Adı": m_adi.strip(), "Ad Soyad": ad_soyad.strip(), "TC": tc.strip(), "Telefon": tel.strip(), "E-Mail": email.strip(),
                    "Doğum Tarihi": dogru_tarihi.strip(), "İl": il, "Sınıf": ",".join(sinif), "Ödeme": odeme, 
                    "Satış Tarihi": s_tarihi.strip(), "Tutar": tutar.strip(), "Durum": "Muhasebe Onayı Bekliyor", 
                    "Danışman": aktif_kullanici_ad, "Fatura No": "", "Fatura Tarihi": "", "Başvuru No": "", "Başvuru Tarihi": "", "Yayın Tarihi": "", "Yayın Bitiş Tarihi": "", "Sonraki Aşama Seçimi": "", "İtiraz Tarihi": "", "Tescil Tebliğ Tarihi": "", "Tescil Son Ödeme Tarihi": "", "Ödeme Tarihi": "", "Tescil Harç Tutarı": ""
                }
                guncel_df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                guncel_df.to_csv(DATA_FILE, index=False)
                st.success("✅ Satış başarıyla kaydedildi ve onay için muhasebeye gönderildi. Ana sayfaya yönlendiriliyorsunuz...")
                st.session_state.aktif_sayfa = "Ana Sayfa"
                st.rerun()

elif not is_muhasebe and st.session_state.aktif_sayfa == "Satışlarım":
    if st.button("⬅️ Geri Çık"):
        sayfa_degistir("Ana Sayfa")
        
    mevcut_ay = datetime.now().strftime("%m")
    mevcut_yil = str(datetime.now().year)
    st.markdown(f"<h2>📅 Satışlarım (Bu Ay: {mevcut_ay}/{mevcut_yil})</h2>", unsafe_allow_html=True)
    
    df['Danisman_Temp'] = df['Danışman'].astype(str).str.strip().str.upper()
    danisman_df = df[df['Danisman_Temp'] == aktif_kullanici_ad].copy()
    
    def bu_ay_faturalanan(row):
        try:
            f_tarih = row.get('Fatura Tarihi', '')
            if pd.isna(f_tarih) or str(f_tarih).strip() == '' or str(f_tarih).lower() == 'none': return False
            dt = pd.to_datetime(f_tarih, format='%d/%m/%Y', errors='coerce')
            if pd.isna(dt): dt = pd.to_datetime(f_tarih, errors='coerce')
            if pd.isna(dt): return False
            return f"{dt.month:02d}" == mevcut_ay and str(dt.year) == mevcut_yil
        except: return False
            
    if not danisman_df.empty:
        danisman_df = danisman_df[danisman_df.apply(bu_ay_faturalanan, axis=1)]
    danisman_df = danisman_df.drop(columns=['Danisman_Temp'], errors='ignore')
    
    toplam_ciro = pd.to_numeric(danisman_df['Tutar'], errors='coerce').fillna(0).sum()
    c1, c2 = st.columns(2)
    c1.metric("Bu Ay Satış Adedi", len(danisman_df))
    c2.metric("Bu Ay Toplam Ciro (TL)", f"{toplam_ciro:,.2f} TL")
    st.dataframe(danisman_df, use_container_width=True)

elif not is_muhasebe and st.session_state.aktif_sayfa == "Genel Satışlarım":
    if st.button("⬅️ Geri Çık"):
        sayfa_degistir("Ana Sayfa")
        
    st.markdown(f"<h2>📊 Genel Satışlarım (Filtreleme)</h2>", unsafe_allow_html=True)
    aylar = {"Tümü": None, "Ocak": "01", "Şubat": "02", "Mart": "03", "Nisan": "04", "Mayıs": "05", "Haziran": "06", "Temmuz": "07", "Ağustos": "08", "Eylül": "09", "Ekim": "10", "Kasım": "11", "Aralık": "12"}
    col_f1, col_f2 = st.columns(2)
    secilen_ay_isim = col_f1.selectbox("Ay Seçin", list(aylar.keys()))
    secilen_yil = col_f2.text_input("Yıl (Örn: 2026)", value=str(datetime.now().year))
    secilen_ay_kod = aylar[secilen_ay_isim]
    
    df['Danisman_Temp'] = df['Danışman'].astype(str).str.strip().str.upper()
    danisman_df = df[df['Danisman_Temp'] == aktif_kullanici_ad].copy()
    
    def genel_filtrele(row):
        try:
            f_tarih = row.get('Fatura Tarihi', '')
            if pd.isna(f_tarih) or str(f_tarih).strip() == '' or str(f_tarih).lower() == 'none': return False
            dt = pd.to_datetime(f_tarih, format='%d/%m/%Y', errors='coerce')
            if pd.isna(dt): dt = pd.to_datetime(f_tarih, errors='coerce')
            if pd.isna(dt): return False
            ay_eslesir = True if secilen_ay_kod is None else (f"{dt.month:02d}" == secilen_ay_kod)
            yil_eslesir = True if not secilen_yil.strip() else (str(dt.year) == secilen_yil.strip())
            return ay_eslesir and yil_eslesir
        except: return False
            
    if not danisman_df.empty:
        danisman_df = danisman_df[danisman_df.apply(genel_filtrele, axis=1)]
    danisman_df = danisman_df.drop(columns=['Danisman_Temp'], errors='ignore')
    
    toplam_ciro = pd.to_numeric(danisman_df['Tutar'], errors='coerce').fillna(0).sum()
    c1, c2 = st.columns(2)
    c1.metric("Filtrelenen Satış Adedi", len(danisman_df))
    c2.metric("Filtrelenen Ciro (TL)", f"{toplam_ciro:,.2f} TL")
    st.dataframe(danisman_df, use_container_width=True)

# --- DANIŞMAN SATIŞLARINI DÜZENLE (YÖNETİCİLER İÇİN) ---
elif is_muhasebe and st.session_state.aktif_sayfa == "Danışman Satışlarını Düzenle":
    if st.button("⬅️ Geri Çık"):
        sayfa_degistir("Ana Sayfa")
        
    st.markdown("<h2>🛠️ Danışman Satışlarını Düzenleme Paneli</h2>", unsafe_allow_html=True)
    
    if df.empty:
        st.info("Sistemde kayıtlı hiç satış bulunmuyor.")
    else:
        arama_input = st.text_input("🔍 Marka Adı ile Ara", placeholder="Marka adı yazın...")
        
        filtrelenmis_df = df.copy()
        if arama_input.strip():
            filtrelenmis_df = filtrelenmis_df[filtrelenmis_df['Marka Adı'].astype(str).str.contains(arama_input.strip(), case=False, na=False)]
            
        marka_listesi_tum = filtrelenmis_df['Marka Adı'].astype(str).tolist()
        
        if not marka_listesi_tum:
            st.warning("Aramanızla eşleşen marka bulunamadı.")
        else:
            secilen_duzenle_marka = st.selectbox("Düzenlenecek Markayı Seçin", options=marka_listesi_tum, key="admin_duzenle_marka")
            
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
                        
                        df.to_csv(DATA_FILE, index=False)
                        st.success(f"✅ '{secilen_duzenle_marka}' markasına ait danışman satış bilgileri başarıyla güncellendi!")
                        st.rerun()

                    if submitted_delete:
                        df_yeni = df[df['Marka Adı'].astype(str) != secilen_duzenle_marka]
                        df_yeni.to_csv(DATA_FILE, index=False)
                        st.success(f"🗑️ '{secilen_duzenle_marka}' markasına ait kayıt başarıyla silindi!")
                        st.rerun()

# --- TESCİL TEBLİĞ EDİLİ MÜŞTERİ ARANDI EKRANI ---
elif is_muhasebe and st.session_state.aktif_sayfa == "Tescil Tebliğ Edildi Müşteri Arandı":
    if st.button("⬅️ Geri Çık"):
        sayfa_degistir("Ana Sayfa")
        
    st.markdown("<h2>💳 Tescil Tebliğ Edildi Müşteri Arandı Ekranı</h2>", unsafe_allow_html=True)
    
    tescil_df = df[(df['Durum'].astype(str).str.strip().isin(["Tescil Tebliğ Beklemede", "Tescil Kurum Ödemesi Bekleyen"])) & 
                   (df['Tescil Tebliğ Tarihi'].astype(str).str.strip() != "") & 
                   (df['Tescil Tebliğ Tarihi'].astype(str).str.lower() != "nan")]
    
    if tescil_df.empty:
        st.info("Tescil Tebliğ Tarihi girilmiş ve işlem bekleyen marka bulunmuyor.")
    else:
        arama_tescil = st.text_input("🔍 Marka Ara", placeholder="Marka adı yazın...", key="arama_tescil_odeme_input")
        if arama_tescil.strip():
            tescil_df = tescil_df[tescil_df['Marka Adı'].astype(str).str.contains(arama_tescil.strip(), case=False, na=False)]
            
        if tescil_df.empty:
            st.warning("Aramanızla eşleşen marka bulunamadı.")
        else:
            marka_listesi_tescil = tescil_df['Marka Adı'].astype(str).tolist()
            secilen_tescil_marka = st.selectbox("İşlem Yapılacak Markayı Seçin", options=marka_listesi_tescil, key="sel_tescil_odeme_marka")
            
            if secilen_tescil_marka:
                t_row = tescil_df[tescil_df['Marka Adı'].astype(str) == secilen_tescil_marka].iloc[0]
                
                tescil_tarihi_str = t_row.get('Tescil Tebliğ Tarihi', '')
                son_odeme_tarihi_str = t_row.get('Tescil Son Ödeme Tarihi', '')
                
                if not son_odeme_tarihi_str or son_odeme_tarihi_str == 'nan':
                    try:
                        parsed_t_tar = datetime.strptime(tescil_tarihi_str.strip(), "%d/%m/%Y")
                        taslak_son = ay_ekle(parsed_t_tar, 2)
                        hesaplanan_son = resmi_tatil_ve_tatil_kontrol(taslak_son)
                        son_odeme_tarihi_str = hesaplanan_son.strftime("%d/%m/%Y")
                        
                        idx_temp = df.index[df['Marka Adı'].astype(str) == str(secilen_tescil_marka)][0]
                        df.at[idx_temp, 'Tescil Son Ödeme Tarihi'] = son_odeme_tarihi_str
                        df.to_csv(DATA_FILE, index=False)
                    except:
                        son_odeme_tarihi_str = ""

                st.markdown(f"**Marka:** {t_row['Marka Adı']} | **Danışman:** *{t_row['Danışman']}*")
                
                c1, c2, c3, c4, c5 = st.columns([1.1, 1.1, 1.1, 1.1, 1])
                c1.markdown(f"**Tescil Tebliğ Tarihi**\n\n`{tescil_tarihi_str}`")
                c2.markdown(f"**TESCİL SON GÜNÜ**\n\n`{son_odeme_tarihi_str}`")
                tescil_fatura_no = c3.text_input("Tescil Fatura No", value="", key="ozel_tescil_f_no")
                tescil_tutar = c4.text_input("Tescil Harç / Hizmet Tutarı (TL)", value="2500", key="ozel_tescil_tutar")
                odeme_gunu_ham = c5.text_input("Ödeme Günü (GG/AA/YYYY)", value=str(t_row.get('Ödeme Tarihi', '')) if pd.notna(t_row.get('Ödeme Tarihi')) and str(t_row.get('Ödeme Tarihi')) != 'nan' else datetime.now().strftime("%d/%m/%Y"), key="ozel_odeme_gunu_input")
                
                st.write("")
                if st.button("⏳ Tescil Kurum Ödemesi Bekleyen Yap", key="ozel_tescil_onay_btn"):
                    odeme_gunu = tarih_birlestir_ve_formatla(odeme_gunu_ham)
                    if odeme_gunu.strip():
                        idx = df.index[df['Marka Adı'].astype(str) == str(secilen_tescil_marka)][0]
                        df.at[idx, 'Durum'] = "Tescil Kurum Ödemesi Bekleyen"
                        if tescil_fatura_no.strip():
                            df.at[idx, 'Fatura No'] = tescil_fatura_no.strip()
                        df.at[idx, 'Ödeme Tarihi'] = odeme_gunu.strip()
                        df.at[idx, 'Tescil Harç Tutarı'] = tescil_tutar.strip()
                        df.to_csv(DATA_FILE, index=False)
                        st.success(f"⏳ '{secilen_tescil_marka}' başarıyla 'Tescil Kurum Ödemesi Bekleyen' aşamasına taşındı!")
                        sayfa_degistir("Tescil Kurum Ödemesi Bekleyen")
                    else:
                        st.warning("Lütfen Ödeme Günü alanını doldurunuz.")

# --- MUHASEBE AŞAMA SAYFALARI (SOL MENÜDEN SEÇİLENLER) ---
elif is_muhasebe and st.session_state.aktif_sayfa in [
    "Muhasebe Onayı Bekliyor", "Başvuru Beklemede", "Kurum İncelemesinde", 
    "Yayında", "İtiraz Geldi - Savunma Bekliyor", "Tescil Tebliğ Beklemede", 
    "Tescil Tebliğ Edildi Müşteri Arandı", "Tescil Kurum Ödemesi Bekleyen", "Tescil Kuruma Ödendi", "Tescillendi", "Reddedildi"
]:
    secilen_asama = st.session_state.aktif_sayfa
    
    top_col1, top_col2 = st.columns([2, 1])
    with top_col1:
        st.markdown(f"<h2>📂 Aşama: {secilen_asama}</h2>", unsafe_allow_html=True)
    with top_col2:
        arama_metni = st.text_input("🔍 Marka Ara", placeholder="Marka adı yazın...", key=f"arama_{secilen_asama}")
    
    asama_df = df[df['Durum'].astype(str).str.strip() == secilen_asama]
    
    if secilen_asama == "Tescil Tebliğ Beklemede":
        asama_df = asama_df[(asama_df['Tescil Tebliğ Tarihi'].astype(str).str.strip() == "") | 
                            (asama_df['Tescil Tebliğ Tarihi'].astype(str).str.lower() == "nan")]

    if arama_metni.strip():
        asama_df = asama_df[asama_df['Marka Adı'].astype(str).str.contains(arama_metni.strip(), case=False, na=False)]
    
    if asama_df.empty:
        st.info(f"'{secilen_asama}' aşamasında aramanızla eşleşen kayıt bulunmuyor.")
    else:
        if secilen_asama == "Kurum İncelemesinde":
            gosterge_df = asama_df[['Marka Adı', 'Başvuru No', 'Başvuru Tarihi']].copy()
            st.dataframe(gosterge_df, use_container_width=True)
        else:
            st.dataframe(asama_df, use_container_width=True)
            
        st.write("---")
        
        if secilen_asama == "Muhasebe Onayı Bekliyor":
            st.subheader("✅ Onay Bekleyen Satışları Faturalandır ve Başvuru Beklemede'ye Al")
            for i, row in asama_df.iterrows():
                with st.container():
                    st.markdown(f"Marka: **{row['Marka Adı']}** | Satışı Giren Danışman: *{row['Danışman']}* | Tutar: **{row['Tutar']} TL**")
                    c1, c2, c3 = st.columns([1.5, 1.5, 1])
                    f_no = c1.text_input("Fatura No", key=f"f_no_{row['Marka Adı']}")
                    f_tarih_ham = c2.text_input("Fatura Tarihi (GG/AA/YYYY)", value=datetime.now().strftime("%d/%m/%Y"), key=f"f_tar_{row['Marka Adı']}")
                    
                    with c3:
                        st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
                        if st.button("✅ Onayla ve Başvuru Beklemede Yap", key=f"onay_btn_{row['Marka Adı']}"):
                            f_tarih = tarih_birlestir_ve_formatla(f_tarih_ham)
                            if f_no.strip() and f_tarih.strip():
                                idx = df.index[df['Marka Adı'].astype(str) == str(row['Marka Adı'])][0]
                                df.at[idx, 'Durum'] = "Başvuru Beklemede"
                                df.at[idx, 'Fatura No'] = f_no.strip()
                                df.at[idx, 'Fatura Tarihi'] = f_tarih.strip()
                                df.to_csv(DATA_FILE, index=False)
                                st.success(f"✅ '{row['Marka Adı']}' onaylandı ve 'Başvuru Beklemede' aşamasına taşındı!")
                                st.rerun()
                            else:
                                st.warning("Lütfen Fatura No ve Fatura Tarihi alanlarını doldurun.")
                    st.write("---")
        else:
            st.subheader("✏️ Marka Bilgilerini ve Durumunu Güncelle")
            
            marka_listesi = asama_df['Marka Adı'].astype(str).tolist()
            secilen_marka = st.selectbox("İşlem Yapılacak Markayı Seçin", options=marka_listesi, key=f"sel_marka_{secilen_asama}")
            
            if secilen_marka:
                s_row = df[(df['Durum'].astype(str).str.strip() == secilen_asama) & (df['Marka Adı'].astype(str) == secilen_marka)].iloc[0]
                orijinal_danisman = str(s_row.get('Danışman', '')).strip().upper()
                st.markdown(f"**Seçilen Marka:** {s_row['Marka Adı']} | **Satışı Giren Danışman:** {orijinal_danisman}")
                
                with st.form(f"form_guncelle_{secilen_marka}"):
                    c1, c2 = st.columns(2)
                    
                    tum_durumlar = [
                        "Muhasebe Onayı Bekliyor",
                        "Başvuru Beklemede",
                        "Kurum İncelemesinde",
                        "Yayında",
                        "İtiraz Geldi - Savunma Bekliyor",
                        "Tescil Tebliğ Beklemede",
                        "Tescil Tebliğ Edildi Müşteri Arandı",
                        "Tescil Kurum Ödemesi Bekleyen",
                        "Tescil Kuruma Ödendi",
                        "Tescillendi 🎉",
                        "Reddedildi ❌"
                    ]
                    
                    if secilen_asama == "Başvuru Beklemede":
                        c1.text_input("Yeni Durum / Aşama", value="Başvuru Beklemede", disabled=True)
                        yeni_durum = "Başvuru Beklemede"
                        c2.text_input("Danışman (Satışı Giren)", value=orijinal_danisman, disabled=True)
                    else:
                        mevcut_durum_index = tum_durumlar.index(secilen_asama) if secilen_asama in tum_durumlar else 0
                        yeni_durum = c1.selectbox("Yeni Durum / Aşama", options=tum_durumlar, index=mevcut_durum_index)
                        c2.text_input("Danışman (Satışı Giren)", value=orijinal_danisman, disabled=True)

                    mevcut_b_no = str(s_row.get('Başvuru No', '')) if pd.notna(s_row.get('Başvuru No')) else ""
                    mevcut_b_tar = str(s_row.get('Başvuru Tarihi', '')) if pd.notna(s_row.get('Başvuru Tarihi')) else ""

                    b_no_disabled = bool(mevcut_b_no.strip() and mevcut_b_no != 'nan')
                    b_tar_disabled = bool(mevcut_b_tar.strip() and mevcut_b_tar != 'nan')

                    b_no = c1.text_input("Başvuru No", value=mevcut_b_no if mevcut_b_no != 'nan' else "", disabled=b_no_disabled)
                    b_tarih_ham = c2.text_input("Başvuru Tarihi (GG/AA/YYYY)", value=mevcut_b_tar if mevcut_b_tar != 'nan' else datetime.now().strftime("%d/%m/%Y"), disabled=b_tar_disabled, key=f"form_b_tar_{secilen_marka}")
                    
                    mevcut_y_tar = str(s_row.get('Yayın Tarihi', '')) if pd.notna(s_row.get('Yayın Tarihi')) else ""
                    mevcut_yayin_bitis = str(s_row.get('Yayın Bitiş Tarihi', '')) if pd.notna(s_row.get('Yayın Bitiş Tarihi')) else ""

                    y_tar_disabled = bool(mevcut_y_tar.strip() and mevcut_y_tar != 'nan')

                    y_tar_ham = c1.text_input("Yayın Tarihi (GG/AA/YYYY)", value=mevcut_y_tar if mevcut_y_tar != 'nan' else "", disabled=y_tar_disabled, key=f"form_y_tar_{secilen_marka}")
                    
                    y_tar = tarih_birlestir_ve_formatla(y_tar_ham)

                    calculated_yayin_bitis = ""
                    if y_tar.strip() and y_tar.strip().lower() != 'nan':
                        try:
                            parsed_y_tar = datetime.strptime(y_tar.strip(), "%d/%m/%Y")
                            taslak_bitis = ay_ekle(parsed_y_tar, 2)
                            hesaplanan_bitis = resmi_tatil_ve_tatil_kontrol(taslak_bitis)
                            calculated_yayin_bitis = hesaplanan_bitis.strftime("%d/%m/%Y")
                        except:
                            pass

                    final_yayin_bitis_val = mevcut_yayin_bitis if (mevcut_yayin_bitis and mevcut_yayin_bitis != 'nan') else calculated_yayin_bitis

                    yayin_bitis = c2.text_input("Yayın Bitiş Tarihi (GG/AA/YYYY)", value=final_yayin_bitis_val, disabled=True, key=f"form_yayin_bitis_{secilen_marka}")

                    mevcut_sonraki_asama = str(s_row.get('Sonraki Aşama Seçimi', '')) if pd.notna(s_row.get('Sonraki Aşama Seçimi')) else ""
                    secenekler = ["", "İtiraz Tebliğ Beklemede", "Tescil Tebliğ Beklemede"]
                    secilen_asama_indeks = secenekler.index(mevcut_sonraki_asama) if mevcut_sonraki_asama in secenekler else 0

                    sonraki_asama = c1.selectbox("Sonraki Aşama Seçimi", options=secenekler, index=secilen_asama_indeks, key=f"form_sonraki_asama_{secilen_marka}")

                    mevcut_itiraz_tar = str(s_row.get('İtiraz Tarihi', '')) if pd.notna(s_row.get('İtiraz Tarihi')) else ""
                    mevcut_tescil_tar = str(s_row.get('Tescil Tebliğ Tarihi', '')) if pd.notna(s_row.get('Tescil Tebliğ Tarihi')) else ""

                    itiraz_tar_ham = ""
                    tescil_tar_ham = ""

                    if sonraki_asama == "İtiraz Tebliğ Beklemede":
                        itiraz_tar_ham = c2.text_input("İtiraz Tarihi (GG/AA/YYYY)", value=mevcut_itiraz_tar if mevcut_itiraz_tar != 'nan' else datetime.now().strftime("%d/%m/%Y"), key=f"form_itiraz_tar_{secilen_marka}")
                    elif sonraki_asama == "Tescil Tebliğ Beklemede":
                        tescil_tar_ham = c2.text_input("Tescil Tebliğ Tarihi (GG/AA/YYYY)", value=mevcut_tescil_tar if mevcut_tescil_tar != 'nan' else datetime.now().strftime("%d/%m/%Y"), key=f"form_tescil_tar_{secilen_marka}")

                    submitted_update = st.form_submit_button("💾 Kaydı Güncelle")
                    if submitted_update:
                        b_tarih = tarih_birlestir_ve_formatla(b_tarih_ham)
                        itiraz_tar = tarih_birlestir_ve_formatla(itiraz_tar_ham)
                        tescil_tar = tarih_birlestir_ve_formatla(tescil_tar_ham)

                        final_durum = yeni_durum
                        
                        if secilen_asama == "Kurum İncelemesinde":
                            if not y_tar.strip() or y_tar.strip().lower() == 'nan':
                                st.error("❌ Hata: Yayın Tarihi girmeden kaydı güncelleyemezsiniz!")
                                st.stop()
                            else:
                                final_durum = "Yayında"

                        if sonraki_asama == "İtiraz Tebliğ Beklemede":
                            final_durum = "İtiraz Geldi - Savunma Bekliyor"
                        elif sonraki_asama == "Tescil Tebliğ Beklemede":
                            final_durum = "Tescil Tebliğ Beklemede"

                        idx = df.index[(df['Durum'].astype(str).str.strip() == secilen_asama) & (df['Marka Adı'].astype(str) == secilen_marka)][0]
                        df.at[idx, 'Durum'] = final_durum
                        df.at[idx, 'Danışman'] = orijinal_danisman
                        
                        if not b_no_disabled and b_no.strip():
                            df.at[idx, 'Başvuru No'] = b_no.strip()
                        if not b_tar_disabled and b_tarih.strip():
                            df.at[idx, 'Başvuru Tarihi'] = b_tarih.strip()
                            
                        if not y_tar_disabled and y_tar.strip():
                            df.at[idx, 'Yayın Tarihi'] = y_tar.strip()
                            
                        if final_yayin_bitis_val:
                            df.at[idx, 'Yayın Bitiş Tarihi'] = final_yayin_bitis_val

                        df.at[idx, 'Sonraki Aşama Seçimi'] = sonraki_asama
                        if itiraz_tar.strip():
                            df.at[idx, 'İtiraz Tarihi'] = itiraz_tar.strip()
                        if tescil_tar.strip():
                            df.at[idx, 'Tescil Tebliğ Tarihi'] = tescil_tar.strip()
                            
                            try:
                                parsed_tescil_tar = datetime.strptime(tescil_tar.strip(), "%d/%m/%Y")
                                taslak_son_odeme = ay_ekle(parsed_tescil_tar, 2)
                                hesaplanan_son_odeme = resmi_tatil_ve_tatil_kontrol(taslak_son_odeme)
                                df.at[idx, 'Tescil Son Ödeme Tarihi'] = hesaplanan_son_odeme.strftime("%d/%m/%Y")
                            except:
                                pass
                            
                        df.to_csv(DATA_FILE, index=False)
                        
                        st.success(f"✅ Eksiksiz Güncellendi! '{secilen_marka}' markasının aşaması '{final_durum}' olarak güncellendi.")
                        st.rerun()

elif is_admin and st.session_state.aktif_sayfa == "Personel Yönetimi":
    if st.button("⬅️ Geri Çık"):
        sayfa_degistir("Ana Sayfa")
        
    st.markdown("<h2>👥 Personel ve Danışman Yönetimi</h2>", unsafe_allow_html=True)
    if os.path.exists(USER_FILE):
        st.dataframe(pd.read_csv(USER_FILE), use_container_width=True)
    
    t1, t2, t3 = st.tabs(["➕ Danışman Ekle", "🔑 Şifre Değiştir", "❌ Danışman Sil"])
    with t1:
        n, s = st.text_input("Personel / Danışman Adı", key="ekle"), st.text_input("Şifre", type="password", key="sifre")
        if st.button("Danışman Ekle"):
            if n.strip():
                u_df = pd.read_csv(USER_FILE) if os.path.exists(USER_FILE) else pd.DataFrame(columns=["İsim", "Şifre"])
                yeni_kisi = pd.DataFrame({"İsim": [n.strip().upper()], "Şifre": [s.strip()]})
                pd.concat([u_df, yeni_kisi], ignore_index=True).to_csv(USER_FILE, index=False)
                st.success(f"🎉 '{n.strip().upper()}' başarıyla eklendi!")
                st.rerun()
            else:
                st.warning("Lütfen bir isim girin.")
    with t2:
        if os.path.exists(USER_FILE):
            u_df = pd.read_csv(USER_FILE)
            p = st.selectbox("Personel Seç", u_df["İsim"].tolist(), key="sel")
            s2 = st.text_input("Yeni Şifre", type="password", key="new")
            if st.button("Şifreyi Güncelle"):
                u_df.loc[u_df["İsim"] == p, "Şifre"] = s2.strip()
                u_df.to_csv(USER_FILE, index=False)
                st.success("✅ Şifre güncellendi!")
                st.rerun()
    with t3:
        if os.path.exists(USER_FILE):
            u_df = pd.read_csv(USER_FILE)
            s3 = st.selectbox("Silinecek Personel", u_df["İsim"].tolist(), key="del")
            if st.button("Danışmanı Sil"):
                u_df = u_df[u_df["İsim"] != s3]
                u_df.to_csv(USER_FILE, index=False)
                st.success(f"❌ '{s3}' sistemden silindi!")
                st.rerun()
