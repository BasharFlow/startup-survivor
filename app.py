import streamlit as st
import google.generativeai as genai
import random
import json

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Startup Survivor", page_icon="🚀", layout="centered")

# --- 1. TEK ANAHTARLI BASİT BAĞLANTI ---
def configure_genai():
    try:
        if "GOOGLE_API_KEYS" in st.secrets:
            # Listeden ilk anahtarı al
            api_key = st.secrets["GOOGLE_API_KEYS"][0]
            genai.configure(api_key=api_key)
            return True
        else:
            st.error("HATA: Secrets dosyasında anahtar bulunamadı!")
            return False
    except Exception as e:
        st.error(f"Bağlantı Hatası: {e}")
        return False

# --- 2. OYUN DEĞİŞKENLERİ ---
if "history" not in st.session_state: st.session_state.history = []
if "stats" not in st.session_state: st.session_state.stats = {"money": 50, "team": 50, "motivation": 50}
if "month" not in st.session_state: st.session_state.month = 0
if "game_over" not in st.session_state: st.session_state.game_over = False
if "game_over_reason" not in st.session_state: st.session_state.game_over_reason = ""

# --- 3. YAPAY ZEKA ---
def get_ai_response(user_input):
    if not configure_genai(): return None

    system_prompt = """
    Sen 'Startup Survivor' adında zorlu bir girişimcilik simülasyonusun.
    Görevin: Kullanıcının startup'ını 12 ay boyunca hayatta tutmaya çalışmak.
    Kurallar: 1. Her turda kriz yarat. 2. İstatistikleri (Money, Team, Motivation) yönet. 3. Biri 0 olursa Game Over.
    Cevabını SADECE şu JSON formatında ver:
    {"text": "Hikaye...", "month": (ay), "stats": {"money": 50, "team": 50, "motivation": 50}, "game_over": false, "game_over_reason": ""}
    """
    
    # --- DÜZELTME BURADA: ARTIK 2.0 KULLANILIYOR ---
    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
    except:
        # Eğer onda da sorun çıkarsa (çok düşük ihtimal) en temel modele geç
        model = genai.GenerativeModel('gemini-pro')
    
    chat_history = [{"role": "user", "parts": [system_prompt]}]
    for msg in st.session_state.history: chat_history.append(msg)
    chat_history.append({"role": "user", "parts": [user_input]})

    try:
        response = model.generate_content(chat_history)
        text = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(text)
    except Exception as e:
        st.error(f"AI Model Hatası: {e}")
        return None

# --- 4. ARAYÜZ ---
st.title("🚀 Startup Survivor")
st.caption("🟢 Sistem Aktif | Model: Gemini 2.0 Flash")
st.markdown("---")

col1, col2, col3 = st.columns(3)
col1.metric("💰 Nakit", f"%{st.session_state.stats['money']}")
col1.progress(st.session_state.stats['money'] / 100)
col2.metric("👥 Ekip", f"%{st.session_state.stats['team']}")
col2.progress(st.session_state.stats['team'] / 100)
col3.metric("🔥 Motivasyon", f"%{st.session_state.stats['motivation']}")
col3.progress(st.session_state.stats['motivation'] / 100)
st.markdown("---")

for msg in st.session_state.history:
    if msg["role"] == "model":
        try: content = json.loads(msg["parts"][0])["text"]
        except: content = msg["parts"][0]
        with st.chat_message("ai"): st.write(content)
    else:
        if "Sen 'Startup Survivor'" not in msg["parts"][0]:
            with st.chat_message("user"): st.write(msg["parts"][0])

if st.session_state.month == 0:
    st.info("Hoş geldin! Şirketinin adı ne?")
    startup_idea = st.chat_input("Girişim fikrini yaz...")
    if startup_idea:
        with st.spinner("Yatırımcılar fikrini inceliyor..."):
            response = get_ai_response(f"Oyun başlasın. Fikrim: {startup_idea}")
            if response:
                st.session_state.history.append({"role": "user", "parts": [f"Girişim: {startup_idea}"]})
                st.session_state.history.append({"role": "model", "parts": [json.dumps(response)]})
                st.session_state.stats = response["stats"]
                st.session_state.month = response["month"]
                st.rerun()
elif not st.session_state.game_over:
    user_move = st.chat_input("Ne yapacaksın?")
    if user_move:
        st.session_state.history.append({"role": "user", "parts": [user_move]})
        with st.spinner("Piyasa tepki veriyor..."):
            response = get_ai_response(user_move)
            if response:
                st.session_state.history.append({"role": "model", "parts": [json.dumps(response)]})
                st.session_state.stats = response["stats"]
                st.session_state.month = response["month"]
                if response.get("game_over"):
                    st.session_state.game_over = True
                    st.session_state.game_over_reason = response.get("game_over_reason")
                st.rerun()
else:
    st.error(f"OYUN BİTTİ: {st.session_state.game_over_reason}")
    if st.button("Tekrar Oyna"):
        st.session_state.clear()
        st.rerun()