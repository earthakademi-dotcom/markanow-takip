import streamlit as st
import pandas as pd
import os

# STREAMING_CHUNK: Kullanıcı Tanımları
KULLANICILAR = {
    "Ali Osman Yelbey": {"sifre": "MarkanowAdmin2026!", "rol": "Admin"},
    "MERVE YURTLU": {"sifre": "MerveDanisman789!", "rol": "Danışman"},
    "Muhasebe Kullanıcısı": {"sifre": "Muhasebe987!", "rol": "Muhasebe"},
    "Operasyon Yetkilisi": {"sifre": "Op123456!", "rol": "Operasyon"}
}

ILLER = ["Adana", "Ankara", "İstanbul", "İzmir", "Bursa", "Antalya", "Konya", "Diğer"] # Uzun listeyi kısalttım, dilediğinizce artırabilirsiniz.
DATA_FILE = "marka_satislar.csv"
siniflar = [str(i) for i in range(1, 46)]
alt_siniflar_35 = [f"35/{i}" for i in range(1, 35)]
tum_sinif_secenekleri = siniflar + alt_siniflar_35

def load_data():
    cols = ["ID", "Marka Adı", "Ad Soyad", "TC Kimlik", "İl", "Sınıf", "Satış Tarihi", "Tutar", "Durum", "Danışman"]
    if os.path.exists(DATA_FILE): 
        df = pd.read_csv(DATA_FILE)
        df['Satış Tarihi'] = pd.to_datetime(df['Satış Tarihi'])
        return df
    return pd.DataFrame(columns=cols)

st.set_page_config(page_title="Markanow ERP", layout="wide")

# STREAMING_CHUNK: Güvenli Giriş Sistemi
if "giris_yapildi" not in st.session_state: st.session_state.giris_yapildi = False

if not st.session_state.giris_yapildi:
    st.markdown('<div class="login-card" style="max-width:400px; margin:auto; padding:40px; border-radius:20px; box-shadow:0 4px 15px rgba(0,0,0,0.1); background:white; text-align:center;">', unsafe_allow_html=True)
    st.markdown('<img src="https://i.imgur.com/zZJ3TZW.jpeg" style="width:250px; margin-bottom:20px;">', unsafe_allow_html=True)
    k_adi = st.selectbox("Kullanıcı Adı", list(KULLANICILAR.keys()))
    sifre = st.text_input("Şifre", type="password")
    if st.button("Giriş Yap", use_container_width=True):
        if KULLANICILAR[k_adi]["sifre"] == sifre:
            st.session_state.giris_yapildi = True
            st.session_state.kullanici = k_adi
            st.session_state.rol = KULLANICILAR[k_adi]["rol"]
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# STREAMING_CHUNK: Sidebar ve Navigasyon
with st.sidebar:
    st.title(f"👤 {st.session_state.kullanici}")
    st.info(f"Görev: {st.session_state.rol}")
    if st.button("🚪 Güvenli Çıkış"):
        st.session_state.giris_yapildi = False
        st.rerun()

# STREAMING_CHUNK: Ana Panel ve Hata Yönetimi
df = load_data()
st.title("🏢 Markanow Satış Yönetim Paneli")

tab1, tab2, tab3 = st.tabs(["📝 Satış Girişi", "⚙️ Operasyon Onay", "📊 Finansal Raporlar"])

with tab1:
    with st.form("detayli_satis", clear_on_submit=True):
        c1, c2 = st.columns(2)
        marka = c1.text_input("Marka Adı")
        ad_soyad = c1.text_input("Müşteri Ad Soyad")
        tc = c1.text_input("TC Kimlik No")
        il = c2.selectbox("İl Seçin", ILLER)
        sinif = c2.multiselect("Sınıf Seçimi", tum_sinif_secenekleri)
        tarih = c2.date_input("Satış Tarihi")
        tutar = st.number_input("Tutar (TL)", min_value=0.0)
        if st.form_submit_button("Satışı Kaydet"):
            new_row = {"ID": len(df)+1, "Marka Adı": marka, "Ad Soyad": ad_soyad, "TC Kimlik": tc, 
                       "İl": il, "Sınıf": ", ".join(sinif), "Satış Tarihi": tarih, "Tutar": tutar, 
                       "Durum": "Bekliyor", "Danışman": st.session_state.kullanici}
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            df.to_csv(DATA_FILE, index=False)
            st.rerun()

with tab3: # Raporlar (Hata Giderilmiş)
    if not df.empty:
        aylar = sorted(df['Satış Tarihi'].dt.month.unique())
        ay_secimi = st.selectbox("Raporlanacak Ay", aylar)
        filtered_df = df[df['Satış Tarihi'].dt.month == ay_secimi]
        col1, col2 = st.columns(2)
        col1.metric("Toplam Satış Adedi", len(filtered_df))
        col2.metric("Toplam Ciro", f"{filtered_df['Tutar'].sum():,.2f} TL")
        st.bar_chart(filtered_df.set_index("Marka Adı")["Tutar"])
    else: st.info("Henüz veri girişi yapılmamış.")
