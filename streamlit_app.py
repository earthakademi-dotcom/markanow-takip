import streamlit as st

# --- ŞİFRE KAYDETME VE GÜNCELLEME ---
def sifre_kayit_paneli():
    st.markdown("### 🔑 Şifre Yönetimi")
    st.info("Kişisel şifrenizi güncellemek için aşağıdaki formu kullanın.")
    
    with st.form("sifre_guncelle_formu"):
        mevcut = st.text_input("Mevcut Şifre", type="password")
        yeni = st.text_input("Yeni Şifre", type="password")
        yeni_tekrar = st.text_input("Yeni Şifre (Tekrar)", type="password")
        
        kaydet = st.form_submit_button("Şifreyi Güncelle ve Kaydet")
        
        if kaydet:
            # Mevcut şifre kontrolü
            if mevcut == KULLANICILAR[st.session_state.kullanici_adi]["sifre"]:
                if yeni == yeni_tekrar and len(yeni) >= 6:
                    # Şifre güncelleme işlemi
                    KULLANICILAR[st.session_state.kullanici_adi]["sifre"] = yeni
                    st.success("Şifreniz başarıyla güncellendi ve sisteme kaydedildi!")
                elif len(yeni) < 6:
                    st.error("Şifre en az 6 karakter olmalıdır.")
                else:
                    st.error("Yeni şifreler eşleşmiyor!")
            else:
                st.error("Mevcut şifrenizi yanlış girdiniz.")

# --- MENÜYE EKLEME ---
# Sidebar fonksiyonunuzun içine ekleyin:
def sidebar_menu():
    # ... mevcut menüler ...
    st.markdown('<p class="menu-header">HESAP</p>', unsafe_allow_html=True)
    if st.button("🔑 Şifre Ayarları"): st.session_state.menu = "Sifre_Ayarlari"
    # ...

# --- UYGULAMA İÇİNDE ---
if st.session_state.menu == "Sifre_Ayarlari":
    sifre_kayit_paneli()
