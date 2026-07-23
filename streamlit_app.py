import streamlit as st
import pandas as pd
import os
import base64
from datetime import datetime, timedelta

# --- SAYFA YAPILANDIRMASI ---
st.set_page_config(page_title="Markanow ERP", layout="wide")

# --- GLOBAL & GİRİŞ CSS STİLLERİ ---
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

def load_data():
    zorunlu_kolonlar = [
        "Marka Adı", "Ad Soyad", "TC", "Telefon", "Doğum Tarihi", "İl", "Sınıf", "Ödeme", 
        "Satış Tarihi", "Tutar", "Durum", "Danışman", "Fatura No", "Fatura Tarihi", 
        "Başvuru No", "Başvuru Tarihi", "Kurum İnceleme Bitiş Tarihi", "Yayın Tarihi", "Tescil Tebliğ Tarihi"
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
        "Tescillendi 🎉", "Reddedildi ❌"
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
        if st.button("🎉 Tescillendi", use_container_width=True):
            sayfa_degistir("Tescillendi")
        if st.button("❌ Reddedildi", use_container_width=True):
            sayfa_degistir("Reddedildi")

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
        c1.text_input("Danışman", value=aktif_kullanici_ad, disabled=True)
        dogru_tarihi = c1.text_input("Doğum Tarihi (GG/AA/YYYY)", value="")
        
        il = c2.selectbox("İl", ILLER)
        sinif = c2.multiselect("Sınıf Seçimi", SINIFLAR)
        odeme = c2.selectbox("Ödeme Türü", ["EFT", "Kredi Kartı"])
        s_tarihi = c2.text_input("Satış Tarihi (GG/AA/YYYY)", value=datetime.now().strftime("%d/%m/%Y"))
        tutar = c2.text_input("Tutar (TL)", value="")
        
        submitted = st.form_submit_button("Satışı Kaydet")
        if submitted:
            eksik_alanlar = []
            if not m_adi.strip(): eksik_alanlar.append("Marka Adı")
            if not ad_soyad.strip(): eksik_alanlar.append("İsim Soyisim")
            if not tc.strip(): eksik_alanlar.append("TC")
            if not tel.strip(): eksik_alanlar.append("Telefon")
            if not dogru_tarihi.strip(): eksik_alanlar.append("Doğum Tarihi")
            if not sinif: eksik_alanlar.append("Sınıf Seçimi")
            if not s_tarihi.strip(): eksik_alanlar.append("Satış Tarihi")
            if not tutar.strip(): eksik_alanlar.append("Tutar")
            
            if eksik_alanlar:
                st.error(f"❌ Lütfen boş bırakılan zorunlu alanları doldurunuz: {', '.join(eksik_alanlar)}")
            else:
                new_row = {
                    "Marka Adı": m_adi.strip(), "Ad Soyad": ad_soyad.strip(), "TC": tc.strip(), "Telefon": tel.strip(), 
                    "Doğum Tarihi": dogru_tarihi.strip(), "İl": il, "Sınıf": ",".join(sinif), "Ödeme": odeme, 
                    "Satış Tarihi": s_tarihi.strip(), "Tutar": tutar.strip(), "Durum": "Muhasebe Onayı Bekliyor", 
                    "Danışman": aktif_kullanici_ad, "Fatura No": "", "Fatura Tarihi": "", "Başvuru No": "", "Başvuru Tarihi": "", "Kurum İnceleme Bitiş Tarihi": "", "Yayın Tarihi": "", "Tescil Tebliğ Tarihi": ""
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

# --- MUHASEBE AŞAMA SAYFALARI (SOL MENÜDEN SEÇİLENLER) ---
elif is_muhasebe and st.session_state.aktif_sayfa in [
    "Muhasebe Onayı Bekliyor", "Başvuru Beklemede", "Kurum İncelemesinde", 
    "Yayında", "İtiraz Geldi - Savunma Bekliyor", "Tescil Tebliğ Beklemede", 
    "Tescillendi", "Reddedildi"
]:
    secilen_asama = st.session_state.aktif_sayfa
    
    top_col1, top_col2 = st.columns([2, 1])
    with top_col1:
        st.markdown(f"<h2>📂 Aşama: {secilen_asama}</h2>", unsafe_allow_html=True)
    with top_col2:
        arama_metni = st.text_input("🔍 Marka Ara", placeholder="Marka adı yazın...", key=f"arama_{secilen_asama}")
    
    asama_df = df[df['Durum'].astype(str).str.strip() == secilen_asama]
    
    if arama_metni.strip():
        asama_df = asama_df[asama_df['Marka Adı'].astype(str).str.contains(arama_metni.strip(), case=False, na=False)]
    
    if asama_df.empty:
        st.info(f"'{secilen_asama}' aşamasında aramanızla eşleşen kayıt bulunmuyor.")
    else:
        if secilen_asama == "Kurum İncelemesinde":
            gosterge_df = asama_df[['Marka Adı', 'Başvuru No', 'Kurum İnceleme Bitiş Tarihi']].copy()
            st.dataframe(gosterge_df, use_container_width=True)
        else:
            st.dataframe(asama_df, use_container_width=True)
            
        st.write("---")
        
        if secilen_asama == "Muhasebe Onayı Bekliyor":
            st.subheader("✅ Onay Bekleyen Satışları Faturalandır ve Başvuru Beklemede'ye Al")
            for i, row in asama_df.iterrows():
                with st.container():
                    st.markdown(f"Marka: **{row['Marka Adı']}** | Satışı Giren Danışman: *{row['Danışman']}* | Tutar: **{row['Tutar']} TL**")
                    c1, c2, c3 = st.columns(3)
                    f_no = c1.text_input("Fatura No", key=f"f_no_{row['Marka Adı']}")
                    f_tarih = c2.text_input("Fatura Tarihi (GG/AA/YYYY)", value=datetime.now().strftime("%d/%m/%Y"), key=f"f_tar_{row['Marka Adı']}")
                    
                    if c3.button("✅ Onayla ve Başvuru Beklemede Yap", key=f"onay_btn_{row['Marka Adı']}"):
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

                    # Mevcut Değerler (Kayıtlı Veriler)
                    mevcut_b_no = str(s_row.get('Başvuru No', '')) if pd.notna(s_row.get('Başvuru No')) else ""
                    mevcut_b_tar = str(s_row.get('Başvuru Tarihi', '')) if pd.notna(s_row.get('Başvuru Tarihi')) else ""
                    mevcut_kurum_bitis = str(s_row.get('Kurum İnceleme Bitiş Tarihi', '')) if pd.notna(s_row.get('Kurum İnceleme Bitiş Tarihi')) else ""

                    # Eğer daha önce girilmişse kilitli (disabled=True), boşsa yeni giriş için aktif tutulabilir
                    b_no_disabled = bool(mevcut_b_no.strip() and mevcut_b_no != 'nan')
                    b_tar_disabled = bool(mevcut_b_tar.strip() and mevcut_b_tar != 'nan')
                    kurum_bitis_disabled = bool(mevcut_kurum_bitis.strip() and mevcut_kurum_bitis != 'nan')

                    b_no = c1.text_input("Başvuru No", value=mevcut_b_no if mevcut_b_no != 'nan' else "", disabled=b_no_disabled)
                    b_tarih = c2.text_input("Başvuru Tarihi (GG/AA/YYYY)", value=mevcut_b_tar if mevcut_b_tar != 'nan' else datetime.now().strftime("%d/%m/%Y"), disabled=b_tar_disabled, key=f"form_b_tar_{secilen_marka}")
                    
                    default_bitis = ""
                    if b_tarih.strip():
                        try:
                            parsed_b_tar = datetime.strptime(b_tarih.strip(), "%d/%m/%Y")
                            default_bitis = (parsed_b_tar + timedelta(days=30)).strftime("%d/%m/%Y")
                        except:
                            default_bitis = datetime.now().strftime("%d/%m/%Y")

                    final_bitis_val = mevcut_kurum_bitis if mevcut_kurum_bitis and mevcut_kurum_bitis != 'nan' else default_bitis

                    kurum_bitis = c1.text_input("Kurum İnceleme Bitiş Tarihi (GG/AA/YYYY)", value=final_bitis_val, disabled=kurum_bitis_disabled, key=f"form_kurum_bitis_{secilen_marka}")

                    y_tar_val = str(s_row.get('Yayın Tarihi', ''))
                    y_tar = c2.text_input("Yayın Tarihi (GG/AA/YYYY)", value=y_tar_val if y_tar_val and y_tar_val != 'nan' else "", key=f"form_y_tar_{secilen_marka}")
                    
                    if st.form_submit_button("💾 Kaydı Güncelle"):
                        final_durum = yeni_durum
                        if secilen_asama == "Kurum İncelemesinde" and y_tar.strip():
                            final_durum = "Yayında"

                        idx = df.index[(df['Durum'].astype(str).str.strip() == secilen_asama) & (df['Marka Adı'].astype(str) == secilen_marka)][0]
                        df.at[idx, 'Durum'] = final_durum
                        df.at[idx, 'Danışman'] = orijinal_danisman
                        
                        # Sadece daha önceden boşsa güncellemelerine izin ver, doluysa sabit tut
                        if not b_no_disabled and b_no.strip():
                            df.at[idx, 'Başvuru No'] = b_no.strip()
                        if not b_tar_disabled and b_tarih.strip():
                            df.at[idx, 'Başvuru Tarihi'] = b_tarih.strip()
                        if not kurum_bitis_disabled and kurum_bitis.strip():
                            df.at[idx, 'Kurum İnceleme Bitiş Tarihi'] = kurum_bitis.strip()
                            
                        df.at[idx, 'Yayın Tarihi'] = y_tar.strip()
                        df.to_csv(DATA_FILE, index=False)
                        
                        if final_durum == "Yayında" and secilen_asama != "Yayında":
                            st.success(f"✅ Yayın Tarihi girildiği için '{secilen_marka}' otomatik olarak 'Yayında' aşamasına taşındı!")
                        else:
                            st.success(f"✅ '{secilen_marka}' markasına ait kayıt başarıyla güncellendi!")
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
