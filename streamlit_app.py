import streamlit as st
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta

st.set_page_config(page_title="Markanow Operasyon", layout="wide")

# --- OTOMASYON HESAPLAMA ---
def add_months(date_str, months):
    try:
        dt = datetime.strptime(date_str, "%d.%m.%Y")
        return (dt + relativedelta(months=months)).strftime("%d.%m.%Y")
    except: return "-"

if "markalar" not in st.session_state:
    st.session_state.markalar = pd.DataFrame(columns=[
        "Marka Adı", "Bülten Tarihi", "İlan Bitiş", "İtiraz Tebliğ", "İtiraz Son Gün", 
        "Tescil Bildirim", "Tescil Son Gün"
    ])

# --- SOL MENÜ VE HATIRLATMALAR ---
def sidebar_menu():
    st.sidebar.title("📌 İşlem Menüsü")
    if st.sidebar.button("⚙️ Operasyon Paneli"): st.session_state.menu = "Operasyon"
    if st.sidebar.button("📅 Bugünün Hatırlatmaları"): st.session_state.menu = "Hatırlatma"
    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 Güvenli Çıkış"): 
        st.session_state.giris_yapildi = False
        st.rerun()

# --- ANA EKRAN HATIRLATMALARI ---
def gunun_hatirlatmalari():
    st.subheader(f"🔔 Bugün: {datetime.now().strftime('%d.%m.%Y')}")
    today = datetime.now().strftime("%d.%m.%Y")
    
    col1, col2 = st.columns(2)
    with col1:
        st.info("📌 Bugünün Son Günleri")
        hatirlatmalar = st.session_state.markalar[
            (st.session_state.markalar["İlan Bitiş"] == today) | 
            (st.session_state.markalar["İtiraz Son Gün"] == today) | 
            (st.session_state.markalar["Tescil Son Gün"] == today)
        ]
        st.dataframe(hatirlatmalar)

# --- UYGULAMA MANTIĞI ---
if "menu" not in st.session_state: st.session_state.menu = "Hatırlatma"

sidebar_menu()

if st.session_state.menu == "Hatırlatma":
    gunun_hatirlatmalari()

elif st.session_state.menu == "Operasyon":
    st.subheader("⚙️ Operasyon ve Takip Otomasyonu")
    if not st.session_state.markalar.empty:
        m_adi = st.selectbox("Marka Seçin", st.session_state.markalar["Marka Adı"].unique())
        idx = st.session_state.markalar[st.session_state.markalar["Marka Adı"] == m_adi].index[0]
        with st.form("oto_takip"):
            bulten = st.date_input("Bülten Tarihi")
            itiraz = st.date_input("İtiraz Tebliğ Tarihi")
            tescil = st.date_input("Tescil Bildirim Tarihi")
            if st.form_submit_button("Hesapla ve Güncelle"):
                b_str = bulten.strftime("%d.%m.%Y")
                st.session_state.markalar.at[idx, "Bülten Tarihi"] = b_str
                st.session_state.markalar.at[idx, "İlan Bitiş"] = add_months(b_str, 2)
                st.session_state.markalar.at[idx, "İtiraz Son Gün"] = add_months(itiraz.strftime("%d.%m.%Y"), 1)
                st.session_state.markalar.at[idx, "Tescil Son Gün"] = add_months(tescil.strftime("%d.%m.%Y"), 2)
                st.success("Tarihler güncellendi!")
    st.dataframe(st.session_state.markalar)
