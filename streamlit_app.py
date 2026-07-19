import streamlit as st
import pandas as pd
import os

# STREAMING_CHUNK: Kullanıcılar ve Veri Hazırlığı
KULLANICILAR = {
    "Ali Osman Yelbey": {"sifre": "MarkanowAdmin2026!", "rol": "Admin"},
    "MERVE YURTLU": {"sifre": "MerveDanisman789!", "rol": "Danışman"},
    "Muhasebe Kullanıcısı": {"sifre": "Muhasebe987!", "rol": "Muhasebe"},
    "Operasyon Yetkilisi": {"sifre": "Op123456!", "rol": "Operasyon"}
}

DATA_FILE = "marka_satislar.csv"

# Sınıf listeleri
siniflar = [str(i) for i in range(1, 46)]
alt_siniflar_35 = [f"35/{i}" for i in range(1, 35)]
tum_sinif_secenekleri = siniflar + alt_siniflar_35

def load_data():
    cols = ["ID", "Marka Adı", "Ad Soyad", "TC Kimlik", "İl", "Sınıf", "Satış Tarihi", "Tutar", "Durum", "Danışman"]
    if os.path.exists(DATA_FILE): return pd.read_csv(DATA_FILE)
    return pd.DataFrame(columns=cols)

st.set_page_config(page_title="Markanow ERP", layout="wide")

# STREAMING_CHUNK: Giriş Kontrolü
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

# STREAMING_CHUNK: Ana Yönetim Paneli ve Form
df = load_data()

st.title("📊 Markanow Satış Takip")
tab1, tab2, tab3 = st.tabs(["📝 Yeni Satış Girişi", "⚙️ Operasyon Onay", "📈 Finansal Raporlar"])

with tab1: # Detaylı Satış Formu
    with st.form("yeni_satis_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        marka = col1.text_input("Marka Adı")
        ad_soyad = col1.text_input("Müşteri Ad Soyad")
        tc = col1.text_input("TC Kimlik No")
        il = col2.selectbox("İl", ["İstanbul", "Ankara", "İzmir", "Bursa", "Diğer"])
        sinif = col2.multiselect("Sınıf Bilgisi", tum_sinif_secenekleri)
        tarih = col2.date_input("Satış Tarihi")
        tutar = st.number_input("Tutar (TL)", min_value=0.0)
        
        if st.form_submit_button("Satışı Kaydet"):
            new_data = {"ID": len(df)+1, "Marka Adı": marka, "Ad Soyad": ad_soyad, "TC Kimlik": tc, 
                        "İl": il, "Sınıf": ", ".join(sinif), "Satış Tarihi": tarih, "Tutar": tutar, 
                        "Durum": "Bekliyor", "Danışman": st.session_state.kullanici}
            df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
            df.to_csv(DATA_FILE, index=False)
            st.success("Kayıt başarılı!")

with tab2: # Operasyon Paneli
    st.dataframe(df, use_container_width=True)
    onay_id = st.number_input("Onaylanacak Satış ID", min_value=1)
    if st.button("Seçili Kaydı Onayla"):
        df.loc[df['ID'] == onay_id, 'Durum'] = 'Onaylandı'
        df.to_csv(DATA_FILE, index=False)
        st.rerun()

with tab3: # Raporlar
    st.metric("Toplam Satış Hacmi", f"{df['Tutar'].sum():,.2f} TL")
    st.bar_chart(df.set_index("Marka Adı")["Tutar"])

