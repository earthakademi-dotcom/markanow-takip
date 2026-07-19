import streamlit as st
import pandas as pd
import os
import re

# ... existing code ...
# (KULLANICILAR, ILLER, tum_sinif_secenekleri tanımları aynı kalıyor)

# ... existing code ...
# (Giriş sistemi aynı kalıyor)

# STREAMING_CHUNK: Satış Girişi ve Kesin Hata Kontrolü
with tab1:
    # Formu daha güvenli işlemek için form dışı bir buton mantığına geçiyoruz
    st.subheader("Yeni Satış Bilgileri")
    
    c1, c2 = st.columns(2)
    m_adi = c1.text_input("Marka Adı*")
    ad_soyad = c1.text_input("Müşteri Ad Soyad*")
    tc = c1.text_input("TC Kimlik No (11 Hane)*")
    tel = c1.text_input("Telefon (05xxxxxxxxx)*")
    dogum = c2.date_input("Doğum Tarihi")
    il = c2.selectbox("İl Seçin*", ILLER)
    sinif = c2.multiselect("Sınıf Seçimi*", tum_sinif_secenekleri)
    satis_tarihi = c2.date_input("Satış Tarihi")
    tutar = st.number_input("Tutar (TL)*", min_value=0.0, format="%.2f")
    
    if st.button("Satışı Kaydet"):
        # Hata listesi oluştur
        errors = []
        if not m_adi: errors.append("Marka Adı boş bırakılamaz.")
        if not ad_soyad: errors.append("Ad Soyad boş bırakılamaz.")
        if len(tc) != 11 or not tc.isdigit(): errors.append("TC Kimlik 11 haneli bir sayı olmalıdır.")
        if not tel.startswith("05") or len(tel) != 11 or not tel.isdigit(): 
            errors.append("Telefon 05 ile başlamalı ve 11 haneli olmalıdır.")
        if not sinif: errors.append("En az bir Sınıf seçmelisiniz.")
        
        if errors:
            for err in errors:
                st.error(f"⚠️ {err}")
        else:
            # Kayıt işlemi
            new_row = {"ID": len(df)+1, "Marka Adı": m_adi, "Ad Soyad": ad_soyad, "TC Kimlik": tc, "Telefon": tel, 
                       "Doğum Tarihi": dogum.strftime("%d.%m.%Y"), "İl": il, "Sınıf": ", ".join(sinif), 
                       "Satış Tarihi": satis_tarihi.strftime("%d.%m.%Y"), "Tutar": tutar, 
                       "Durum": "Bekliyor", "Danışman": st.session_state.kullanici}
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            df.to_csv(DATA_FILE, index=False)
            st.success("Satış başarıyla kaydedildi!")
# ... existing code ...
