import streamlit as st
import google.generativeai as genai

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Startup Survivor", page_icon="🚀", layout="centered")

# --- 1. BAĞLANTI VE OTOMATİK MODEL SEÇİMİ ---
def configure_genai():
    # 1. Anahtarı Bul
    api_key = None
    if "GOOGLE_API_KEYS" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEYS"][0]
    elif "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]

    if not api_key:
        st.error("HATA: Secrets dosyasında API Anahtarı bulunamadı!")
        st.stop()

    try:
        genai.configure(api_key=api_key)
        
        # 2. Hesabındaki Açık Modeli Otomatik Bul
        bulunan_model = None
        # Öncelik sırası: Önce 2.0 Flash (Hızlı), sonra 1.5 Flash, sonra Pro
        oncelikli_modeller = ['gemini-2.0-flash', 'gemini-1.5-flash', 'gemini-pro']
        
        # Önce listedekileri dene
        for m_name in oncelikli_modeller:
            try:
                model = genai.GenerativeModel(m_name)
                # Test atışı yapalım ki modelin çalıştığından emin olalım
                model.generate_content("Test")
                bulunan_model = m_name
                break
            except:
                continue
        
        # Eğer listedekiler çalışmazsa, sistemden herhangi bir açık model bul
        if not bulunan_model:
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    bulunan_model = m.name
                    break
        
        if not bulunan_model:
            st.error("Hesabında kullanılabilir model bulunamadı.")
            st.stop()
            
        return genai.GenerativeModel(bulunan_model)

    except Exception as e:
        st.error(f"Bağlantı Hatası: {e}")
        st.stop()

# Modeli Başlat
model = configure_genai()

# --- OYUN FONKSİYONLARI ---
def oyun_baslat(startup_fikri):
    prompt = f"""
    Sen 'Startup Survivor' oyunusun. Kullanıcının Fikri: "{startup_fikri}"
    GÖREVİN:
    1. Bu fikrin ilk ayını simüle et.
    2. Kullanıcıya bir kriz sun.
    3. İki seçenek (A ve B) öner.
    Cevabı şu formatta ver:
    **DURUM:** [Durum]
    **KRİZ:** [Kriz]
    **SEÇENEKLER:** A) [Seçenek 1] B) [Seçenek 2]
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Yapay zeka yanıt veremedi. Hata: {e}"

def hamle_yap(eski_hikaye, kullanici_hamlesi):
    prompt = f"""
    Önceki Hikaye: {eski_hikaye}
    Kullanıcının Hamlesi: "{kullanici_hamlesi}"
    GÖREVİN:
    1. Hamlenin sonucunu yaz (Başarılı mı, battı mı?).
    2. Hikayeyi sonraki aya taşı ve yeni kriz çıkar.
    Cevap Formatı:
    **SONUÇ:** [Sonuç]
    **YENİ DURUM:** [Yeni durum]
    **KRİZ:** [Yeni kriz]
    **SEÇENEKLER:** A) [Seçenek 1] B) [Seçenek 2]
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Yapay zeka yanıt veremedi. Hata: {e}"

# --- ARAYÜZ ---
st.title("🚀 Startup Survivor")
st.write("Girişim fikrini yaz, bakalım 12 ay hayatta kalabilecek misin?")

if "messages" not in st.session_state:
    st.session_state.messages = []
if "oyun_aktif" not in st.session_state:
    st.session_state.oyun_aktif = False

if not st.session_state.oyun_aktif:
    fikir = st.chat_input("Fikrini buraya yaz (Örn: Uçan Kargo Drone'ları)...")
    if fikir:
        st.session_state.oyun_aktif = True
        st.session_state.messages.append({"role": "user", "content": fikir})
        with st.spinner("Simülasyon başlatılıyor..."):
            cevap = oyun_baslat(fikir)
            st.session_state.messages.append({"role": "assistant", "content": cevap})
            st.rerun()
else:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    hamle = st.chat_input("Hamleni yap (A, B veya kendi fikrin)...")
    if hamle:
        st.session_state.messages.append({"role": "user", "content": hamle})
        with st.chat_message("user"):
            st.write(hamle)
        with st.chat_message("assistant"):
            with st.spinner("Hesaplanıyor..."):
                gecmis = "\n".join([m["content"] for m in st.session_state.messages[-3:]])
                cevap = hamle_yap(gecmis, hamle)
                st.markdown(cevap)
                st.session_state.messages.append({"role": "assistant", "content": cevap})