import streamlit as st
import google.generativeai as genai
import time

st.set_page_config(page_title="Key Tester", layout="wide")
st.title("🔑 Anahtar Kontrol Merkezi (Röntgen)")

# 1. Anahtarları Al
try:
    if "GOOGLE_API_KEYS" in st.secrets:
        key_list = st.secrets["GOOGLE_API_KEYS"]
        st.info(f"📂 Toplam Anahtar Sayısı: {len(key_list)}")
    else:
        st.error("Secrets dosyasında anahtar bulunamadı!")
        st.stop()
except:
    st.error("Secrets dosyası okunamadı.")
    st.stop()

# 2. Test Butonu
if st.button("Tüm Anahtarları Test Et 🚀"):
    
    progress_bar = st.progress(0)
    status_box = st.empty()
    
    working_keys = []
    failed_keys = []
    
    st.write("---")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("✅ Çalışanlar")
        
    with col2:
        st.subheader("❌ Bozuk/Yetkisizler")

    # Döngüyle Hepsini Dene
    for i, key in enumerate(key_list):
        # İlerleme çubuğunu güncelle
        progress_bar.progress((i + 1) / len(key_list))
        status_box.text(f"Kontrol ediliyor: {i+1}/{len(key_list)} (Sonu: ...{key[-6:]})")
        
        try:
            # Anahtarı ayarla
            genai.configure(api_key=key)
            
            # Basit bir "Merhaba" testi yap (Gemini 2.0 ile)
            model = genai.GenerativeModel('gemini-2.0-flash')
            response = model.generate_content("Test", request_options={"timeout": 5})
            
            # Hata vermediyse çalışıyordur
            with col1:
                st.success(f"Key {i+1} (...{key[-6:]}): BAŞARILI 🟢")
            working_keys.append(key)
            
        except Exception as e:
            error_msg = str(e)
            with col2:
                if "API key not valid" in error_msg:
                    st.error(f"Key {i+1}: GEÇERSİZ ANAHTAR 🔴")
                elif "User has not used the project" in error_msg or "API not enabled" in error_msg:
                    st.warning(f"Key {i+1}: API KAPALI 🟡 (Enable API yapmalısın)")
                elif "429" in error_msg:
                    st.error(f"Key {i+1}: KOTA DOLU 🔴")
                else:
                    st.error(f"Key {i+1}: HATA 🔴 -> {error_msg}")
            failed_keys.append(key)
            
        time.sleep(0.5) # Hızlı gidip kendimiz banlanmayalım

    st.write("---")
    st.metric("Sağlam Anahtar Sayısı", len(working_keys))
    
    if len(working_keys) > 0:
        st.balloons()
        st.success("Tebrikler! Çalışan anahtarların var. Şimdi oyunu tekrar yükleyebilirsin.")
    else:
        st.error("Hiçbir anahtar çalışmadı. Lütfen Secrets dosyasını ve Google Cloud ayarlarını kontrol et.")