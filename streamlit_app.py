import streamlit as st
import pandas as pd
import os
import base64
from datetime import datetime

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
        "Başvuru No", "Başvuru Tarihi", "Yayın Tarihi", "Tescil Tebliğ Tarihi"
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
    st.sidebar.markdown("### 📋 Marka Tescil Aşamaları")
    if st.sidebar.button("📌 Muhasebe Onayı Bekliyor", use_container_width=True):
        sayfa_degistir("Muhasebe Onayı Bekliyor")
    if st.sidebar.button("⏳ Başvuru Beklemede", use_container_width=True):
        sayfa_degistir("Başvuru Beklemede")
    if st.sidebar.button("🔍 Kurum İncelemesinde", use_container_width=True):
        sayfa_degistir("Kurum İncelemesinde")
    if st.sidebar.button("📰 Yayında", use_container_width=True):
        sayfa_degistir("Yayında")
    if st.sidebar.button("⚠️ İtiraz / Savunma Bekliyor", use_container_width=True):
        sayfa_degistir("İtiraz Geldi - Savunma Bekliyor")
    if st.sidebar.button("📄 Tescil Tebliğ Beklemede", use_container_width=True):
        sayfa_degistir("Tescil Tebliğ Beklemede")
    if st.sidebar.button("🎉 Tescillendi", use_container_width=True):
        sayfa_degistir("Tescillendi")
    if st.sidebar.button("❌ Reddedildi", use_container_width=True):
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
        
    st.markdown(f"<h2>📝 Yeni Satış Girişi (Danışman: {aktif_kullanici_ad})</h2>", unsafe_allow_html=True)
    
    with st.form("yeni_satis_formu", clear_on_submit=True):
        c1, c2 = st.columns(2)
        m_adi = c1.text_input("Marka Adı")
        ad_soyad = c1.text_input("İsim Soyisim")
        tc = c1.text_input("TC (11 Hane)")
        tel = c1.text_input("Telefon")
        
        st.markdown("<p style='color: white; font-weight: bold; margin-bottom: 0px;'>Doğum Tarihi</p>", unsafe_allow_html=True)
        d1, d2, d3 = st.columns(3)
        gun = d1.selectbox("Gün", range(1, 32))
        ay = d2.selectbox("Ay", range(1, 13))
        yil = d3.selectbox("Yıl", range(datetime.now().year, 1919, -1))
        
        il = c2.selectbox("İl", ILLER)
        sinif = c2.multiselect("Sınıf Seçimi", SINIFLAR)
        odeme = c2.selectbox("Ödeme Türü", ["EFT", "Kredi Kartı"])
        s_tarihi = c2.date_input("Satış Tarihi")
        tutar = c2.number_input("Tutar (TL)", min_value=0.0)
        
        if st.form_submit_button("Satışı Kaydet"):
            new_row = {
                "Marka Adı": m_adi, "Ad Soyad": ad_soyad, "TC": tc, "Telefon": tel, 
                "Doğum Tarihi": f"{gun:02d}/{ay:02d}/{yil}", "İl": il, "Sınıf": ",".join(sinif), "Ödeme": odeme, 
                "Satış Tarihi": s_tarihi.strftime("%d/%m/%Y"), "Tutar": str(tutar), "Durum": "Muhasebe Onayı Bekliyor", 
                "Danışman": aktif_kullanici_ad, "Fatura No": "", "Fatura Tarihi": "", "Başvuru No": "", "Başvuru Tarihi": "", "Yayın Tarihi": "", "Tescil Tebliğ Tarihi": ""
            }
            guncel_df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            guncel_df.to_csv(DATA_FILE, index=False)
            st.success("✅ Satış başarıyla kaydedildi ve onay için muhasebeye gönderildi.")

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
        st.dataframe(asama_df, use_container_width=True)
        st.write("---")
        
        if secilen_asama == "Muhasebe Onayı Bekliyor":
            st.subheader("✅ Onay Bekleyen Satışları Faturalandır ve Başvuru Beklemede'ye Al")
            for i, row in asama_df.iterrows():
                with st.container():
                    st.markdown(f"Marka: **{row['Marka Adı']}** | Danışman: *{row['Danışman']}* | Tutar: **{row['Tutar']} TL**")
                    c1, c2, c3 = st.columns(3)
                    f_no = c1.text_input("Fatura No", key=f"f_no_{row['Marka Adı']}")
                    f_tarih = c2.date_input("Fatura Tarihi", value=datetime.now(), key=f"f_tar_{row['Marka Adı']}")
                    
                    if c3.button("✅ Onayla ve Başvuru Beklemede Yap", key=f"onay_btn_{row['Marka Adı']}"):
                        if f_no.strip():
                            idx = df.index[df['Marka Adı'].astype(str) == str(row['Marka Adı'])][0]
                            df.at[idx, 'Durum'] = "Başvuru Beklemede"
                            df.at[idx, 'Fatura No'] = f_no.strip()
                            df.at[idx, 'Fatura Tarihi'] = f_tarih.strftime("%d/%m/%Y")
                            df.at[idx, 'Danışman'] = aktif_kullanici_ad
                            df.to_csv(DATA_FILE, index=False)
                            st.success(f"✅ '{row['Marka Adı']}' onaylandı ve 'Başvuru Beklemede' aşamasına taşındı!")
                            st.rerun()
                        else:
                            st.warning("Lütfen bir Fatura No girin.")
                    st.write("---")
        else:
            st.subheader("✏️ Marka Bilgilerini ve Durumunu Güncelle")
            
            marka_listesi = asama_df['Marka Adı'].astype(str).tolist()
            secilen_marka = st.selectbox("İşlem Yapılacak Markayı Seçin", options=marka_listesi, key=f"sel_marka_{secilen_asama}")
            
            if secilen_marka:
                s_row = df[(df['Durum'].astype(str).str.strip() == secilen_asama) & (df['Marka Adı'].astype(str) == secilen_marka)].iloc[0]
                st.markdown(f"**Seçilen Marka:** {s_row['Marka Adı']} | **Danışman:** {s_row['Danışman']}")
                
                with st.form(f"form_guncelle_{secilen_marka}"):
                    c1, c2 = st.columns(2)
                    
                    # Durum alanını o anki aşamada sabit tutuyoruz (değiştirilemez)
                    c1.text_input("Yeni Durum / Aşama", value=secilen_asama, disabled=True)
                    yeni_durum = secilen_asama
                    
                    if os.path.exists(USER_FILE):
                        u_df = pd.read_csv(USER_FILE)
                        personel_listesi = u_df["İsim"].tolist()
                    else:
                        personel_listesi = [aktif_kullanici_ad]
                    
                    mevcut_danisman = str(s_row.get('Danışman', aktif_kullanici_ad)).strip().upper()
                    if mevcut_danisman not in personel_listesi:
                        personel_listesi.append(mevcut_danisman)
                    
                    danisman_secim = c2.selectbox("Danışman", options=personel_listesi, index=personel_listesi.index(mevcut_danisman) if mevcut_danisman in personel_listesi else 0)

                    f_no = c1.text_input("Fatura No", value=str(s_row.get('Fatura No', '')) if pd.notna(s_row.get('Fatura No')) else "")
                    f_tarih_val = str(s_row.get('Fatura Tarihi', ''))
                    try:
                        f_tarih_parsed = datetime.strptime(f_tarih_val, "%d/%m/%Y") if f_tarih_val and f_tarih_val != 'nan' else datetime.now()
                    except:
                        f_tarih_parsed = datetime.now()
                    f_tarih = c2.date_input("Fatura Tarihi", value=f_tarih_parsed, key=f"form_f_tar_{secilen_marka}")
                    
                    b_no = c1.text_input("Başvuru No", value=str(s_row.get('Başvuru No', '')) if pd.notna(s_row.get('Başvuru No')) else "")
                    b_tarih_val = str(s_row.get('Başvuru Tarihi', ''))
                    try:
                        b_tarih_parsed = datetime.strptime(b_tarih_val, "%d/%m/%Y") if b_tarih_val and b_tarih_val != 'nan' else datetime.now()
                    except:
                        b_tarih_parsed = datetime.now()
                    b_tarih = c2.date_input("Başvuru Tarihi", value=b_tarih_parsed, key=f"form_b_tar_{secilen_marka}")
                    
                    if secilen_asama == "Başvuru Beklemede":
                        y_tar = str(s_row.get('Yayın Tarihi', ''))
                        t_tar = str(s_row.get('Tescil Tebliğ Tarihi', ''))
                    else:
                        y_tar = c1.text_input("Yayın Tarihi (GG/AA/YYYY)", value=str(s_row.get('Yayın Tarihi', '')) if pd.notna(s_row.get('Yayın Tarihi')) else "")
                        t_tar = c2.text_input("Tescil Tebliğ Tarihi (GG/AA/YYYY)", value=str(s_row.get('Tescil Tebliğ Tarihi', '')) if pd.notna(s_row.get('Tescil Tebliğ Tarihi')) else "")
                    
                    if st.form_submit_button("💾 Kaydı Güncelle"):
                        idx = df.index[(df['Durum'].astype(str).str.strip() == secilen_asama) & (df['Marka Adı'].astype(str) == secilen_marka)][0]
                        df.at[idx, 'Durum'] = yeni_durum
                        df.at[idx, 'Danışman'] = danisman_secim
                        df.at[idx, 'Fatura No'] = f_no.strip()
                        df.at[idx, 'Fatura Tarihi'] = f_tarih.strftime("%d/%m/%Y")
                        df.at[idx, 'Başvuru No'] = b_no.strip()
                        df.at[idx, 'Başvuru Tarihi'] = b_tarih.strftime("%d/%m/%Y")
                        df.at[idx, 'Yayın Tarihi'] = y_tar.strip()
                        df.at[idx, 'Tescil Tebliğ Tarihi'] = t_tar.strip()
                        df.to_csv(DATA_FILE, index=False)
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
