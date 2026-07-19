import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

st.set_page_config(page_title="Markanow ERP & Satış Takip", layout="wide")

# Yardımcı: Tarih ekleme
def add_months(date_str, months):
    try:
        dt = datetime.strptime(date_str, "%d.%m.%Y")
        return (dt + relativedelta(months=months)).strftime("%d.%m.%Y")
    except: return "-"

# --- VERİ HAZIRLIĞI ---
if "markalar" not in st.session_state:
    st.session_state.markalar = pd.DataFrame(columns=[
        "Marka Adı", "Bülten Tarihi", "İlan Bitiş", "İtiraz Tebliğ", "İtiraz Son Gün", 
        "Tescil Bildirim", "Tescil Son Gün", "B. Onay"
    ])

# --- OPERASYON PANELİ VE OTOMASYON ---
st.subheader("⚙️ Operasyon ve Takip Otomasyonu")

if not st.session_state.markalar.empty:
    m_adi = st.selectbox("Marka Seçin", st.session_state.markalar["Marka Adı"].unique())
    idx = st.session_state.markalar[st.session_state.markalar["Marka Adı"] == m_adi].index[0]
    
    with st.form("oto_takip"):
        bulten = st.date_input("Bülten Tarihi")
        itiraz_teblig = st.date_input("İtiraz Tebliğ Tarihi (Varsa)")
        tescil_bildirim = st.date_input("Tescil Bildirim Tarihi (Varsa)")
        
        if st.form_submit_button("Güncelle ve Hesapla"):
            b_str = bulten.strftime("%d.%m.%Y")
            st.session_state.markalar.at[idx, "Bülten Tarihi"] = b_str
            st.session_state.markalar.at[idx, "İlan Bitiş"] = add_months(b_str, 2)
            
            if itiraz_teblig:
                it_str = itiraz_teblig.strftime("%d.%m.%Y")
                st.session_state.markalar.at[idx, "İtiraz Tebliğ"] = it_str
                st.session_state.markalar.at[idx, "İtiraz Son Gün"] = add_months(it_str, 1)
                
            if tescil_bildirim:
                t_str = tescil_bildirim.strftime("%d.%m.%Y")
                st.session_state.markalar.at[idx, "Tescil Bildirim"] = t_str
                st.session_state.markalar.at[idx, "Tescil Son Gün"] = add_months(t_str, 2)
            
            st.success("Tarihler otomatik hesaplandı!")

# --- TAKİP RAPORLARI ---
st.subheader("📊 Otomatik Takip Raporları")
tab1, tab2, tab3 = st.tabs(["İlan Bitişi Gelenler", "İtiraz Süreci", "Tescil Ödemeleri"])

with tab1:
    st.dataframe(st.session_state.markalar[["Marka Adı", "Bülten Tarihi", "İlan Bitiş"]])
with tab2:
    st.dataframe(st.session_state.markalar[["Marka Adı", "İtiraz Tebliğ", "İtiraz Son Gün"]])
with tab3:
    st.dataframe(st.session_state.markalar[["Marka Adı", "Tescil Bildirim", "Tescil Son Gün"]])
