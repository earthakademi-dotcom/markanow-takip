import streamlit as st
import pandas as pd
import os

# STREAMING_CHUNK: Yapılandırma ve Tanımlamalar
KULLANICILAR = {
    "Ali Osman Yelbey": {"sifre": "MarkanowAdmin2026!", "rol": "Admin"},
    "MERVE YURTLU": {"sifre": "MerveDanisman789!", "rol": "Danışman"},
    "Muhasebe Kullanıcısı": {"sifre": "Muhasebe987!", "rol": "Muhasebe"},
    "Operasyon Yetkilisi": {"sifre": "Op123456!", "rol": "Operasyon"}
}
ILLER = ["Adana", "Ankara", "İstanbul", "İzmir", "Bursa", "Antalya", "Konya", "Diğer"]
DATA_FILE = "marka_satislar.csv"
tum_sinif_secenekleri = [str(i) for i in range(1, 46)] + [f"35/{i}" for i in range(1, 35)]

def load_data():
    cols = ["ID", "Marka Adı", "Ad Soyad", "TC Kimlik", "Telefon", "Doğum Tarihi", "İl", "Sınıf", "Satış Tarihi", "Tutar", "Durum", "Danışman"]
    if os.path.exists(DATA_FILE): return pd.read_csv(DATA_FILE)
    return pd.DataFrame(columns=cols)

st.set_page_config(page_title="Markanow ERP", layout="wide")

# STREAMING_CHUNK: Giriş Sistemi
if "giris_yapildi" not in st.session_state: st.session_state.giris_yapildi = False

if not st.session_state.giris_yapildi:
    k_adi = st.selectbox("Kullanıcı Adı", list(KULLANICILAR.keys()))
    sifre = st.text_input("Şifre", type="password")
    if st.button("Giriş Yap"):
        if KULLANICILAR[k_adi]["sifre"] == sifre:
            st.session_state.giris_yapildi = True
            st.session_state.kullanici = k_adi
            st.session_state.rol = KULLANICILAR[k_adi]["rol"]
            st.rerun()
    st.stop()

# STREAMING_CHUNK: Dashboard ve Sekmeler
with st.sidebar:
    st.title(f"👤 {st.session_state.kullanici}")
    st.info(f"Görev: {st.session_state.rol}")
    if st.button("🚪 Güvenli Çıkış"):
        st.session_state.giris_yapildi = False
        st.rerun()

st.title("🏢 Markanow Satış Yönetim Paneli")
df = load_data()

# ÖNCE TABS TANIMLA, SONRA İÇİNE YAZ
tab1, tab2, tab3 = st.tabs(["📝 Satış Girişi", "⚙️ Operasyon Onay", "📊 Finansal Raporlar"])

with tab1:
    m_adi = st.text_input("Marka Adı*")
    ad_soyad = st.text_input("Müşteri Ad Soyad*")
    tc = st.text_input("TC Kimlik No (11 Hane)*")
    tel = st.text_input("Telefon (05xxxxxxxxx)*")
    dogum = st.date_input("Doğum Tarihi")
    il = st.selectbox("İl Seçin*", ILLER)
    sinif = st.multiselect("Sınıf Seçimi*", tum_sinif_secenekleri)
    satis_tarihi = st.date_input("Satış Tarihi")
    tutar = st.number_input("Tutar (TL)*", min_value=0.0)
    
    if st.button("Satışı Kaydet"):
        errors = []
        if not m_adi: errors.append("Marka Adı")
        if len(tc) != 11 or not tc.isdigit(): errors.append("TC Kimlik (11 haneli sayı olmalı)")
        if not tel.startswith("05") or len(tel) != 11: errors.append("Telefon (05 ile başlamalı ve 11 hane)")
        
        if errors:
            for e in errors: st.error(f"⚠️ {e}")
        else:
            new_row = {"ID": len(df)+1, "Marka Adı": m_adi, "Ad Soyad": ad_soyad, "TC Kimlik": tc, "Telefon": tel, 
                       "Doğum Tarihi": dogum.strftime("%d.%m.%Y"), "İl": il, "Sınıf": ", ".join(sinif), 
                       "Satış Tarihi": satis_tarihi.strftime("%d.%m.%Y"), "Tutar": tutar, "Durum": "Bekliyor", "Danışman": st.session_state.kullanici}
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            df.to_csv(DATA_FILE, index=False)
            st.success("Kaydedildi!")

with tab2:
    st.dataframe(df)
    onay_id = st.number_input("Onaylanacak ID", step=1)
    if st.button("Onayla"):
        df.loc[df['ID'] == onay_id, 'Durum'] = 'Onaylandı'
        df.to_csv(DATA_FILE, index=False)
        st.rerun()

with tab3:
    if not df.empty:
        st.metric("Toplam Ciro", f"{df['Tutar'].sum():,.2f} TL")
