import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Markanow ERP", layout="wide")

# --- TASARIM VE STİL ---
st.markdown("""
    <style>
    .stApp { background-color: #f4f7f9; }
    [data-testid="stSidebar"] { background-color: #ffffff; border-right: 1px solid #e1e4e8; }
    .stButton>button { 
        width: 100%; border-radius: 5px; border: none; 
        background-color: #f8f9fa; color: #34495e; 
        text-align: left; padding: 10px 15px; margin-bottom: 5px;
    }
    .stButton>button:hover { background-color: #e9ecef; }
    .menu-header { color: #7f8c8d; font-size: 0.75rem; text-transform: uppercase; margin: 15px 0 5px 15px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# --- STATE YÖNETİMİ ---
if "mesajlar" not in st.session_state: st.session_state.mesajlar = []
if "kullanici_adi" not in st.session_state: st.session_state.kullanici_adi = "Personel"

# --- MENÜ YAPISI ---
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
        
        st.markdown('<p class="menu-header">İLETİŞİM</p>', unsafe_allow_html=True)
        if st.button("📩 Sistem Mesajları"): st.session_state.menu = "Mesajlar"
        
        st.markdown("---")
        # --- GÜVENLİ ÇIKIŞ ---
        if st.button("🚪 Güvenli Çıkış"):
            st.session_state.giris_yapildi = False
            st.rerun()

# --- UYGULAMA MANTIĞI ---
if "menu" not in st.session_state: st.session_state.menu = "Basvuru_Beklemede"
sidebar_menu()

# --- SAYFA İÇERİKLERİ ---
if st.session_state.menu == "Mesajlar":
    st.title("📩 Sistem İçi Mesajlaşma")
    
    # Mesaj Geçmişi
    for msg in st.session_state.mesajlar:
        with st.chat_message(msg["user"]):
            st.write(msg["text"])
    
    # Mesaj Gönderme
    if prompt := st.chat_input("Mesajınızı buraya yazın..."):
        st.session_state.mesajlar.append({"user": st.session_state.kullanici_adi, "text": prompt})
        st.rerun()

else:
    st.markdown(f"## {st.session_state.menu.replace('_', ' ')}")
    st.info("Bu alanda süreçteki tüm kayıtlarınız güncel olarak listelenir.")
