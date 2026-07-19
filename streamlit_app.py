import streamlit as st

st.set_page_config(page_title="Markanow ERP", layout="wide")

# --- 1. OTURUM VE MENU TANIMLARI ---
if "giris_yapildi" not in st.session_state: st.session_state.giris_yapildi = False
if "menu" not in st.session_state: st.session_state.menu = "Basvuru_Beklemede"

# --- 2. LOGIN EKRANI ---
if not st.session_state.giris_yapildi:
    st.title("🔒 Markanow Giriş")
    kullanici = st.text_input("Kullanıcı Adı")
    sifre = st.text_input("Şifre", type="password")
    if st.button("Giriş Yap"):
        # Buraya kendi kullanıcı kontrol mantığınızı ekleyin
        if kullanici == "admin" and sifre == "1234":
            st.session_state.giris_yapildi = True
            st.rerun()
        else:
            st.error("Hatalı giriş!")
    st.stop() # Giriş yapılmadıysa aşağısını çalıştırma

# --- 3. ANA UYGULAMA (Giriş yapıldıktan sonra) ---
with st.sidebar:
    st.markdown("### 🏢 Markanow ERP")
    if st.button("⏳ Başvuru Beklemede"): 
        st.session_state.menu = "Basvuru_Beklemede"
        st.rerun()
    if st.button("🔑 Şifre Ayarları"): 
        st.session_state.menu = "Sifre_Ayarlari"
        st.rerun()
    st.markdown("---")
    if st.button("🚪 Güvenli Çıkış"):
        st.session_state.giris_yapildi = False
        st.rerun()

# --- 4. SAYFA YÖNETİMİ ---
if st.session_state.menu == "Basvuru_Beklemede":
    st.header("⏳ Başvuru Beklemede")
    st.write("Süreçteki dosyalarınız burada görünecek.")

elif st.session_state.menu == "Sifre_Ayarlari":
    st.header("🔑 Şifre Yönetimi")
    st.write("Şifrenizi buradan güncelleyebilirsiniz.")
