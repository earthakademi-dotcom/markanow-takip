import streamlit as st
import pandas as pd
from datetime import datetime

# --- KULLANICI, ŞİFRE VE ROL TANIMLAMALARI ---
KULLANICILAR = {
    "Ali Osman Yelbey": {"sifre": "MarkanowAdmin2026!", "rol": "Admin"},
    "Buğra Büyükeren": {"sifre": "BugraVekil456!", "rol": "Admin"},
    "MERVE YURTLU": {"sifre": "MerveDanisman789!", "rol": "Marka Danışmanı"},
    "Ahmet Yılmaz": {"sifre": "AhmetDanisman321!", "rol": "Marka Danışmanı"},
    "Muhasebe Kullanıcısı": {"sifre": "Muhasebe987!", "rol": "Muhasebe"}
}

st.set_page_config(page_title="Markanow ERP & Satış Takip", layout="wide")

# Oturum Hafızası Başlatma
if "giris_yapildi" not in st.session_state:
    st.session_state.giris_yapildi = False
    st.session_state.kullanici_adi = ""
    st.session_state.kullanici_rolu = ""

if "markalar" not in st.session_state:
    st.session_state.markalar = pd.DataFrame(columns=[
        "Marka Adı", "Personel", "Adı Soyadı", "Telefon No", "Satış Tarihi",
        "Başvuru Ücreti", "B. Onay Durumu", "Savunma Ücreti", "S. Onay Durumu",
        "Tescil Ücreti", "T. Onay Durumu", "Toplam Onaylı Ciro", "Başvuru No",
        "Başvuru Tarihi", "Bülten Tarihi", "İlan Bitiş Tarihi", "İtiraz Tebliğ T.",
        "Savunma Son Gün", "Kurul Kararı / Durum", "Belge Son Ödeme T.", "Yenileme (Vize) T."
    ])

if "danismanlar" not in st.session_state:
    st.session_state.danismanlar = ["MERVE YURTLU", "Ahmet Yılmaz", "Buğra Büyükeren"]

# --- 1. GİRİŞ EKRANI KONTROLÜ ---
if not st.session_state.giris_yapildi:
    st.title("🔒 Markanow Takip Sistemi - Kullanıcı Girişi")
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
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

# --- 2. GİRİŞ YAPILDIYSA SOL PANEL VE GÜVENLİK BİLGİLERİ ---
st.sidebar.title("🔑 Kullanıcı Giriş Paneli")
st.sidebar.success(f"👤 Aktif Kullanıcı: {st.session_state.kullanici_adi}")
st.sidebar.info(f"🛡️ Rolünüz: {st.session_state.kullanici_rolu}")

if st.sidebar.button("Güvenli Çıkış Yap", use_container_width=True):
    st.session_state.giris_yapildi = False
    st.session_state.kullanici_adi = ""
    st.session_state.kullanici_rolu = ""
    st.rerun()

st.sidebar.markdown("---")

# --- 3. ANA UYGULAMA BAŞLIĞI ---
st.title("🛡️ Marka Tescil, Finans ve Personel Takip Sistemi")
st.write(f"Hoş geldiniz. Sistem şu anda **{st.session_state.kullanici_rolu}** yetkileriyle çalışıyor.")
st.markdown("---")

# --- 4. ROL BAZLI PANEL YETKİLENDİRMELERİ ---

# A) MARKA DANIŞMANI PANELİ (Sadece Giriş Yapabilir, Finans/Admin Göremez)
if st.session_state.kullanici_rolu == "Marka Danışmanı":
    st.subheader("📝 Yeni Marka Satış Giriş Formu")
    
    with st.form("danisman_satis_formu", clear_on_submit=True):
        marka_adi = st.text_input("Marka Adı *")
        musteri_ad_soyad = st.text_input("Müşteri Adı Soyadı")
        musteri_tel = st.text_input("Müşteri Telefon No")
        satis_tarihi = st.date_input("Satış Tarihi (Sisteme Giriş)", datetime.today())
        
        submit = st.form_submit_button("Satışı Sisteme Kaydet")
        
        if submit:
            if not marka_adi:
                st.error("Lütfen Marka Adı alanını boş bırakmayınız!")
            else:
                yeni_veri = {
                    "Marka Adı": marka_adi,
                    "Personel": st.session_state.kullanici_adi, # Giriş yapan danışmanın adı otomatik işlenir
                    "Adı Soyadı": musteri_ad_soyad,
                    "Telefon No": musteri_tel,
                    "Satış Tarihi": satis_tarihi.strftime("%d.%m.%Y"),
                    "Başvuru Ücreti": 0, "B. Onay Durumu": "Bekliyor",
                    "Savunma Ücreti": 0, "S. Onay Durumu": "-",
                    "Tescil Ücreti": 0, "T. Onay Durumu": "-",
                    "Toplam Onaylı Ciro": 0, "Başvuru No": "-",
                    "Başvuru Tarihi": "-", "Bülten Tarihi": "-", "İlan Bitiş Tarihi": "-",
                    "İtiraz Tebliğ T.": "-", "Savunma Son Gün": "-", "Kurul Kararı / Durum": "-",
                    "Belge Son Ödeme T.": "-", "Yenileme (Vize) T.": "-"
                }
                st.session_state.markalar = pd.concat([st.session_state.markalar, pd.DataFrame([yeni_veri])], ignore_index=True)
                st.success(f"'{marka_adi}' markası başarıyla kaydedildi! Admin ücret tanımı ve Muhasebe onayı bekleniyor.")

# B) ADMIN YÖNETİM VE SÜREÇ İLERLEME PANELİ (Sadece Admin Görebilir)
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
        with c2:
            s_ucreti = st.number_input("Savunma Ücreti (TL)", value=int(st.session_state.markalar.at[idx, "Savunma Ücreti"]))
            bulten_t = st.text_input("Bülten İlan Tarihi (GG.AA.YYYY)", value=str(st.session_state.markalar.at[idx, "Bülten İlan Tarihi"]))
            itiraz_t = st.text_input("İtiraz Tebliğ Tarihi (GG.AA.YYYY)", value=str(st.session_state.markalar.at[idx, "İtiraz Tebliğ T."]))
        with c3:
            t_ucreti = st.number_input("Tescil Ücreti (TL)", value=int(st.session_state.markalar.at[idx, "Tescil Ücreti"]))
            kurul_karar = st.text_input("Kurul Kararı / Durum", value=str(st.session_state.markalar.at[idx, "Kurul Kararı / Durum"]))
            vize_t = st.text_input("Yenileme (Vize) T. (GG.AA.YYYY)", value=str(st.session_state.markalar.at[idx, "Yenileme (Vize) T."]))
            
        if st.button("Verileri Güncelle / Kaydet", type="primary"):
            st.session_state.markalar.at[idx, "Başvuru Ücreti"] = b_ucreti
            st.session_state.markalar.at[idx, "Başvuru No"] = b_no
            st.session_state.markalar.at[idx, "Başvuru Tarihi"] = b_tarih
            st.session_state.markalar.at[idx, "Savunma Ücreti"] = s_ucreti
            st.session_state.markalar.at[idx, "Bülten İlan Tarihi"] = bulten_t
            st.session_state.markalar.at[idx, "İtiraz Tebliğ T."] = itiraz_t
            st.session_state.markalar.at[idx, "Tescil Ücreti"] = t_ucreti
            st.session_state.markalar.at[idx, "Kurul Kararı / Durum"] = kurul_karar
            st.session_state.markalar.at[idx, "Yenileme (Vize) T."] = vize_t
            
            # Eğer bekliyor durumundaysa ve admin fiyat girdiyse muhasebe için durum alanlarını hazırla
            if st.session_state.markalar.at[idx, "B. Onay Durumu"] == "Bekliyor":
                pass
            if s_ucreti > 0 and st.session_state.markalar.at[idx, "S. Onay Durumu"] == "-":
                st.session_state.markalar.at[idx, "S. Onay Durumu"] = "Bekliyor"
            if t_ucreti > 0 and st.session_state.markalar.at[idx, "T. Onay Durumu"] == "-":
                st.session_state.markalar.at[idx, "T. Onay Durumu"] = "Bekliyor"
                
            st.success("Süreç ve finansal tanımlamalar başarıyla güncellendi!")
            st.rerun()
    else:
        st.info("Sistemde henüz süreç güncellemesi yapılacak bir marka bulunmuyor.")

# C) MUHASEBE PANELİ (Sadece Ödeme Onaylarını Kontrol Edebilir)
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
            
            # Ödeme Butonları
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

# --- 5. ORTAK CANLI RAPORLAMA VE CİRO TABLOLARI (Herkes Görebilir)
st.subheader("📊 Canlı Rapor Tablosu (Excel / Google E-Tablolar Uyumlu)")

# Canlı Ciro Hesaplama Mantığı
for i, row in st.session_state.markalar.iterrows():
    toplam = 0
    if row["B. Onay Durumu"] == "ONAYLANDI": toplam += int(row["Başvuru Ücreti"])
    if row["S. Onay Durumu"] == "ONAYLANDI": toplam += int(row["Savunma Ücreti"])
    if row["T. Onay Durumu"] == "ONAYLANDI": toplam += int(row["Tescil Ücreti"])
    st.session_state.markalar.at[i, "Toplam Onaylı Ciro"] = toplam

st.dataframe(st.session_state.markalar)

# Excel Çıktı Altyapısı
def convert_df(df):
    return df.to_csv(index=False).encode('utf-8')
csv_data = convert_df(st.session_state.markalar)
st.download_button("📥 Tabloyu Excel (CSV) Olarak İndir", csv_data, "marka_takip_raporu.csv", "text/csv")

st.markdown("---")

st.subheader("📈 Aylık Personel Ciro Özeti (Yalnızca Muhasebe Onaylılar)")
if not st.session_state.markalar.empty:
    ozet_data = []
    for personel in st.session_state.danismanlar:
        p_rows = st.session_state.markalar[st.session_state.markalar["Personel"] == personel]
        adet = len(p_rows[p_rows["Toplam Onaylı Ciro"] > 0])
        ciro = p_rows["Toplam Onaylı Ciro"].sum()
        ozet_data.append({"Ay / Yıl": "Temmuz 2026", "Satışı Yapan Personel": personel, "Toplam Yapılan Satış (Adet)": adet, "Toplam Onaylanmış Ciro (TL)": f"{ciro} TL"})
    
    st.dataframe(pd.DataFrame(ozet_data))
