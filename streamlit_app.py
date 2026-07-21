import streamlit as st
import pandas as pd
import os
import json
import base64
from datetime import datetime

# --- SAYFA YAPILANDIRMASI ---
st.set_page_config(page_title="Markanow ERP", layout="wide")

# --- GLOBAL CSS (SİDEBAR VE YAZI RENKLERİ) ---
st.markdown(
    """
    <style>
    /* Tüm başlıkları, etiketleri ve form yazılarını beyaz yapar */
    h1, h2, h3, h4, h5, h6, 
    .stTextInput label, 
    .stSelectbox label, 
    .stDateInput label, 
    .stNumberInput label, 
    .stMultiSelect label,
    div[data-testid="stMarkdownContainer"] p {
        color: #FFFFFF !important;
    }
    
    /* Sidebar (Menü) arka planını koyu antrasit yapar ve yazılarını beyaz yapar */
    [data-testid="stSidebar"] {
        background-color: #1a1a1a !important;
    }
    [data-testid="stSidebar"] span, [data-testid="stSidebar"] p, [data-testid="stSidebar"] label, [data-testid="stSidebar"] div {
        color: #FFFFFF !important;
    }
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
logo_path = "sosyalmedya-2.jpg.jpg"

if os.path.exists(logo_path):
    with open(logo_path, "rb") as f:
        bin_str = base64.b64encode(f.read()).decode()
    
    page_bg_img = f'''
    <style>
    .stApp {{
        background: linear-gradient(rgba(30, 30, 30, 0.8), rgba(30, 30, 30, 0.8)), url("data:image/jpeg;base64,{bin_str}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}
    .stSelectbox label, .stTextInput label {{
        color: #FFFFFF !important;
        font-weight: bold;
    }}
    </style>
    '''
    st.markdown(page_bg_img, unsafe_allow_html=True)
else:
    st.markdown(
        """
        <style>
        .stApp {
            background-color: #222222;
        }
        .stSelectbox label, .stTextInput label {
            color: #FFFFFF !important;
            font-weight: bold;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

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
    st.header("📥 Excel/CSV ile Toplu Satış Girişi")
    uploaded_file = st.file_uploader("Dosya Seçin", type=["csv", "xlsx"])
    if uploaded_file:
        yeni_data = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
        if st.button("Tümünü Sisteme Ekle"):
            pd.concat([df, yeni_data], ignore_index=True).to_csv(DATA_FILE, index=False)
            st.success("Tüm satışlar başarıyla aktarıldı!"); st.rerun()

elif menu == "💰 Muhasebe Onayı":
    st.header("💰 Muhasebe Onay ve Tam Düzenleme Paneli")
    with st.expander("✏️ TÜM SATIŞ BİLGİLERİNİ TAM DÜZENLE"):
        secili_id = st.number_input("Düzenlenecek Satış ID", step=1)
        if secili_id in df['ID'].values:
            row = df[df['ID'] == secili_id].iloc[0]
            with st.form("tam_duzenleme_formu"):
                c1, c2 = st.columns(2)
                v_m, v_a, v_t, v_tl = c1.text_input("Marka", value=row['Marka Adı']), c1.text_input("İsim", value=row['Ad Soyad']), c1.text_input("TC", value=row['TC']), c1.text_input("Tel", value=row['Telefon'])
                v_d, v_i, v_s = c2.text_input("Doğum", value=row['Doğum Tarihi']), c2.selectbox("İl", ILLER, index=ILLER.index(row['İl']) if row['İl'] in ILLER else 0), c2.text_input("Sınıf", value=row['Sınıf'])
                v_o, v_tu, v_du, v_f = c2.selectbox("Ödeme", ["EFT", "Kredi Kartı"], index=["EFT", "Kredi Kartı"].index(row['Ödeme'])), c2.number_input("Tutar", value=float(row['Tutar'])), c1.selectbox("Durum", ["Muhasebe Onayı Bekliyor", "Onaylandı", "Tamamlandı"], index=["Muhasebe Onayı Bekliyor", "Onaylandı", "Tamamlandı"].index(row['Durum'])), c2.text_input("Fatura No", value=str(row['Fatura No']) if pd.notna(row['Fatura No']) else "")
                if st.form_submit_button("TÜMÜNÜ GÜNCELLE"):
                    df.loc[df['ID'] == secili_id, ['Marka Adı', 'Ad Soyad', 'TC', 'Telefon', 'Doğum Tarihi', 'İl', 'Sınıf', 'Ödeme', 'Tutar', 'Durum', 'Fatura No']] = [v_m, v_a, v_t, v_tl, v_d, v_i, v_s, v_o, v_tu, v_du, v_f]
                    df.to_csv(DATA_FILE, index=False); st.success("Güncellendi!"); st.rerun()
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
