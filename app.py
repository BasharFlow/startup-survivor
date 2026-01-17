import streamlit as st
import google.generativeai as genai
import random
import json
import time

# --- SAYFA AYARLARI ---
st.set_page_config(
    page_title="Startup Survivor",
    page_icon="🚀",
    layout="centered"
)

# --- 1. API KEY ROTASYONU (30 KEY DESTEKLİ) ---
def configure_genai():
    try:
        # Secrets dosyasındaki listeden rastgele bir anahtar seç
        if "GOOGLE_API_KEYS" in st.secrets:
            key_list = st.secrets["GOOGLE_API_KEYS"]
            selected_key = random.choice(key_list)
            genai.configure(api_key=selected_key)
            return True
        else:
            st.error("HATA: Secrets dosyasında GOOGLE_API_KEYS bulunamadı!")
            return False
    except Exception as e:
        st.error(f"Konfigürasyon hatası: {e}")
        return False

# --- 2. OYUN HAFIZASI (SESSION STATE) ---
if "history" not in st.session_state:
    st.session_state.history = []  # Sohbet geçmişi
if "stats" not in st.session_state:
    st.session_state.stats = {
        "money": 50,
        "team": 50,
        "motivation": 50
    }
if "month" not in st.session_state:
    st.session_state.month = 0
if "game_over" not in st.session_state:
    st.session_state.game_over = False
if "last_scenario" not in st.session_state:
    st.session_state.last_scenario = None

# --- 3. YAPAY ZEKA FONKSİYONU ---
def get_ai_response(user_input):
    # Anahtarımızı her seferinde tazeleyelim (Rotation)
    if not configure_genai():
        return None

    # Sistem Talimatı (Prompt Mühendisliği)
    system_prompt = """
    Sen 'Startup Survivor' adında zorlu bir girişimcilik simülasyonusun.
    Görevin: Kullanıcının startup'ını 12 ay boyunca hayatta tutmaya çalışmak.
    
    Kurallar:
    1. Her turda bir kriz veya olay yarat.
    2. Kullanıcıya seçenekler sun veya kendi cevabını yorumla.
    3. Şu istatistikleri takip et (0-100 arası): Para (Money), Ekip (Team), Motivasyon (Motivation).
    4. Herhangi biri 0 olursa oyun biter (Game Over).
    5. Cevabını SADECE ve SADECE şu JSON formatında ver (yorum katma):
    
    {
        "text": "Olayın hikayesi ve sonucu buraya...",
        "month": (Şu anki ay sayısı),
        "stats": {"money": (yeni değer), "team": (yeni değer), "motivation": (yeni değer)},
        "game_over": (true veya false),
        "game_over_reason": "Eğer bittiyse sebebi, yoksa boş bırak"
    }
    """
    
    # Model Ayarları
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    # Sohbet Geçmişini Modele Verelim
    chat_history = [{"role": "user", "parts