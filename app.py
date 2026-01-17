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

# --- 1. ZORUNLU ANAHTAR ROTASYONU ---
def get_random_key():
    """Secrets dosyasındaki 30 anahtardan birini rastgele seçer."""
    try:
        if "GOOGLE_API_KEYS" in st.secrets:
            key_list = st.secrets["GOOGLE_API_KEYS"]
            # Listeden rastgele bir anahtar seç
            selected_key = random.choice(key_list)
            return selected_key
        else:
            st.error("HATA: Secrets dosyasında anahtar listesi bulunamadı!")
            return None
    except Exception as e:
        st.error(f"Anahtar seçim hatası: {e}")
        return None

# --- 2. OYUN HAFIZASI ---
if "history" not in st.session_state:
    st.session_state.history = []
if "stats" not in st.session_state:
    st.session_state.stats = {"money": 50, "team": 50, "motivation": 50}
if "month" not in st.session_state:
    st.session_state.month = 0
if "game_over" not in st.session_state:
    st.session_state.game_over = False
if "game_over_reason" not in st.session_state:
    st.session_state.game_over_reason = ""

# --- 3. YAPAY ZEKA FONKSİYONU ---
def get_ai_response(user_input):
    # ADIM 1: Yeni bir anahtar çek ve sisteme yükle
    active_key = get_random_key()
    if not active_key:
        return None
    
    genai.configure(api_key=active_key)
    
    # Debug: Hangi anahtarın kullanıldığını (son 4 hanesini) görmek istersen:
    # print(f"Kullanılan Anahtar Sonu: ...{active_key[-4:]}")

    # ADIM 2: Prompt Hazırla
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
    
    # ADIM 3: Modeli Seç (gemini-1.5-flash şu an en kararlı olanıdır)
    # Eğer 1.5 çalışmazsa 2.0'ı dener.
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
    except:
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
    
    chat_history = [{"role": "user", "parts": [system_prompt]}]
    for msg in st.session_state.history:
        chat_history.append(msg)
    
    chat_history.append({"role": "user", "parts": [user_input]})

    try:
        response = model.generate_content(chat_history)
        text = response.text
        # JSON temizliği
        text = text.replace("```json", "").replace("```", "").strip()
        return json.loads(text)
    except Exception as e:
        st.error(f"Yapay zeka hatası (Anahtar limiti veya model sorunu): {e}")
        return None

# --- 4. ARAYÜZ (UI) ---

st.title("🚀 Startup Survivor")
st.caption(f"Sistem Durumu: 🟢 Aktif | 30 Anahtarlı Rotasyon Devrede")
st.markdown("---")

col1, col2, col3 = st.columns(3)
col1.metric("💰 Nakit", f"%{st.session_state.stats['money']}")
col1.progress(st.session_state.stats['money'] / 100)

col2.metric("👥 Ekip Ruhu", f"%{st.session_state.stats['team']}")
col2.progress(st.session_state.stats['team'] / 100)

col3.metric("🔥 Motivasyon", f"%{st.session_state.stats['motivation']}")
col3.progress(st.session_state.stats['motivation'] / 100)

st.markdown("---")

for msg in st.session_state.history:
    if msg["role"] == "model":
        try:
            content = json.loads(msg["parts"][0])["text"]
        except:
            content = msg["parts"][0]
        with st.chat_message("ai"):
            st.write(content)
    else:
        if "Sen 'Startup Survivor'" not in msg["parts"][0]:
            with st.chat_message("user"):
                st.write(msg["parts"][0])

# --- 5. OYUN AKIŞI ---

if st.session_state.month == 0:
    with st.chat_message("ai"):
        st.write("Hoş geldin Girişimci! 🌍 Şirketinin adı ne ve ne üretiyorsunuz? (Örn: 'Uçan Kargo Dronu yapan SkyNet')")
    
    startup_idea = st.chat_input("Girişim fikrini buraya yaz...")
    if startup_idea:
        with st.spinner("Yatırımcılar ve Analistler toplanıyor..."):
            response_json = get_ai_response(f"Oyun başlıyor. Girişim fikrim: {startup_idea}. Bana ilk ayın durumunu (Ay 1) ve istatistikleri (hepsi 50 başlasın) ver.")
            
            if response_json:
                st.session_state.history.append({"role": "user", "parts": [f"Girişimim: {startup_idea}"]})
                st.session_state.history.append({"role": "model", "parts": [json.dumps(response_json)]})
                st.session_state.stats = response_json["stats"]
                st.session_state.month = response_json["month"]
                st.rerun()

elif not st.session_state.game_over:
    user_move = st.chat_input("Hamleni yap (Örn: 'Yatırımcıyla görüş' veya 'Reklam ver')...")
    
    if user_move:
        st.session_state.history.append({"role": "user", "parts": [user_move]})
        with st.spinner("Piyasa tepki veriyor..."):
            response_json = get_ai_response(user_move)
            
            if response_json:
                st.session_state.history.append({"role": "model", "parts": [json.dumps(response_json)]})
                st.session_state.stats = response_json["stats"]
                st.session_state.month = response_json["month"]
                if response_json.get("game_over") == True:
                    st.session_state.game_over = True
                    st.session_state.game_over_reason = response_json.get("game_over_reason", "Bilinmiyor")
                st.rerun()

else:
    st.error(f"❌ OYUN BİTTİ! Sebebi: {st.session_state.get('game_over_reason', 'İflas')}")
    if st.button("Tekrar Dene 🔄"):
        st.session_state.history = []
        st.session_state.stats = {"money": 50, "team": 50, "motivation": 50}
        st.session_state.month = 0
        st.session_state.game_over = False
        st.session_state.game_over_reason = ""
        st.rerun()