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
    }}
    
    [data-testid="stSidebar"] span, 
    [data-testid="stSidebar"] p, 
    [data-testid="stSidebar"] label, 
    [data-testid="stSidebar"] div, 
    [data-testid="stSidebar"] .stRadio label {{
        color: #FFFFFF !important;
    }}

    div.stButton > button:first-child {{
        background-color: #6b1d2f !important;
        color: #FFFFFF !important;
        border: 1px solid #85243b !important;
    }}
    div.stButton > button:first-child:hover {{
        background-color: #85243b !important;
        color: #FFFFFF !important;
        border: 1px solid #9e2a45 !important;
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
        return pd.read_csv(DATA_FILE)
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
            new_row = {"ID": len(df)+1 if df.empty else df['ID'].max()+1, "Marka Adı": m_adi, "Ad Soyad": ad_soyad, "TC": tc, "Telefon": tel, 
                       "Doğum Tarihi": f"{gun:02d}/{ay:02d}/{yil}", "İl": il, "Sınıf": ",".join(sinif), "Ödeme": odeme, 
                       "Satış Tarihi": s_tarihi.strftime("%d/%m/%Y"), "Tutar": tutar, 
                       "Durum": "Muhasebe Onayı Bekliyor", "Danışman": st.session_state.kullanici, "Fatura No": ""}
            pd.concat([df, pd.DataFrame([new_row])], ignore_index=True).to_csv(DATA_FILE, index=False)
            st.success("Satış kaydedildi.")

elif menu == "📊 Satışlarım":
    st.header(f"📊 {st.session_state.kullanici} - Satışlarım")
    st.dataframe(df[df['Danışman'] == st.session_state.kullanici], use_container_width=True)

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
                    yeni_data = pd.read_csv(uploaded_file, encoding='utf-8', sep=None, engine='python', mangle_dup_cols=True)
                except Exception:
                    uploaded_file.seek(0)
                    try:
                        yeni_data = pd.read_csv(uploaded_file, encoding='latin-1', sep=None, engine='python', mangle_dup_cols=True)
                    except Exception:
                        uploaded_file.seek(0)
                        yeni_data = pd.read_csv(uploaded_file, encoding='cp1254', sep=None, engine='python', mangle_dup_cols=True)
            else:
                yeni_data = pd.read_excel(uploaded_file)
            
            # Sütun isimlerindeki boşlukları temizleme
            yeni_data.columns = [str(col).strip() for col in yeni_data.columns]
            
            # Yinelenen sütun isimleri varsa benzersizleştirme
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
                baslangic_id = int(df['ID'].max() + 1) if not df.empty and 'ID' in df.columns else 1
                yeni_data['ID'] = range(baslangic_id, baslangic_id + len(yeni_data))
                
                # Danışman sütunu tespiti ve satırdaki isimlerin atanması
                if 'Danışman' not in yeni_data.columns:
                    yeni_data['Danışman'] = st.session_state.kullanici
                else:
                    # Boş olan satırlar varsa oturum açan kullanıcıyı yaz, dolu olanlarda satırdaki ismi koru ve büyük harfe çevir
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
        toplu_secim_idleri = st.multiselect("İşlem Yapılacak Satış ID'lerini Seçin veya Girin", options=df['ID'].tolist())
        col_t1, col_t2, col_t3 = st.columns(3)
        with col_t1:
            if st.button("✅ Seçilenleri 'Onayla'", use_container_width=True):
                if toplu_secim_idleri:
                    df.loc[df['ID'].isin(toplu_secim_idleri), 'Durum'] = "Onaylandı"
                    df.to_csv(DATA_FILE, index=False)
                    st.success("Seçilen kayıtlar onaylandı!")
                    st.rerun()
                else:
                    st.warning("Lütfen en az bir ID seçin.")
        with col_t2:
            if st.button("🎯 Seçilenleri 'Tamamlandı' Yap", use_container_width=True):
                if toplu_secim_idleri:
                    df.loc[df['ID'].isin(toplu_secim_idleri), 'Durum'] = "Tamamlandı"
                    df.to_csv(DATA_FILE, index=False)
                    st.success("Seçilen kayıtlar tamamlandı olarak güncellendi!")
                    st.rerun()
                else:
                    st.warning("Lütfen en az bir ID seçin.")
        with col_t3:
            if st.button("❌ Seçilenleri Kalıcı Olarak Sil", use_container_width=True):
                if toplu_secim_idleri:
                    df = df[~df['ID'].isin(toplu_secim_idleri)]
                    df.to_csv(DATA_FILE, index=False)
                    st.success("Seçilen kayıtlar silindi!")
                    st.rerun()
                else:
                    st.warning("Lütfen en az bir ID seçin.")

    with st.expander("✏️ TÜM SATIŞ BİLGİLERİNİ TAM DÜZENLE"):
        secili_id = st.number_input("Düzenlenecek Satış ID", step=1)
        if secili_id in df['ID'].values:
            row = df[df['ID'] == secili_id].iloc[0]
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
                
                v_tu = c2.number_input("Tutar", value=float(row['Tutar']) if pd.notna(row['Tutar']) else 0.0)
                
                durum_secenekleri = ["Muhasebe Onayı Bekliyor", "Onaylandı", "Tamamlandı"]
                mevcut_durum = str(row['Durum']).strip() if pd.notna(row['Durum']) else "Muhasebe Onayı Bekliyor"
                durum_index = durum_secenekleri.index(mevcut_durum) if mevcut_durum in durum_secenekleri else 0
                v_du = c1.selectbox("Durum", durum_secenekleri, index=durum_index)
                
                v_f = c2.text_input("Fatura No", value=str(row['Fatura No']) if pd.notna(row['Fatura No']) and str(row['Fatura No']).lower() != 'nan' else "")
                
                if st.form_submit_button("TÜMÜNÜ GÜNCELLE"):
                    df.loc[df['ID'] == secili_id, ['Marka Adı', 'Ad Soyad', 'TC', 'Telefon', 'Doğum Tarihi', 'İl', 'Sınıf', 'Ödeme', 'Tutar', 'Durum', 'Fatura No']] = [v_m, v_a, v_t, v_tl, v_d, v_i, v_s, v_o, v_tu, v_du, v_f]
                    df.to_csv(DATA_FILE, index=False); st.success("Güncellendi!"); st.rerun()
                    
    st.write("---")
    st.subheader("📋 Tüm Satış Listesi ve Onay Bekleyenler")
    st.dataframe(df, use_container_width=True)
    
    for i, row in df[df['Durum'] == "Muhasebe Onayı Bekliyor"].iterrows():
        if st.button(f"✅ Onayla: {row['Marka Adı']} ({row['Tutar']} TL)", key=f"onay_{row['ID']}"):
            df.loc[df['ID'] == row['ID'], 'Durum'] = "Onaylandı"; df.to_csv(DATA_FILE, index=False); st.rerun()

elif menu == "📊 Performans Raporu":
    st.header("📊 Performans"); st.bar_chart(df[df['Durum'] == "Tamamlandı"].groupby('Danışman')['Tutar'].sum())

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
