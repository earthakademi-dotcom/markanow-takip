import streamlit as st
import pandas as pd
import os
import base64

# --- SAYFA YAPILANDIRMASI ---
st.set_page_config(page_title="Markanow ERP - Giriş", layout="wide")

# Logo dosyasını base64 formatına çevirme (varsa arka plan veya logo için)
logo_path = "sosyalmedya-2.jpg.jpg"
logo_base64 = ""
if os.path.exists(logo_path):
    with open(logo_path, "rb") as f:
        logo_base64 = base64.b64encode(f.read()).decode()

# --- GLOBAL & GİRİŞ CSS STİLLERİ ---
st.markdown(
    f"""
    <style>
    /* Genel Arka Plan Antrasit */
    .stApp {{
        background-color: #222222 !important;
    }}

    /* Tüm Yazılar ve Etiketler Beyaz */
    h1, h2, h3, h4, h5, h6, 
    .stTextInput label, 
    .stSelectbox label, 
    div[data-testid="stMarkdownContainer"] p {{
        color: #FFFFFF !important;
    }}

    /* Giriş Yap Butonu: Normalde Mavi, Yazısı Beyaz */
    div.stButton > button:first-child {{
        background-color: #007BFF !important;
        color: #FFFFFF !important;
        border: 1px solid #0056b3 !important;
        font-weight: bold;
        transition: background-color 0.1s ease;
    }}

    /* Butona Basıldığında (Active / Hover) Sarı Renk */
    div.stButton > button:first-child:hover,
    div.stButton > button:first-child:active,
    div.stButton > button:first-child:focus {{
        background-color: #FFC107 !important;
        color: #000000 !important;
        border: 1px solid #E0A800 !important;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# --- TANIMLAMALAR ---
USER_FILE = "users.csv"

# Varsayılan kullanıcılar yoksa oluştur
if not os.path.exists(USER_FILE):
    pd.DataFrame({
        "İsim": ["ALİ OSMAN YELBEY", "DENİZ TELLİ GÜRLEYENDAĞ", "MERVE YURTLU", "SELEN AKCAN"],
        "Şifre": ["MARKA123", "MARKA123", "MARKA123", "MARKA123"]
    }).to_csv(USER_FILE, index=False)

# --- GİRİŞ KONTROLÜ ---
if "kullanici" not in st.session_state: 
    st.session_state.kullanici = None

if not st.session_state.kullanici:
    st.markdown("<h1 style='text-align: center; color: #FFFFFF;'>Markanow Patent Satış Takip ERP</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #FFFFFF;'>Lütfen sisteme giriş yapınız.</p>", unsafe_allow_html=True)
    
    # Ortalanmış bir form görünümü için kolonlar
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
