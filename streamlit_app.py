import streamlit as st
import pandas as pd
import os

# STREAMING_CHUNK: Tanımlamalar
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
    if os.path.exists(DATA_FILE): return pd.read_csv(DATA_FILE)
    return pd.DataFrame(columns=["ID", "Marka Adı", "Ad Soyad", "TC Kimlik", "Telefon", "Doğum Tarihi", "İl", "Sınıf", "Satış Tarihi", "Tutar", "Durum", "Danışman"])

st.set_page_config(page_title="Markanow ERP", layout="wide")

# STREAMING_CHUNK: Giriş Kontrolü
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

# STREAMING_CHUNK: Sol Menü (Sidebar)
with st.sidebar:
    st.title("📂 Markanow ERP")
    st.write(f"👤 **Kullanıcı:** {st.session_state.kullanici}")
    st.write(f"🛡️ **Rol:** {st.session_state.rol}")
    st.markdown("---")
    menu = st.radio("Menü", ["📝 Satış Girişi", "⚙️ Operasyon Onay", "📊 Finansal Raporlar"])
    st.markdown("---")
    if st.button("🚪 Güvenli Çıkış"):
        st.session_state.giris_yapildi = False
        st.rerun()

# STREAMING_CHUNK: Satış Girişi ve Form Detayları
df = load_data()

if menu == "📝 Satış Girişi":
    st.header("📝 Yeni Satış Girişi")
    c1, c2 = st.columns(2)
    
    with c1:
        m_adi = st.text_input("Marka Adı*")
        ad_soyad = st.text_input("Müşteri Ad Soyad*")
        tc = st.text_input("TC Kimlik No (11 Hane)*")
        tel = st.text_input("Telefon (05xxxxxxxxx)*")
        
    with c2:
        dogum = st.date_input("Doğum Tarihi")
        il = st.selectbox("İl Seçin*", ILLER)
        sinif = st.multiselect("Sınıf Seçimi*", tum_sinif_secenekleri)
        s_tarihi = st.date_input("Satış Tarihi")
        
    tutar = st.number_input("Tutar (TL)*", min_value=0.0)
    
    if st.button("Satışı Kaydet"):
        # Doğrulama Kuralları
        if len(str(tc)) != 11 or not str(tel).startswith("05") or len(str(tel)) != 11:
            st.error("⚠️ TC Kimlik 11 hane ve Telefon 05 ile başlayan 11 hane olmalıdır!")
        else:
            new_row = {"ID": len(df)+1, "Marka Adı": m_adi, "Ad Soyad": ad_soyad, "TC Kimlik": tc, "Telefon": tel, 
                       "Doğum Tarihi": dogum.strftime("%d.%m.%Y"), "İl": il, "Sınıf": ", ".join(sinif), 
                       "Satış Tarihi": s_tarihi.strftime("%d.%m.%Y"), "Tutar": tutar, "Durum": "Bekliyor", "Danışman": st.session_state.kullanici}
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            df.to_csv(DATA_FILE, index=False)
            st.success("Kayıt başarıyla tamamlandı.")

elif menu == "⚙️ Operasyon Onay":
    st.header("⚙️ Operasyonel Süreçler")
    st.dataframe(df)

elif menu == "📊 Finansal Raporlar":
    st.header("📊 Finansal Raporlar")
    if not df.empty:
        st.metric("Toplam Ciro", f"{df['Tutar'].sum():,.2f} TL")
