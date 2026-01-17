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

# --- 1. AKILLI ANAHTAR SEÇİMİ VE RETRY MEKANİZMASI ---
def get_response_with_retry(prompt_parts, max_retries=10):
    """
    Hata alırsa başka anahtara geçip tekrar dener.
    Bu fonksiyon '429 Kota' hatasını kullanıcıya göstermez,
    arkada sessizce yeni anahtarla sorunu çözer.
    """
    
    if "GOOGLE_API_KEYS" not in st.secrets:
        st.error("HATA: Secrets dosyasında GOOGLE_API_KEYS bulunamadı!")
        return None

    key_list = st.secrets["GOOGLE_API_KEYS"]
    
    # 10 kereye kadar farklı anahtarlarla deneme hakkı veriyoruz
    for attempt in range(max_retries):
        try:
            # 1. Rastgele bir anahtar seç
            active_key = random.choice(key_list)
            genai.configure(api_key=active_key)
            
            # 2. Modeli Seç (Listende gördüğümüz çalışan model)
            # gemini-2.0-flash şu an senin için en uygunu
            model = genai.GenerativeModel('gemini-2.0-flash')
            
            # 3. İsteği Gönder
            response = model.generate_content(prompt_parts)
            
            # 4. Cevabı JSON'a çevir ve döndür
            text = response.text
            text = text.replace("```json", "").replace("```", "").strip()
            return json.loads(text)
            
        except Exception as e:
            # Eğer hata '429' (Kota) ise veya başka bir sunucu hatasıysa:
            # Kullanıcıya hissettirmeden döngünün başına dön ve yeni anahtar seç.
            # Sadece geliştirici konsoluna (loglara) not düşelim.
            print(f"Deneme {attempt+1} başarısız (Anahtar sonu ...{active_key[-5:]}): {e}")
            time.sleep(1) # Sunucuyu boğmamak için 1 saniye bekle
            continue
    
    # Eğer 10 denemede de hepsi hata verirse:
    st.error("⚠️ Sistem şu an çok yoğun. Lütfen 1-2 dakika bekleyip tekrar deneyin.")
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
    
    # Sohbet geçmişini hazırla
    chat_history = [{"role": "user", "parts": [system_prompt]}]
    for msg in st.session_state.history:
        chat_history.append(msg)
    chat_history.append({"role": "user", "parts": [user_input]})

    # Yeni yazdığımız "Retry" özellikli fonksiyonu çağır
    return get_response_with_retry(chat_history)

# --- 4. ARAYÜZ (UI) ---

st.title("🚀 Startup Survivor")
st.caption(f"🟢 Sistem Aktif | Gemini 2.0 Flash | 30 Key Auto-Retry Modu")
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
        with st.spinner("Yatırımcılar ve Analistler toplanıyor... (Sabırlı olun, en uygun sunucu aranıyor)"):
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