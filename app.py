import streamlit as st
import google.generativeai as genai
import os

st.title("🔍 Arıza Tespit Ekranı")
st.write(f"Kütüphane Sürümü: {genai.__version__}")

# 1. Anahtarı Al ve Bağlan
try:
    # Secrets içindeki listenin İLK anahtarını alıp deneyelim
    if "GOOGLE_API_KEYS" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEYS"][0]
        st.info(f"🔑 Denenen Anahtar Sonu: ...{api_key[-10:]}")
        genai.configure(api_key=api_key)
    else:
        st.error("Secrets dosyasında anahtar bulunamadı!")
        st.stop()
except Exception as e:
    st.error(f"Anahtar okuma hatası: {e}")
    st.stop()

# 2. Google'a Sor: "Hangi modelleri kullanabilirim?"
st.write("📡 Google sunucularına bağlanılıyor...")

try:
    uygun_modeller = []
    # Tüm modelleri listele
    for m in genai.list_models():
        # Sadece metin üretebilenleri (generateContent) filtrele
        if 'generateContent' in m.supported_generation_methods:
            uygun_modeller.append(m.name)
    
    if uygun_modeller:
        st.success("✅ BAĞLANTI BAŞARILI! Bu anahtarın yetkisi olan modeller:")
        st.json(uygun_modeller)
        st.write("👆 **Yukarıdaki listede yazan isimlerden birini koda yazarsak %100 çalışır.**")
    else:
        st.error("❌ Bağlantı kuruldu ama LİSTE BOŞ GELDİ. Bu, anahtarın 'Generative Language API' yetkisinin kapalı olduğunu gösterir.")
        
except Exception as e:
    st.error(f"❌ Bağlantı Hatası: {e}")
    st.warning("İpucu: Eğer '400 Bad Request' veya 'API Key invalid' alıyorsan, proje silinmiş veya faturalandırma sorunu vardır.")