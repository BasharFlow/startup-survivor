import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="Manuel Test", page_icon="🔑")

st.title("🔑 Manuel Anahtar Testi")
st.warning("Bu test, Secrets dosyasını atlar ve anahtarı doğrudan dener.")

# 1. Anahtarı Elle Gir (Secrets dosyasını kullanmıyoruz)
api_key = st.text_input("O yeni, hiç kullanılmamış anahtarı buraya yapıştır:", type="password")

if st.button("Test Et 🚀"):
    if not api_key:
        st.error("Lütfen bir anahtar yapıştırın.")
    else:
        try:
            # 2. Bağlantıyı Kur
            genai.configure(api_key=api_key)
            
            # 3. Modeli Dene (Senin hesabında açık olan 2.0 Flash ile)
            model = genai.GenerativeModel('gemini-2.0-flash')
            
            with st.spinner("Google'a bağlanılıyor..."):
                response = model.generate_content("Merhaba, sen çalışıyor musun?", request_options={"timeout": 10})
            
            # 4. Sonuç
            st.balloons()
            st.success("✅ ÇALIŞTI! Sorun senin anahtarında değil, Streamlit'in eski anahtarı hafızada tutmasındaymış.")
            st.write(f"Cevap: {response.text}")
            
        except Exception as e:
            st.error("❌ HATA DEVAM EDİYOR!")
            st.code(str(e))
            
            if "429" in str(e):
                st.error("YORUM: Bu anahtar gerçekten bloklanmış. Google, seri üretim proje açtığın için ana hesabını geçici olarak 'spam' moduna almış olabilir.")
            elif "API key not valid" in str(e):
                st.error("YORUM: Anahtar yanlış kopyalanmış.")