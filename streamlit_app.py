import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="Markanow ERP", layout="wide")

DATA_FILE = "marka_takip.csv"
USER_FILE = "kullanicilar.csv"
ILLER = ["Adana", "Adıyaman", "Afyonkarahisar", "Ağrı", "Aksaray", "Amasya", "Ankara", "Antalya", "Ardahan", "Artvin", "Aydın", "Balıkesir", "Bartın", "Batman", "Bayburt", "Bilecik", "Bingöl", "Bitlis", "Bolu", "Burdur", "Bursa", "Çanakkale", "Çankırı", "Çorum", "Denizli", "Diyarbakır", "Düzce", "Edirne", "Elazığ", "Erzincan", "Erzurum", "Eskişehir", "Gaziantep", "Giresun", "Gümüşhane", "Hakkari", "Hatay", "Iğdır", "Isparta", "İstanbul", "İzmir", "Kahramanmaraş", "Karabük", "Karaman", "Kars", "Kastamonu", "Kayseri", "Kırıkkale", "Kırklareli", "Kırşehir", "Kilis", "Kocaeli", "Konya", "Kütahya", "Malatya", "Manisa", "Mardin", "Mersin", "Muğla", "Muş", "Nevşehir", "Niğde", "Ordu", "Osmaniye", "Rize", "Sakarya", "Samsun", "Siirt", "Sinop", "Sivas", "Şanlıurfa", "Şırnak", "Tekirdağ", "Tokat", "Trabzon", "Tunceli", "Uşak", "Van", "Yalova", "Yozgat", "Zonguldak"]
SINIFLAR = [str(i) for i in range(1, 46)] + [f"35/{i}" for i in range(1, 35)]

def load_data():
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
        df['Satış Tarihi_dt'] = pd.to_datetime(df['Satış Tarihi'], dayfirst=True)
        return df
    return pd.DataFrame(columns=["ID", "Marka Adı", "Ad Soyad", "TC", "Telefon", "Doğum Tarihi", "İl", "Sınıf", "Ödeme", "Satış Tarihi", "Tutar", "Durum", "Danışman", "Fatura No", "Fatura Tarihi"])

# --- GİRİŞ ---
if "kullanici" not in st.session_state: st.session_state.kullanici = None
if not st.session_state.kullanici:
    if not os.path.exists(USER_FILE):
        pd.DataFrame({"İsim": ["ALİ OSMAN YELBEY", "DENİZ TELLİ GÜRLEYENDAĞ", "MERVE YURTLU", "SELEN AKCAN"],
                      "Şifre": ["MARKA123", "MARKA123", "MARKA123", "MARKA123"]}).to_csv(USER_FILE, index=False)
    user_df = pd.read_csv(USER_FILE)
    secili = st.selectbox("Kullanıcı", user_df["İsim"].tolist())
    sifre = st.text_input("Şifre", type="password")
    if st.button("Giriş"):
        if str(sifre).strip() == str(user_df.loc[user_df["İsim"]==secili, "Şifre"].values[0]).strip():
            st.session_state.kullanici = secili
            st.rerun()
    st.stop()

# --- MENÜ ---
st.sidebar.write(f"👤 **{st.session_state.kullanici}**")
if st.sidebar.button("🚪 Çıkış"): st.session_state.kullanici = None; st.rerun()

menu_options = []
if st.session_state.kullanici not in ["ALİ OSMAN YELBEY", "SELEN AKCAN"]:
    menu_options.extend(["📝 Satış Girişi", "📊 Satışlarım"])
menu_options.append("💰 Muhasebe Onayı")
if st.session_state.kullanici in ["ALİ OSMAN YELBEY", "DENİZ TELLİ GÜRLEYENDAĞ"]:
    menu_options.extend(["📊 Performans Raporu", "👥 Personel Yönetimi"])

menu = st.sidebar.radio("Menü", menu_options)
df = load_data()

# --- MODÜLLER ---
if menu == "📝 Satış Girişi":
    with st.form("yeni_satis"):
        m_adi = st.text_input("Marka Adı"); tutar = st.number_input("Tutar")
        sinif = st.multiselect("Sınıf", SINIFLAR)
        if st.form_submit_button("Kaydet"):
            new_row = pd.DataFrame([{"ID": len(df)+1, "Marka Adı": m_adi, "Tutar": tutar, "Sınıf": ",".join(sinif), 
                                     "Durum": "Muhasebe Onayı Bekliyor", "Danışman": st.session_state.kullanici, 
                                     "Satış Tarihi": datetime.now().strftime("%d/%m/%Y")}])
            pd.concat([df, new_row]).to_csv(DATA_FILE, index=False)
            st.success("Satış kaydedildi.")

elif menu == "📊 Satışlarım":
    st.header("📊 Satışlarım ve Fatura İşlemleri")
    my_df = df[df['Danışman'] == st.session_state.kullanici].copy()
    ay = st.selectbox("Ay Seçin", range(1, 13), index=datetime.now().month-1)
    filtered = my_df[my_df['Satış Tarihi_dt'].dt.month == ay]
    
    st.metric("Toplam Ciro (Onaylı)", f"{filtered[filtered['Durum']=='Onaylandı']['Tutar'].sum():,.2f} TL")
    st.dataframe(filtered, use_container_width=True)
    
    st.subheader("Faturalandırılacak Satışlar")
    onaylilar = filtered[filtered['Durum'] == "Onaylandı"]
    st.dataframe(onaylilar[['ID', 'Marka Adı', 'Tutar']])
    id_f = st.number_input("Fatura Kesilecek ID", step=1)
    f_no = st.text_input("Fatura No")
    if st.button("Fatura Kaydet"):
        df.loc[df['ID'] == id_f, ['Fatura No', 'Durum']] = [f_no, "Tamamlandı"]
        df.to_csv(DATA_FILE, index=False); st.rerun()

elif menu == "💰 Muhasebe Onayı":
    if st.session_state.kullanici == "SELEN AKCAN":
        st.header("Onay Bekleyenler")
        bekleyen = df[df['Durum'] == "Muhasebe Onayı Bekliyor"]
        st.dataframe(bekleyen)
        id_onay = st.number_input("Onay ID", step=1)
        if st.button("Onayla"):
            df.loc[df['ID'] == id_onay, 'Durum'] = "Onaylandı"
            df.to_csv(DATA_FILE, index=False); st.rerun()
    else: st.info("Sadece muhasebe yetkilisi onay yapabilir.")

elif menu == "📊 Performans Raporu":
    st.header("Performans")
    rapor = df[df['Durum'] == "Tamamlandı"].groupby('Danışman')['Tutar'].sum()
    st.bar_chart(rapor)

elif menu == "👥 Personel Yönetimi":
    st.header("👥 Personel Yönetimi")
    users_df = pd.read_csv(USER_FILE)
    st.dataframe(users_df, use_container_width=True)
    tab1, tab2, tab3 = st.tabs(["➕ Ekle", "🔑 Şifre Değiştir", "❌ Sil"])
    with tab1:
        yeni_ad = st.text_input("Personel Adı", key="ekle_ad")
        yeni_sifre = st.text_input("Şifre Belirle", type="password", key="ekle_sifre")
        if st.button("Personel Ekle"):
            pd.concat([users_df, pd.DataFrame({"İsim": [yeni_ad], "Şifre": [yeni_sifre]})], ignore_index=True).to_csv(USER_FILE, index=False)
            st.rerun()
    with tab2:
        secilen_p = st.selectbox("Personel Seçin", users_df["İsim"].tolist(), key="guncelle_sec")
        yeni_sifre_g = st.text_input("Yeni Şifre", type="password", key="guncelle_sifre")
        if st.button("Şifreyi Güncelle"):
            users_df.loc[users_df["İsim"] == secilen_p, "Şifre"] = yeni_sifre_g
            users_df.to_csv(USER_FILE, index=False)
            st.success("Şifre güncellendi.")
            st.rerun()
    with tab3:
        silinecek = st.selectbox("Silinecek Personel", users_df["İsim"].tolist(), key="sil_sec")
        if st.button("Personeli Sil"):
            users_df[users_df["İsim"] != silinecek].to_csv(USER_FILE, index=False)
            st.rerun()
