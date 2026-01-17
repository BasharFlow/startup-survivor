import streamlit as st
import google.generativeai as genai

# --- AYARLAR ---
# Şifreyi Streamlit'in gizli kasasından çekiyoruz
API_KEY = st.secrets["GOOGLE_API_KEY"] 

# Sayfa Ayarları
st.set_page_config(page_title="Startup Survivor", page_icon="🚀", layout="centered")

# --- MODELİ OTOMATİK BULMA VE BAĞLANMA ---
try:
    genai.configure(api_key=API_KEY)
    
    # Kullanılabilir modelleri listele ve uygun olanı bul
    bulunan_model = None
    kullanilabilir_modeller = []
    
    try:
        for m in genai.list_models():
            kullanilabilir_modeller.append(m.name)
            if 'generateContent' in m.supported_generation_methods:
                # Öncelik Flash modelde (daha hızlı), yoksa Pro, o da yoksa ilk bulduğunu seç
                if 'flash' in m.name:
                    bulunan_model = m.name
                    break
                elif 'pro' in m.name and not bulunan_model:
                    bulunan_model = m.name
        
        # Eğer hiç flash/pro bulamazsa listenin ilkini al
        if not bulunan_model and kullanilabilir_modeller:
             for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    bulunan_model = m.name
                    break

    except Exception as e:
        st.error(f"Model listesi alınamadı. API Key doğru mu? Hata: {e}")
        st.stop()

    if not bulunan_model:
        st.error("Hesabında kullanılabilir bir metin modeli bulunamadı.")
        st.stop()

    # Modeli başlat
    model = genai.GenerativeModel(bulunan_model)
    # Ekrana hangi modelin seçildiğini gizlice yaz (kontrol için)
    print(f"Sistem şu modeli kullanıyor: {bulunan_model}")

except Exception as e:
    st.error(f"Genel Bağlantı Hatası: {e}")
    st.stop()

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