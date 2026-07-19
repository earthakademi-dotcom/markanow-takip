import streamlit as st
import pandas as pd
import os

# STREAMING_CHUNK: Kullanıcı Tanımları ve Şifreler
DATA_FILE = "marka_takip.csv"
KULLANICILAR = {
    "Ali Osman Yelbey": {"sifre": "MarkanowAdmin2026!", "rol": "Admin"},
    "MERVE YURTLU": {"sifre": "MerveDanisman789!", "rol": "Satış Danışmanı"},
    "Muhasebe Kullanıcısı": {"sifre": "Muhasebe987!", "rol": "Muhasebe"},
    "Operasyon Yetkilisi": {"sifre": "Op123456!", "rol": "Operasyon"}
}

def load_data():
    if os.path.exists(DATA_FILE): return pd.read_csv(DATA_FILE)
    return pd.DataFrame(columns=["ID", "Marka Adı", "Ad Soyad", "TC", "Telefon", "Tutar", "Durum", "Rol"])

st.set_page_config(page_title="Markanow ERP", layout="wide")

# STREAMING_CHUNK: Giriş Mantığı ve Şifre Kontrolü
if "kullanici" not in st.session_state: st.session_state.kullanici = None

if not st.session_state.kullanici:
    st.title("🔒 Markanow Giriş")
    k = st.selectbox("Kullanıcı", list(KULLANICILAR.keys()))
    sifre = st.text_input("Şifre", type="password")
    
    if st.button("Giriş Yap"):
        if sifre == KULLANICILAR[k]["sifre"]:
            st.session_state.kullanici = k
            st.session_state.rol = KULLANICILAR[k]["rol"]
            st.rerun()
        else:
            st.error("Hatalı Şifre!")
    st.stop()

# STREAMING_CHUNK: Sidebar ve Menü
with st.sidebar:
    st.write(f"👤 Kullanıcı: {st.session_state.kullanici}")
    st.write(f"🛡️ Rol: {st.session_state.rol}")
    st.markdown("---")
    menu = st.radio("Menü", ["📝 Satış Girişi"])
    st.markdown("---")
    if st.button("🚪 Çıkış"): st.session_state.kullanici = None; st.rerun()

# STREAMING_CHUNK: Satış Girişi (Adım 1 devamı)
df = load_data()
if menu == "📝 Satış Girişi":
    st.header("📝 Yeni Satış Kaydı")
    with st.form("temel_satis"):
        marka = st.text_input("Marka Adı")
        submit = st.form_submit_button("Kaydet")
        if submit:
            new_row = {"ID": len(df)+1, "Marka Adı": marka, "Durum": "Yeni"}
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            df.to_csv(DATA_FILE, index=False)
            st.success("Kaydedildi!")
