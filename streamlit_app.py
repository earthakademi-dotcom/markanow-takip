import streamlit as st
import pandas as pd
from datetime import datetime

# --- STREAMING_CHUNK: Configuring users and authorization credentials... ---
# Kullanıcı adı, şifre ve rol tanımlamaları
KULLANICILAR = {
    "Ali Osman Yelbey": {"sifre": "MarkanowAdmin2026!", "rol": "Admin"},
    "Buğra Büyükeren": {"sifre": "BugraVekil456!", "rol": "Admin"},
    "MERVE YURTLU": {"sifre": "MerveDanisman789!", "rol": "Marka Danışmanı"},
    "Ahmet Yılmaz": {"sifre": "AhmetDanisman321!", "rol": "Marka Danışmanı"},
    "Muhasebe Kullanıcısı": {"sifre": "Muhasebe987!", "rol": "Muhasebe"}
}

st.set_page_config(page_title="Markanow ERP & Satış Takip", layout="wide")

# --- STREAMING_CHUNK: Checking session state and login credentials... ---
# Oturum Hafızası Başlatma
if "giris_yapildi" not in st.session_state:
    st.session_state.giris_yapildi = False
    st.session_state.kullanici_adi = ""
    st.session_state.kullanici_rolu = ""

# --- STREAMING_CHUNK: Initializing database table structure with class code... ---
# Temel Veri Tabanı Yapısı (Sınıf Kodu eklenmiş hali)
if "markalar" not in st.session_state:
    st.session_state.markalar = pd.DataFrame(columns=[
        "Marka Adı", "Sınıf Kodu", "Personel", "Adı Soyadı", "Telefon No", "Satış Tarihi",
        "Ödeme Seçeneği", "Başvuru Ücreti", "B. Onay Durumu", "Savunma Ücreti", "S. Onay Durumu",
        "Tescil Ücreti", "T. Onay Durumu", "Toplam Onaylı Ciro", "Başvuru No",
        "Başvuru Tarihi", "Bülten Tarihi", "İlan Bitiş Tarihi", "İtiraz Tebliğ T.",
        "Savunma Son Gün", "Kurul Kararı / Durum", "Belge Son Ödeme T.", "Yenileme (Vize) T."
    ])

# Geçmiş verilerde Sınıf Kodu kolonu yoksa otomatik olarak ekle ve hata oluşmasını engelle
if "Sınıf Kodu" not in st.session_state.markalar.columns:
    st.session_state.markalar.insert(1, "Sınıf Kodu", "-")

# --- STREAMING_CHUNK: Initializing dynamic columns for payment options... ---
if "Ödeme Seçeneği" not in st.session_state.markalar.columns:
    st.session_state.markalar.insert(6, "Ödeme Seçeneği", "-")

if "danismanlar" not in st.session_state:
    st.session_state.danismanlar = ["MERVE YURTLU", "Ahmet Yılmaz", "Buğra Büyükeren"]

# --- STREAMING_CHUNK: Displaying the logo and login interface... ---
def logo_goster():
    st.markdown(
        """
        <div style="display: flex; align-items: center; gap: 15px; margin-bottom: 25px;">
            <div style="background-color: #1e3a8a; color: white; width: 50px; height: 50px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 28px; font-weight: bold; font-family: sans-serif;">
                M
            </div>
            <div>
                <h1 style="margin: 0; font-family: sans-serif; font-weight: bold; color: #1e293b; letter-spacing: -1px; font-size: 32px;">
                    markanow <span style="font-size: 18px; color: #2563eb; font-weight: 600;">ERP & Takip</span>
                </h1>
            </div>
        </div>
        """, 
        unsafe_allow_html=True
    )

# 1. GİRİŞ EKRANI KONTROLÜ
if not st.session_state.giris_yapildi:
    st.title("🔒 Markanow Takip Sistemi - Kullanıcı Girişi")
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        logo_goster()
        st.write("Devam etmek için lütfen kullanıcı adınızı seçin ve şifrenizi girin.")
        
        secilen_kullanici = st.selectbox("Kullanıcı Adınızı Seçin", list(KULLANICILAR.keys()))
        girilen_sifre = st.text_input("Şifrenizi Girin", type="password")
        
        if st.button("Sisteme Giriş Yap", use_container_width=True):
            if girilen_sifre == KULLANICILAR[secilen_kullanici]["sifre"]:
                st.session_state.giris_yapildi = True
                st.session_state.kullanici_adi = secilen_kullanici
                st.session_state.kullanici_rolu = KULLANICILAR[secilen_kullanici]["rol"]
                st.success(f"Başarıyla giriş yapıldı. Hoş geldiniz, {secilen_kullanici}!")
                st.rerun()
            else:
                st.error("Hatalı şifre girdiniz! Lütfen tekrar deneyin.")
    st.stop()

# --- STREAMING_CHUNK: Setting up sidebar and user controls... ---
# 2. SOL PANEL VE GÜVENLİK BİLGİLERİ
st.sidebar.title("🔑 Kullanıcı Giriş Paneli")
st.sidebar.success(f"👤 Aktif Kullanıcı:\n{st.session_state.kullanici_adi}")
st.sidebar.info(f"🛡️ Rolünüz: {st.session_state.kullanici_rolu}")

if st.sidebar.button("Güvenli Çıkış Yap", use_container_width=True):
    st.session_state.giris_yapildi = False
    st.session_state.kullanici_adi = ""
    st.session_state.kullanici_rolu = ""
    st.rerun()

st.sidebar.markdown("---")

logo_goster()
st.subheader("🛡️ Marka Tescil, Finans ve Personel Takip Sistemi")
st.write(f"Sistem şu anda **{st.session_state.kullanici_rolu}** yetkileriyle aktif olarak çalışıyor.")
st.markdown("---")

# --- STREAMING_CHUNK: Rendering the consultant sales entry form with brand name, class code and price... ---
# 4. ROL BAZLI PANEL YETKİLENDİRMELERİ

# A) MARKA DANIŞMANI PANELİ
if st.session_state.kullanici_rolu == "Marka Danışmanı":
    st.subheader("📝 Yeni Marka Satış Giriş Formu")
    
    with st.form("danisman_satis_formu", clear_on_submit=True):
        col_form1, col_form2 = st.columns(2)
        
        with col_form1:
            marka_adi = st.text_input("Marka Adı *")
            
            # 1'den 45'e kadar sınıf kodlarının çoklu seçim (multiselect) kutusu
            sinif_listesi = [f"Sınıf {i}" for i in range(1, 46)]
            secilen_siniflar = st.multiselect(
                "Sınıf Kodu / Kodları (Birden fazla seçilebilir) *", 
                options=sinif_listesi,
                placeholder="Sınıf seçiniz..."
            )
            
            basvuru_ucreti = st.number_input("Satış / Başvuru Ücreti (TL) *", min_value=0, value=0, step=100)
            
            # --- STREAMING_CHUNK: Integrating payment option dropdown... ---
            odeme_secenegi = st.selectbox("Ödeme Seçeneği *", ["EFT / Havale", "Kredi Kartı"])
            
        with col_form2:
            musteri_ad_soyad = st.text_input("Müşteri Adı Soyadı")
            musteri_tel = st.text_input("Müşteri Telefon No")
            satis_tarihi = st.date_input("Satış Tarihi (Sisteme Giriş)", datetime.today())
        
        submit = st.form_submit_button("Satışı Sisteme Kaydet", use_container_width=True)
        
        if submit:
            if not marka_adi:
                st.error("Lütfen 'Marka Adı' alanını boş bırakmayınız!")
            elif not secilen_siniflar:
                st.error("Lütfen en az bir adet 'Sınıf Kodu' seçimi yapınız!")
            elif basvuru_ucreti <= 0:
                st.error("Lütfen geçerli bir 'Satış / Başvuru Ücreti' giriniz!")
            else:
                # Seçilen sınıfları temiz metin haline getir (Örnek: "Sınıf 35, Sınıf 41")
                sinif_metni = ", ".join([s.replace("Sınıf ", "") for s in secilen_siniflar])
                
                yeni_veri = {
                    "Marka Adı": marka_adi,
                    "Sınıf Kodu": sinif_metni,
                    "Personel": st.session_state.kullanici_adi,
                    "Adı Soyadı": musteri_ad_soyad,
                    "Telefon No": musteri_tel,
                    "Satış Tarihi": satis_tarihi.strftime("%d.%m.%Y"),
                    "Ödeme Seçeneği": odeme_secenegi,
                    "Başvuru Ücreti": basvuru_ucreti,
                    "B. Onay Durumu": "Bekliyor", # Ücret doğrudan girildiği için onay bekliyor durumuna geçer
                    "Savunma Ücreti": 0, "S. Onay Durumu": "-",
                    "Tescil Ücreti": 0, "T. Onay Durumu": "-",
                    "Toplam Onaylı Ciro": 0, "Başvuru No": "-",
                    "Başvuru Tarihi": "-", "Bülten Tarihi": "-", "İlan Bitiş Tarihi": "-",
                    "İtiraz Tebliğ T.": "-", "Savunma Son Gün": "-", "Kurul Kararı / Durum": "-",
                    "Belge Son Ödeme T.": "-", "Yenileme (Vize) T.": "-"
                }
                st.session_state.markalar = pd.concat([st.session_state.markalar, pd.DataFrame([yeni_veri])], ignore_index=True)
                st.success(f"'{marka_adi}' markası ({sinif_metni}. Sınıflar) {basvuru_ucreti} TL bedel ve {odeme_secenegi} ödeme seçeneği ile başarıyla kaydedildi! Muhasebe onayı bekleniyor.")

# B) ADMIN YÖNETİM VE SÜREÇ İLERLEME PANELİ
elif st.session_state.kullanici_rolu == "Admin":
    st.subheader("⚙️ Admin Yönetim ve Süreç İlerleme Paneli")
    
    with st.expander("👥 Danışman Ekle / Çıkar"):
        yeni_danisman = st.text_input("Yeni Danışman Adı")
        if st.button("Danışman Ekle") and yeni_danisman:
            if yeni_danisman not in st.session_state.danismanlar:
                st.session_state.danismanlar.append(yeni_danisman)
                st.success(f"{yeni_danisman} listeye eklendi.")
    
    if not st.session_state.markalar.empty:
        marka_listesi = st.session_state.markalar["Marka Adı"].tolist()
        secilen_marka = st.selectbox("Süreç Güncellenecek Markayı Seçin", marka_listesi)
        idx = st.session_state.markalar[st.session_state.markalar["Marka Adı"] == secilen_marka].index[0]
        
        st.markdown(f"### 📑 {secilen_marka} - Güncelleme Ekranı")
        
        c1, c2, c3 = st.columns(3)
        with c1:
            b_ucreti = st.number_input("Başvuru Ücreti (TL)", value=int(st.session_state.markalar.at[idx, "Başvuru Ücreti"]))
            b_no = st.text_input("Başvuru No", value=str(st.session_state.markalar.at[idx, "Başvuru No"]))
            b_tarih = st.text_input("Başvuru Tarihi (GG.AA.YYYY)", value=str(st.session_state.markalar.at[idx, "Başvuru Tarihi"]))
            s_kodu = st.text_input("Sınıf Kodu", value=str(st.session_state.markalar.at[idx, "Sınıf Kodu"]))
        with c2:
            s_ucreti = st.number_input("Savunma Ücreti (TL)", value=int(st.session_state.markalar.at[idx, "Savunma Ücreti"]))
            bulten_t = st.text_input("Bülten Tarihi (GG.AA.YYYY)", value=str(st.session_state.markalar.at[idx, "Bülten Tarihi"]))
            itiraz_t = st.text_input("İtiraz Tebliğ Tarihi (GG.AA.YYYY)", value=str(st.session_state.markalar.at[idx, "İtiraz Tebliğ T."]))
            
            # --- STREAMING_CHUNK: Displaying and updating admin payment option... ---
            odeme_secenekleri = ["EFT / Havale", "Kredi Kartı"]
            mevcut_secenek = str(st.session_state.markalar.at[idx, "Ödeme Seçeneği"]) if "Ödeme Seçeneği" in st.session_state.markalar.columns else "EFT / Havale"
            try:
                def_idx = odeme_secenekleri.index(mevcut_secenek)
            except ValueError:
                def_idx = 0
            admin_odeme_secenegi = st.selectbox("Ödeme Seçeneği", odeme_secenekleri, index=def_idx)
        with c3:
            t_ucreti = st.number_input("Tescil Ücreti (TL)", value=int(st.session_state.markalar.at[idx, "Tescil Ücreti"]))
            kurul_karar = st.text_input("Kurul Kararı / Durum", value=str(st.session_state.markalar.at[idx, "Kurul Kararı / Durum"]))
            vize_t = st.text_input("Yenileme (Vize) T. (GG.AA.YYYY)", value=str(st.session_state.markalar.at[idx, "Yenileme (Vize) T."]))
            
        if st.button("Verileri Güncelle / Kaydet", type="primary"):
            st.session_state.markalar.at[idx, "Başvuru Ücreti"] = b_ucreti
            st.session_state.markalar.at[idx, "Başvuru No"] = b_no
            st.session_state.markalar.at[idx, "Başvuru Tarihi"] = b_tarih
            st.session_state.markalar.at[idx, "Sınıf Kodu"] = s_kodu
            st.session_state.markalar.at[idx, "Savunma Ücreti"] = s_ucreti
            st.session_state.markalar.at[idx, "Bülten Tarihi"] = bulten_t
            st.session_state.markalar.at[idx, "İtiraz Tebliğ T."] = itiraz_t
            st.session_state.markalar.at[idx, "Ödeme Seçeneği"] = admin_odeme_secenegi
            st.session_state.markalar.at[idx, "Tescil Ücreti"] = t_ucreti
            st.session_state.markalar.at[idx, "Kurul Kararı / Durum"] = kurul_karar
            st.session_state.markalar.at[idx, "Yenileme (Vize) T."] = vize_t
            
            # Dinamik muhasebe onay tetikleyicileri
            if b_ucreti > 0 and st.session_state.markalar.at[idx, "B. Onay Durumu"] == "-":
                st.session_state.markalar.at[idx, "B. Onay Durumu"] = "Bekliyor"
            if s_ucreti > 0 and st.session_state.markalar.at[idx, "S. Onay Durumu"] == "-":
                st.session_state.markalar.at[idx, "S. Onay Durumu"] = "Bekliyor"
            if t_ucreti > 0 and st.session_state.markalar.at[idx, "T. Onay Durumu"] == "-":
                st.session_state.markalar.at[idx, "T. Onay Durumu"] = "Bekliyor"
                
            st.success("Süreç ve finansal tanımlamalar başarıyla güncellendi!")
            st.rerun()
    else:
        st.info("Sistemde henüz süreç güncellemesi yapılacak bir marka bulunmuyor.")

# C) MUHASEBE PANELİ
elif st.session_state.kullanici_rolu == "Muhasebe":
    st.subheader("💰 Muhasebe Finansal Onay Paneli")
    
    if not st.session_state.markalar.empty:
        bekleyenler = st.session_state.markalar[
            (st.session_state.markalar["B. Onay Durumu"] == "Bekliyor") | 
            (st.session_state.markalar["S. Onay Durumu"] == "Bekliyor") | 
            (st.session_state.markalar["T. Onay Durumu"] == "Bekliyor")
        ]
        
        if not bekleyenler.empty:
            secilen_m_m = st.selectbox("Ödemesi Kontrol Edilecek Marka", bekleyenler["Marka Adı"].tolist())
            m_idx = st.session_state.markalar[st.session_state.markalar["Marka Adı"] == secilen_m_m].index[0]
            
            # --- STREAMING_CHUNK: Displaying payment option to accountant... ---
            mevcut_yontem = st.session_state.markalar.at[m_idx, "Ödeme Seçeneği"] if "Ödeme Seçeneği" in st.session_state.markalar.columns else "Belirtilmemiş"
            st.info(f"💳 Müşterinin Tercih Ettiği Ödeme Yöntemi: **{mevcut_yontem}**")
            
            # Ödeme Onaylama Butonları
            if st.session_state.markalar.at[m_idx, "B. Onay Durumu"] == "Bekliyor":
                st.warning(f"Başvuru Ücreti: {st.session_state.markalar.at[m_idx, 'Başvuru Ücreti']} TL | Durum: Bekliyor")
                if st.button("Başvuru Ödemesini Onayla"):
                    st.session_state.markalar.at[m_idx, "B. Onay Durumu"] = "ONAYLANDI"
                    st.success("Başvuru ödemesi onaylandı!")
                    st.rerun()
                    
            if st.session_state.markalar.at[m_idx, "S. Onay Durumu"] == "Bekliyor":
                st.warning(f"Savunma Ücreti: {st.session_state.markalar.at[m_idx, 'Savunma Ücreti']} TL | Durum: Bekliyor")
                if st.button("Savunma Ödemesini Onayla"):
                    st.session_state.markalar.at[m_idx, "S. Onay Durumu"] = "ONAYLANDI"
                    st.success("Savunma ödemesi onaylandı!")
                    st.rerun()
                    
            if st.session_state.markalar.at[m_idx, "T. Onay Durumu"] == "Bekliyor":
                st.warning(f"Tescil Ücreti: {st.session_state.markalar.at[m_idx, 'Tescil Ücreti']} TL | Durum: Bekliyor")
                if st.button("Tescil Belge Ödemesini Onayla"):
                    st.session_state.markalar.at[m_idx, "T. Onay Durumu"] = "ONAYLANDI"
                    st.success("Tescil belgesi ödemesi onaylandı!")
                    st.rerun()
        else:
            st.info("Onay bekleyen herhangi bir yeni ödeme bulunmuyor.")
    else:
        st.info("Sisteme henüz hiçbir marka girilmemiş.")

st.markdown("---")

# --- STREAMING_CHUNK: Processing live records table and calculating turnover... ---
# 5. ORTAK CANLI RAPORLAMA VE CİRO TABLOLARI
st.subheader("📊 Canlı Rapor Tablosu (Excel / Google E-Tablolar Uyumlu)")

# Canlı Ciro Hesaplama Mantığı
for i, row in st.session_state.markalar.iterrows():
    toplam = 0
    if row["B. Onay Durumu"] == "ONAYLANDI": toplam += int(row["Başvuru Ücreti"])
    if row["S. Onay Durumu"] == "ONAYLANDI": toplam += int(row["Savunma Ücreti"])
    if row["T. Onay Durumu"] == "ONAYLANDI": toplam += int(row["Tescil Ücreti"])
    st.session_state.markalar.at[i, "Toplam Onaylı Ciro"] = toplam

st.dataframe(st.session_state.markalar)

def convert_df(df):
    return df.to_csv(index=False).encode('utf-8')
csv_data = convert_df(st.session_state.markalar)
st.download_button("📥 Tabloyu Excel (CSV) Olarak İndir", csv_data, "marka_takip_raporu.csv", "text/csv")

st.markdown("---")

# --- STREAMING_CHUNK: Generating monthly consultant sales and turnover summary... ---
st.subheader("📈 Aylık Personel Ciro Özeti (Yalnızca Muhasebe Onaylılar)")
if not st.session_state.markalar.empty:
    ozet_data = []
    for personel in st.session_state.danismanlar:
        p_rows = st.session_state.markalar[st.session_state.markalar["Personel"] == personel]
        adet = len(p_rows[p_rows["Toplam Onaylı Ciro"] > 0])
        ciro = p_rows["Toplam Onaylı Ciro"].sum()
        ozet_data.append({"Ay / Yıl": "Temmuz 2026", "Satışı Yapan Personel": personel, "Toplam Yapılan Satış (Adet)": adet, "Toplam Onaylanmış Ciro (TL)": f"{ciro} TL"})
    
    st.dataframe(pd.DataFrame(ozet_data))
