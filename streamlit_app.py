import streamlit as st
import pandas as pd

# STREAMING_CHUNK: Kullanıcı Veritabanı ve Yetki Tanımları
KULLANICILAR = {
    "Ali Osman Yelbey": {"sifre": "MarkanowAdmin2026!", "rol": "Admin"},
    "Buğra Büyükeren": {"sifre": "BugraVekil456!", "rol": "Admin"},
    "MERVE YURTLU": {"sifre": "MerveDanisman789!", "rol": "Danışman"},
    "Ahmet Yılmaz": {"sifre": "AhmetDanisman321!", "rol": "Danışman"},
    "Muhasebe Kullanıcısı": {"sifre": "Muhasebe987!", "rol": "Muhasebe"},
    "Operasyon Yetkilisi": {"sifre": "Op123456!", "rol": "Operasyon"}
}

# STREAMING_CHUNK: Sayfa Yapılandırması ve Stilleri
st.set_page_config(page_title="Markanow ERP & Satış Takip", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    .login-card { max-width: 400px; margin: auto; padding: 40px; border-radius: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); background: white; text-align: center; }
    </style>
""", unsafe_allow_html=True)

# STREAMING_CHUNK: Oturum ve Veri Başlatma
if "giris_yapildi" not in st.session_state: st.session_state.giris_yapildi = False
if "markalar" not in st.session_state:
    st.session_state.markalar = pd.DataFrame(columns=["Marka Adı", "Müşteri", "Tutar", "Durum", "İşlem Yapan"])

# STREAMING_CHUNK: Giriş Ekranı
if not st.session_state.giris_yapildi:
    st.markdown('<div class="login-card">', unsafe_allow_html=True)
    st.markdown('<img src="https://i.imgur.com/zZJ3TZW.jpeg" style="width:250px; margin-bottom:20px;">', unsafe_allow_html=True)
    
    k_adi = st.selectbox("Kullanıcı Adı", list(KULLANICILAR.keys()))
    sifre = st.text_input("Şifre", type="password")
    
    if st.button("Sisteme Giriş Yap", use_container_width=True):
        if KULLANICILAR[k_adi]["sifre"] == sifre:
            st.session_state.giris_yapildi = True
            st.session_state.kullanici = k_adi
            st.session_state.rol = KULLANICILAR[k_adi]["rol"]
            st.rerun()
        else: st.error("Hatalı şifre!")
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# STREAMING_CHUNK: Sidebar ve Rol Bilgisi
st.sidebar.title(f"👤 {st.session_state.kullanici}")
st.sidebar.info(f"Görev: {st.session_state.rol}")
if st.sidebar.button("🚪 Güvenli Çıkış"):
    st.session_state.giris_yapildi = False
    st.rerun()

# STREAMING_CHUNK: Ana Panel ve Sekmeler
st.title(f"🏢 {st.session_state.rol} Yönetim Paneli")
tab1, tab2, tab3 = st.tabs(["📝 Satış Girişi", "⚙️ Operasyon & Onay", "📊 Finansal Raporlar"])

with tab1: # Satış Girişi (Danışman ve Admin)
    if st.session_state.rol in ["Admin", "Danışman"]:
        with st.form("satis_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            m_adi = col1.text_input("Marka Adı")
            tutar = col2.number_input("Tutar (TL)", min_value=0.0)
            if st.form_submit_button("Satış Kaydet"):
                yeni = pd.DataFrame([[m_adi, "Müşteri", tutar, "Bekliyor", st.session_state.kullanici]], columns=st.session_state.markalar.columns)
                st.session_state.markalar = pd.concat([st.session_state.markalar, yeni], ignore_index=True)
                st.success("Satış sisteme eklendi.")
    else: st.warning("Bu bölüme sadece Danışmanlar ve Adminler erişebilir.")

with tab2: # Operasyon (Operasyon ve Admin)
    if st.session_state.rol in ["Admin", "Operasyon"]:
        st.subheader("Operasyonel İşlemler")
        st.dataframe(st.session_state.markalar, use_container_width=True)
        if st.button("Seçilenleri Onayla"):
            st.session_state.markalar["Durum"] = "Onaylandı"
            st.success("Satışlar operasyon tarafından onaylandı.")
    else: st.warning("Bu bölüme sadece Operasyon yetkilileri erişebilir.")

with tab3: # Muhasebe ve Raporlar (Muhasebe ve Admin)
    if st.session_state.rol in ["Admin", "Muhasebe"]:
        st.subheader("Finansal Raporlar")
        toplam = st.session_state.markalar["Tutar"].sum()
        st.metric("Toplam Ciro", f"{toplam:,.2f} TL")
        st.bar_chart(st.session_state.markalar.set_index("Marka Adı")["Tutar"])
    else: st.warning("Bu bölüme sadece Muhasebe yetkilileri erişebilir.")
