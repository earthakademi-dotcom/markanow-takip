import streamlit as st
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta

# Sayfa Genişlik Ayarı
st.set_page_config(layout="wide", page_title="Markanow ERP & Satış Takip")

# Başlık
st.title("🛡️ Marka Tescil, Finans ve Personel Takip Sistemi")
st.write("Admin, Marka Danışmanı ve Muhasebe onay mekanizmalı dijital takip paneli.")

# Veri Tabanı Başlatma (Oturum Hafızası)
if 'markalar' not in st.session_state:
    st.session_state.markalar = pd.DataFrame(columns=[
        "Marka Adı", "Personel", "Adı Soyadı", "Telefon No", "Satış Tarihi",
        "Başvuru Ücreti", "B. Onay Durumu", "Savunma Ücreti", "S. Onay Durumu",
        "Tescil Ücreti", "T. Onay Durumu", "Toplam Onaylı Ciro", "Başvuru No",
        "Başvuru Tarihi", "Bültên Tarihi", "İlan Bitiş Tarihi", "İtiraz Tebliğ T.",
        "Savunma Son Gün", "Kurul Kararı / Durum", "Belge Son Ödeme T.", "Yenileme (Vize) T.",
        "Mevcut Aşama & İşlem Durumu"
    ])

if 'danismanlar' not in st.session_state:
    st.session_state.danismanlar = ["Buğra Büyükeren", "Ahmet Yılmaz"]

# Tarih Hesaplama Yardımcı Fonksiyonu
def tarih_ekle(tarih_str, ay=0, yil=0):
    if not tarih_str or pd.isna(tarih_str) or tarih_str == "-":
        return "-"
    try:
        dt = datetime.strptime(str(tarih_str), "%d.%m.%Y")
        yeni_dt = dt + relativedelta(months=ay, years=yil)
        return yeni_dt.strftime("%d.%m.%Y")
    except:
        return "-"

# --- YAN PANEL: KULLANICI GİRİŞİ & ROLLER ---
st.sidebar.header("🔑 Kullanıcı Giriş Paneli")
rol = st.sidebar.selectbox("Rolünüzü Seçin", ["Admin", "Marka Danışmanı", "Muhasebe"])
aktif_kullanici = st.sidebar.text_input("İsminiz", value="Ali Osman Yelbey")

st.sidebar.markdown("---")

# --- ROL YETKİLENDİRME VE VERİ GİRİŞ ALANLARI ---

if rol == "Marka Danışmanı":
    st.header("📝 Marka Danışmanı Satış Giriş Ekranı")
    with st.form("danisman_form"):
        m_danisman = st.selectbox("İsminiz", st.session_state.danismanlar)
        m_adi = st.text_input("Marka Adı")
        m_musteri = st.text_input("Müşteri Adı Soyadı")
        m_tel = st.text_input("Telefon Numarası")
        m_satis_tarihi = st.date_input("Satış Tarihi (Sisteme Giriş)").strftime("%d.%m.%Y")
        
        submit = st.form_submit_button("Satışı Sisteme Kaydet")
        if submit and m_adi:
            yeni_satir = {col: "-" for col in st.session_state.markalar.columns}
            yeni_satir.update({
                "Marka Adı": m_adi, "Personel": m_danisman, "Adı Soyadı": m_musteri,
                "Telefon No": m_tel, "Satış Tarihi": m_satis_tarihi,
                "Başvuru Ücreti": 0, "B. Onay Durumu": "Bekliyor",
                "Savunma Ücreti": 0, "S. Onay Durumu": "-",
                "Tescil Ücreti": 0, "T. Onay Durumu": "-",
                "Toplam Onaylı Ciro": 0, "Mevcut Aşama & İşlem Durumu": "1. Adım - Giriş (Başvuru Bekleniyor)"
            })
            st.session_state.markalar = pd.concat([st.session_state.markalar, pd.DataFrame([yeni_satir])], ignore_index=True)
            st.success(f"{m_adi} markası başarıyla kaydedildi! Admin ücret tanımı ve Muhasebe onayı bekleniyor.")

elif rol == "Admin":
    st.header("⚙️ Admin Yönetim ve Süreç İlerleme Paneli")
    
    # Kadro Yönetimi
    with st.expander("👥 Danışman Ekle / Çıkar"):
        yeni_d = st.text_input("Yeni Danışman Adı")
        if st.button("Danışmanı Kadroya Ekle") and yeni_d:
            st.session_state.danismanlar.append(yeni_d)
            st.success(f"{yeni_d} sisteme eklendi.")
            
    if not st.session_state.markalar.empty:
        secilen_marka = st.selectbox("Süreç Güncellenecek Markayı Seçin", st.session_state.markalar["Marka Adı"].unique())
        idx = st.session_state.markalar[st.session_state.markalar["Marka Adı"] == secilen_marka].index[0]
        
        with st.form("admin_guncelleme"):
            st.subheader(f"🔄 {secilen_marka} - Güncelleme Ekranı")
            
            b_ucret = st.number_input("Başvuru Ücreti (TL)", value=int(st.session_state.markalar.at[idx, "Başvuru Ücreti"]))
            b_no = st.text_input("Başvuru No", value=str(st.session_state.markalar.at[idx, "Başvuru No"]))
            b_tar = st.text_input("Başvuru Tarihi (GG.AA.YYYY)", value=str(st.session_state.markalar.at[idx, "Başvuru Tarihi"]))
            
            bul_tar = st.text_input("Bülten İlan Tarihi (GG.AA.YYYY)", value=str(st.session_state.markalar.at[idx, "Bültên Tarihi"]))
            
            itz_tar = st.text_input("İtiraz Tebliğ Tarihi (GG.AA.YYYY)", value=str(st.session_state.markalar.at[idx, "İtiraz Tebliğ T."]))
            s_ucret = st.number_input("Savunma Ücreti (TL)", value=int(st.session_state.markalar.at[idx, "Savunma Ücreti"]))
            kurul_durum = st.text_input("Kurul Kararı / Durum", value=str(st.session_state.markalar.at[idx, "Kurul Kararı / Durum"]))
            
            t_ucret = st.number_input("Tescil Ücreti (TL)", value=int(st.session_state.markalar.at[idx, "Tescil Ücreti"]))
            t_bildirim = st.text_input("Tescil Bildirim Tarihi", value="-")
            
            asama_durum = st.text_input("Mevcut Aşama & Durum Notu", value=str(st.session_state.markalar.at[idx, "Mevcut Aşama & İşlem Durumu"]))
            
            if st.form_submit_button("Marka Sürecini ve Ücretleri Güncelle"):
                st.session_state.markalar.at[idx, "Başvuru Ücreti"] = b_ucret
                st.session_state.markalar.at[idx, "Başvuru No"] = b_no
                st.session_state.markalar.at[idx, "Başvuru Tarihi"] = b_tar
                st.session_state.markalar.at[idx, "Bültên Tarihi"] = bul_tar
                st.session_state.markalar.at[idx, "İtiraz Tebliğ T."] = itz_tar
                st.session_state.markalar.at[idx, "Savunma Ücreti"] = s_ucret
                st.session_state.markalar.at[idx, "Kurul Kararı / Durum"] = kurul_durum
                st.session_state.markalar.at[idx, "Tescil Ücreti"] = t_ucret
                st.session_state.markalar.at[idx, "Mevcut Aşama & İşlem Durumu"] = asama_durum
                
                # Otomatik Hesaplamalar
                if bul_tar != "-":
                    st.session_state.markalar.at[idx, "İlan Bitiş Tarihi"] = tarih_ekle(bul_tar, ay=2)
                    st.session_state.markalar.at[idx, "Yenileme (Vize) T."] = tarih_ekle(bul_tar, yil=10)
                if itz_tar != "-":
                    st.session_state.markalar.at[idx, "Savunma Son Gün"] = tarih_ekle(itz_tar, ay=1)
                if t_bildirim != "-":
                    st.session_state.markalar.at[idx, "Belge Son Ödeme T."] = tarih_ekle(t_bildirim, ay=2)
                    
                st.success("Veriler güncellendi, yasal takvimler yeniden hesaplandı!")
    else:
        st.info("Sistemde henüz kayıtlı marka yok. Önce Danışman rolüyle veri ekleyin.")

elif rol == "Muhasebe":
    st.header("💰 Muhasebe Ödeme Onay Ekranı")
    if not st.session_state.markalar.empty:
        secilen_marka = st.selectbox("Ödemesi Kontrol Edilecek Marka", st.session_state.markalar["Marka Adı"].unique())
        idx = st.session_state.markalar[st.session_state.markalar["Marka Adı"] == secilen_marka].index[0]
        
        st.write(f"**Başvuru Ücreti:** {st.session_state.markalar.at[idx, 'Başvuru Ücreti']} TL | Durum: {st.session_state.markalar.at[idx, 'B. Onay Durumu']}")
        if st.session_state.markalar.at[idx, 'B. Onay Durumu'] == "Bekliyor" and st.button("Başvuru Ödemesini Onayla"):
            st.session_state.markalar.at[idx, 'B. Onay Durumu'] = "ONAYLANDI"
            st.success("Başvuru ücreti onaylandı! Ciroya yansıtıldı.")
            st.rerun()
            
        st.write(f"**Savunma Ücreti:** {st.session_state.markalar.at[idx, 'Savunma Ücreti']} TL")
        if st.button("Savunma Ödemesini Onayla"):
            st.session_state.markalar.at[idx, 'S. Onay Durumu'] = "ONAYLANDI"
            st.success("Savunma ücreti onaylandı! Ciroya yansıtıldı.")
            st.rerun()

        st.write(f"**Tescil Ücreti:** {st.session_state.markalar.at[idx, 'Tescil Ücreti']} TL")
        if st.button("Tescil Belge Ödemesini Onayla"):
            st.session_state.markalar.at[idx, 'T. Onay Durumu'] = "ONAYLANDI"
            st.success("Tescil ücreti onaylandı! Ciroya yansıtıldı.")
            st.rerun()
    else:
        st.info("Onaylanacak herhangi bir işlem bulunmuyor.")

# --- DİNAMİK CİRO HESAPLAMA MOTORU ---
for i, row in st.session_state.markalar.iterrows():
    toplam = 0
    if row["B. Onay Durumu"] == "ONAYLANDI": toplam += int(row["Başvuru Ücreti"])
    if row["S. Onay Durumu"] == "ONAYLANDI": toplam += int(row["Savunma Ücreti"])
    if row["T. Onay Durumu"] == "ONAYLANDI": toplam += int(row["Tescil Ücreti"])
    st.session_state.markalar.at[i, "Toplam Onaylı Ciro"] = toplam

st.markdown("---")

# --- 📊 ANA RAPORLAMA VE EXCEL TABLOLARI ---
st.subheader("📊 Canlı Rapor Tablosu (Excel / Google E-Tablolar Uyumlu)")
st.dataframe(st.session_state.markalar)

# Excel Çıktı Butonu
def convert_df(df): return df.to_csv(index=False).encode('utf-8')
csv = convert_df(st.session_state.markalar)
st.download_button("📥 Tabloyu Excel (CSV) Olarak İndir", csv, "marka_takip_raporu.csv", "text/csv")

st.markdown("---")

st.subheader("📈 Aylık Personel Ciro Özeti (Yalnızca Muhasebe Onaylılar)")
if not st.session_state.markalar.empty:
    ozet_data = []
    for personel in st.session_state.danismanlar:
        p_rows = st.session_state.markalar[st.session_state.markalar["Personel"] == personel]
        adet = len(p_rows[p_rows["Toplam Onaylı Ciro"] > 0])
        ciro = p_rows["Toplam Onaylı Ciro"].sum()
        ozet_data.append({"Ay / Yıl": "Temmuz 2026", "Satışı Yapan Personel": personel, "Toplam Yapılan Satış (Adet)": adet, "Toplam Onaylanmış Ciro (TL)": f"{ciro} TL"})
    st.table(pd.DataFrame(ozet_data))
