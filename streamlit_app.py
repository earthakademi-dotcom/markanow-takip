import streamlit as st
import pandas as pd

# STREAMING_CHUNK: Kurumsal Görünüm İçin Tasarım Ayarları
st.set_page_config(page_title="Markanow ERP", layout="wide")

st.markdown("""
    <style>
    /* Kurumsal Renkler ve Font */
    .stApp { background-color: #f4f7f9; }
    h1, h2, h3 { color: #2c3e50; font-family: 'Segoe UI', sans-serif; }
    
    /* Yan Menü Tasarımı */
    [data-testid="stSidebar"] { 
        background-color: #ffffff; 
        border-right: 1px solid #e1e4e8;
    }
    
    /* Buton Tasarımları */
    .stButton>button { 
        width: 100%; 
        border-radius: 5px; 
        border: none; 
        background-color: #f8f9fa; 
        color: #34495e; 
        text-align: left; 
        padding: 10px 15px;
        transition: all 0.3s;
    }
    .stButton>button:hover { background-color: #e9ecef; color: #2c3e50; }
    
    /* Başlık Grupları */
    .menu-header { color: #7f8c8d; font-size: 0.8rem; text-transform: uppercase; margin-top: 20px; padding-left: 15px; }
    </style>
""", unsafe_allow_html=True)

# STREAMING_CHUNK: Menü Yapısı
def sidebar_menu():
    with st.sidebar:
        st.markdown("### 🏢 MARKANOW ERP")
        st.markdown("---")
        
        st.markdown('<p class="menu-header">BAŞVURU SÜRECİ</p>', unsafe_allow_html=True)
        if st.button("⏳ Başvuru Beklemede"): st.session_state.menu = "Basvuru_Beklemede"
        if st.button("📋 Bülten Beklemede"): st.session_state.menu = "Bulten_Beklemede"
        
        st.markdown('<p class="menu-header">SÜREÇ TAKİP</p>', unsafe_allow_html=True)
        if st.button("📢 Bültende (Yayında)"): st.session_state.menu = "Bultende"
        if st.button("⚖️ İtiraz Beklemede"): st.session_state.menu = "Itiraz"
        if st.button("📄 Tescil Tebliğ Beklemede"): st.session_state.menu = "Tescil"
        if st.button("💰 Tescil Kurum Ödeme"): st.session_state.menu = "Odeme"
        if st.button("❌ Red Edilenler"): st.session_state.menu = "Red"

# STREAMING_CHUNK: Mantık ve İçerik Yönetimi
if "menu" not in st.session_state: st.session_state.menu = "Basvuru_Beklemede"
sidebar_menu()

# Kurumsal Başlık Yapısı
st.markdown(f"## {st.session_state.menu.replace('_', ' ')}")
st.markdown("---")

# Örnek Operasyon Paneli Alanı
with st.expander("🛠 Operasyon Paneli (Veri Güncelleme)", expanded=False):
    st.write("Marka bilgilerini ve süreç aşamalarını buradan güncelleyebilirsiniz.")

# Tablo Görünümü
st.info("Bu alanda süreçteki tüm kayıtlarınız güncel olarak listelenir.")
st.dataframe(pd.DataFrame(), use_container_width=True)
