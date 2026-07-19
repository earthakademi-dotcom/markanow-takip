import streamlit as st
import pandas as pd
import os
import json
from datetime import datetime

# --- SAYFA YAPILANDIRMASI ---
st.set_page_config(page_title="Markanow ERP", layout="wide")

# --- TANIMLAMALAR ---
DATA_FILE = "marka_takip.csv"
USER_FILE = "kullanicilar.csv"
PRIM_FILE = "prim_tablosu.json"
ILLER = ["Adana", "Adıyaman", "Afyonkarahisar", "Ağrı", "Aksaray", "Amasya", "Ankara", "Antalya", "Ardahan", "Artvin", "Aydın", "Balıkesir", "Bartın", "Batman", "Bayburt", "Bilecik", "Bingöl", "Bitlis", "Bolu", "Burdur", "Bursa", "Çanakkale", "Çankırı", "Çorum", "Denizli", "Diyarbakır", "Düzce", "Edirne", "Elazığ", "Erzincan", "Erzurum", "Eskişehir", "Gaziantep", "Giresun", "Gümüşhane", "Hakkari", "Hatay", "Iğdır", "Isparta", "İstanbul", "İzmir", "Kahramanmaraş", "Karabük", "Karaman", "Kars", "Kastamonu", "Kayseri", "Kırıkkale", "Kırklareli", "Kırşehir", "Kilis", "Kocaeli", "Konya", "Kütahya", "Malatya", "Manisa", "Mardin", "Mersin", "Muğla", "Muş", "Nevşehir", "Niğde", "Ordu", "Osmaniye", "Rize", "Sakarya", "Samsun", "Siirt", "Sinop", "Sivas", "Şanlıurfa", "Şırnak", "Tekirdağ", "Tokat", "Trabzon", "Tunceli", "Uşak", "Van", "Yalova", "Yozgat", "Zonguldak"]
SINIFLAR = [str(i) for i in range(1, 46)] + [f"35/{i}" for i in range(1, 35)]

def load_data():
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
        return df
    return pd.DataFrame(columns=["ID", "Marka Adı", "Ad Soyad", "TC", "Telefon", "Doğum Tarihi", "İl", "Sınıf", "Ödeme", "Satış Tarihi", "Tutar", "Durum", "Danışman", "Fatura No"])

# --- GİRİŞ ---
if "kullanici" not in st.session_state: st.session_state.kullanici = None
if not st.session_state.kullanici:
    st.markdown("<h1 style='text-align: center; color: #1f77b4;'>Markanow Patent Satış Takip ERP</h1>", unsafe_allow_html=True)
    if not os.path.exists(USER_FILE):
        pd.DataFrame({"İsim": ["ALİ OSMAN YELBEY", "DENİZ TELLİ GÜRLEYENDAĞ", "MERVE YURTLU", "SELEN AKCAN"],
                      "Şifre": ["MARKA123", "MARKA123", "MARKA123", "MARKA123"]}).to_csv(USER_FILE, index=False)
    user_df = pd.read_csv(USER_FILE)
    secili = st.selectbox("Kullanıcı Seçiniz", user_df["İsim"].tolist())
    sifre = st.text_input("Şifre", type="password")
    if st.button("Giriş Yap", use_container_width=True):
        user_row = user_df[user_df["İsim"] == secili]
        if str(sifre).strip() == str(user_row.iloc[0]["Şifre"]).strip():
            st.session_state.kullanici = secili
            st.rerun()
    st.stop()

# --- MENÜ ---
st.sidebar.write(f"👤 Aktif: **{st.session_state.kullanici}**")
if st.sidebar.button("🚪 Güvenli Çıkış", use_container_width=True):
    st.session_state.kullanici = None; st.rerun()
st.sidebar.write("---")

menu_options = ["📝 Satış Girişi", "📊 Satışlarım"]
if st.session_state.kullanici in ["SELEN AKCAN", "ALİ OSMAN YELBEY", "DENİZ TELLİ GÜRLEYENDAĞ"]:
    menu_options.extend(["💰 Muhasebe Onayı"])
if st.session_state.kullanici in ["ALİ OSMAN YELBEY", "DENİZ TELLİ GÜRLEYENDAĞ"]:
    menu_options.extend(["📊 Performans Raporu", "👥 Personel Yönetimi"])

menu = st.sidebar.radio("Menü", menu_options)
df = load_data()

# --- MODÜLLER ---
if menu == "📝 Satış Girişi":
    st.header("📝 Yeni Satış Girişi")
    with st.form("yeni_satis", clear_on_submit=True):
        c1, c2 = st.columns(2)
        m_adi = c1.text_input("Marka Adı"); ad_soyad = c1.text_input("İsim Soyisim")
        tc = c1.text_input("TC (11 Hane)"); tel = c1.text_input("Telefon")
        st.write("Doğum Tarihi")
        d1, d2, d3 = st.columns(3)
        gun = d1.selectbox("Gün", range(1, 32))
        ay = d2.selectbox("Ay", range(1, 13))
        yil = d3.selectbox("Yıl", range(datetime.now().year, 1919, -1))
        il = c2.selectbox("İl", ILLER)
        sinif = c2.multiselect("Sınıf Seçimi", SINIFLAR); odeme = c2.selectbox("Ödeme", ["EFT", "Kredi Kartı"])
        s_tarihi = c2.date_input("Satış Tarihi"); tutar = c2.number_input("Tutar (TL)", min_value=0.0)
        if st.form_submit_button("Satışı Kaydet"):
            dogum_str = f"{gun:02d}/{ay:02d}/{yil}"
            new_row = {"ID": len(df)+1 if df.empty else df['ID'].max()+1, "Marka Adı": m_adi, "Ad Soyad": ad_soyad, "TC": tc, "Telefon": tel, 
                       "Doğum Tarihi": dogum_str, "İl": il, "Sınıf": ",".join(sinif), "Ödeme": odeme, 
                       "Satış Tarihi": s_tarihi.strftime("%d/%m/%Y"), "Tutar": tutar, 
                       "Durum": "Muhasebe Onayı Bekliyor", "Danışman": st.session_state.kullanici, "Fatura No": ""}
            pd.concat([df, pd.DataFrame([new_row])], ignore_index=True).to_csv(DATA_FILE, index=False)
            st.success("Satış kaydedildi.")

elif menu == "📊 Satışlarım":
    st.header(f"📊 {st.session_state.kullanici} - Satışlarım")
    my_df = df[df['Danışman'] == st.session_state.kullanici].copy()
    with st.expander("✏️ Kendi Satışımı Düzenle"):
        duzenle_id = st.number_input("Düzenlemek istediğiniz Satış ID", step=1)
        if duzenle_id in my_df['ID'].values:
            row = df[df['ID'] == duzenle_id].iloc[0]
            with st.form("kendi_satis_duzenle"):
                y_marka = st.text_input("Marka Adı", value=row['Marka Adı'])
                y_tutar = st.number_input("Tutar (TL)", value=float(row['Tutar']))
                if st.form_submit_button("Güncelle"):
                    df.loc[df['ID'] == duzenle_id, ['Marka Adı', 'Tutar']] = [y_marka, y_tutar]
                    df.to_csv(DATA_FILE, index=False); st.success("Satış güncellendi!"); st.rerun()
    st.dataframe(my_df, use_container_width=True)

elif menu == "💰 Muhasebe Onayı":
    st.header("💰 Muhasebe Onay ve Düzenleme Paneli")
    with st.expander("✏️ Yanlış Girilen Satışı Düzenle"):
        secili_id = st.number_input("Düzenlenecek Satış ID", step=1)
        if secili_id in df['ID'].values:
            row = df[df['ID'] == secili_id].iloc[0]
            with st.form("duzenleme_formu"):
                c1, c2 = st.columns(2)
                y_marka = c1.text_input("Marka Adı", value=row['Marka Adı'])
                y_tutar = c2.number_input("Tutar (TL)", value=float(row['Tutar']))
                y_durum = c1.selectbox("Durum", ["Muhasebe Onayı Bekliyor", "Onaylandı", "Tamamlandı"], index=["Muhasebe Onayı Bekliyor", "Onaylandı", "Tamamlandı"].index(row['Durum']))
                y_fatura = c2.text_input("Fatura No", value=str(row['Fatura No']) if pd.notna(row['Fatura No']) else "")
                if st.form_submit_button("Güncelle"):
                    df.loc[df['ID'] == secili_id, ['Marka Adı', 'Tutar', 'Durum', 'Fatura No']] = [y_marka, y_tutar, y_durum, y_fatura]
                    df.to_csv(DATA_FILE, index=False); st.success("Satış güncellendi!"); st.rerun()
    bekleyen = df[df['Durum'] == "Muhasebe Onayı Bekliyor"]
    for i, row in bekleyen.iterrows():
        if st.button(f"✅ Onayla: {row['Marka Adı']} ({row['Tutar']} TL)", key=f"onay_{row['ID']}"):
            df.loc[df['ID'] == row['ID'], 'Durum'] = "Onaylandı"
            df.to_csv(DATA_FILE, index=False); st.rerun()

elif menu == "📊 Performans Raporu":
    st.header("📊 Performans"); st.bar_chart(df[df['Durum'] == "Tamamlandı"].groupby('Danışman')['Tutar'].sum())

elif menu == "👥 Personel Yönetimi":
    st.header("👥 Personel ve Veri Yönetimi")
    if st.button("⚠️ TÜM VERİLERİ SİL"):
        if os.path.exists(DATA_FILE): os.remove(DATA_FILE); st.error("Veriler silindi!"); st.rerun()
    st.dataframe(pd.read_csv(USER_FILE), use_container_width=True)
