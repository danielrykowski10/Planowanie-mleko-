import streamlit as st
import os

# --- KONFIGURACJA STRONY ---
st.set_page_config(page_title="MR Therapy | Twoja Podróż", page_icon="🌿", layout="wide")

# --- ZARZĄDZANIE STANEM (KROKI APLIKACJI) ---
if 'krok' not in st.session_state:
    st.session_state.krok = 0
if 'wybrany_problem' not in st.session_state:
    st.session_state.wybrany_problem = ""

def idz_do_kroku(k):
    st.session_state.krok = k

# --- BAZA WIEDZY I ZABIEGÓW ---
PROBLEMY = {
    "Opadający owal twarzy i brak jędrności": {
        "diagnoza": "Z wiekiem, ale też przez złą postawę (tzw. 'wdowi garb' czy pochylanie się nad telefonem), tkanki tracą podparcie. Powięzi na dekolcie i szyi skracają się, ciągnąc Twoją twarz w dół, tworząc tzw. 'chomiki'.",
        "terapia": "👐 Facemodeling & Kobido",
        "opis_terapii": "Nie potrzebujesz wypełniaczy. Poprzez głęboki masaż powięziowy i lifting japoński, uwolnimy napięcia klatki piersiowej i szyi, przywracając tkankom naturalne rusztowanie i unosząc owal Twojej twarzy.",
        "ikona": "💆‍♀️"
    },
    "Zaciśnięta żuchwa, zgrzytanie zębami (Bruksizm)": {
        "diagnoza": "Stres zapisuje się w ciele, a żwacze to najsilniejsze mięśnie, które biorą na siebie ciężar Twoich nerwów. Zaciskanie zębów powoduje nie tylko ból głowy, ale też 'kwadratowy' i ciężki wygląd twarzy.",
        "terapia": "🌿 Facemodeling (Terapia Transbukalna)",
        "opis_terapii": "Zastosujemy masaż wewnątrz ust (transbukalny). Brzmi nietypowo, ale to jedyna metoda, by dotrzeć do spiętych mięśni żwaczy i skrzydłowych. Rozluźnimy je, co natychmiast wysmukli Twoje rysy i przyniesie ulgę w bólu.",
        "ikona": "🦷"
    },
    "Ciężka głowa, stres i przebodźcowanie": {
        "diagnoza": "Ciągły pośpiech, ekrany i brak oddechu sprawiają, że Twój układ nerwowy jest na skraju wyczerpania. Spięty czepiec ścięgnisty (skóra głowy) blokuje krążenie, powodując napięciowe bóle.",
        "terapia": "💆‍♀️ Head Spa & Relaksacja",
        "opis_terapii": "Zanurzysz się w głębokim relaksie. Poprzez stymulację punktów akupresurowych na głowie, masaż karku i ciepło, zrestartujemy Twój układ nerwowy. Wyjdziesz wyciszona, z lekką głową i lśniącymi włosami.",
        "ikona": "🧘‍♀️"
    },
    "Szara cera, opuchlizna, zmęczone oczy": {
        "diagnoza": "Kiedy limfa nie krąży prawidłowo, woda i toksyny zatrzymują się w tkankach. Budzisz się z opuchniętymi oczami ('worki'), a skóra jest niedotleniona i pozbawiona blasku.",
        "terapia": "🌸 Drenaż Limfatyczny & Kobido",
        "opis_terapii": "Dzięki delikatnym, pompującym ruchom drenażu, odprowadzimy zalegającą limfę. Następnie intensywne techniki Kobido dotlenią każdą komórkę Twojej skóry, dając natychmiastowy efekt 'Glow'.",
        "ikona": "✨"
    }
}

# Foldery na wgrane przez terapeutkę pliki
BAZA_MEDIA = "media_terapia"
os.makedirs(BAZA_MEDIA, exist_ok=True)
for p in PROBLEMY.keys():
    safe_name = "".join([c if c.isalnum() else "_" for c in p])
    os.makedirs(os.path.join(BAZA_MEDIA, safe_name), exist_ok=True)

# --- ESTETYKA (CSS) ---
st.markdown("""
    <style>
        /* Tło całej aplikacji na delikatny, zgaszony beż (jak na IG) */
        .stApp {
            background-color: #FDFBF7;
        }
        /* Kontener udający ekran telefonu */
        .mobile-container {
            background-color: #ffffff;
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0px 10px 30px rgba(139, 115, 85, 0.1);
            text-align: center;
        }
        .main-title { color: #5C4D43; font-family: 'Georgia', serif; font-size: 32px; font-weight: normal; margin-bottom: 5px; text-align: center;}
        .sub-title { color: #8B7355; font-size: 16px; font-style: italic; margin-bottom: 30px; text-align: center;}
        
        /* Przyciski jako eleganckie kafle */
        .stButton>button {
            width: 100%;
            border-radius: 12px;
            background-color: #F4EFEB;
            color: #5C4D43;
            border: 1px solid #E6DCD3;
            padding: 15px 10px;
            font-size: 16px;
            transition: all 0.3s ease;
        }
        .stButton>button:hover {
            background-color: #E6DCD3;
            border-color: #8B7355;
            color: #5C4D43;
        }
        
        .diagnoza-box { background-color: #FDFBF7; border-left: 4px solid #D4C4B7; padding: 15px; text-align: left; color: #5C4D43; font-size: 15px; margin-bottom:20px; }
        .terapia-box { background-color: #F4EFEB; border-radius: 10px; padding: 20px; text-align: center; color: #5C4D43;}
        .terapia-nazwa { font-family: 'Georgia', serif; font-size: 22px; font-weight: bold; color: #8B7355; margin-bottom: 10px;}
    </style>
""", unsafe_allow_html=True)


# --- STRUKTURA APLIKACJI (Kolumny tworzące "smartfon" na środku ekranu) ---
spacer_left, mobile_col, spacer_right = st.columns([1, 1.5, 1])

with mobile_col:
    # EKRAN 0: POWITANIE
    if st.session_state.krok == 0:
        st.markdown("<div class='mobile-container'>", unsafe_allow_html=True)
        st.markdown("<div class='main-title'>MR Therapy</div>", unsafe_allow_html=True)
        st.markdown("<div class='sub-title'>Odkryj piękno płynące z głębi ciała</div>", unsafe_allow_html=True)
        
        st.image("https://images.unsplash.com/photo-1600334089648-b0d9d3028eb2?q=80&w=800&auto=format&fit=crop", use_container_width=True)
        st.markdown("<br><p style='color:#5C4D43; text-align:center;'>Twoja twarz to mapa emocji i napięć.<br>Zanim dobierzemy terapię, powiedz mi, czego dzisiaj potrzebujesz najbardziej?</p><br>", unsafe_allow_html=True)
        
        if st.button("Rozpocznij diagnozę ✨"):
            idz_do_kroku(1)
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    # EKRAN 1: WYBÓR PROBLEMU
    elif st.session_state.krok == 1:
        st.markdown("<div class='mobile-container'>", unsafe_allow_html=True)
        st.markdown("<div class='main-title'>Z czym do mnie przychodzisz?</div>", unsafe_allow_html=True)
        st.markdown("<div class='sub-title'>Wybierz obszar, który sprawia Ci dyskomfort.</div>", unsafe_allow_html=True)
        
        for problem in PROBLEMY.keys():
            if st.button(f"{PROBLEMY[problem]['ikona']} {problem}"):
                st.session_state.wybrany_problem = problem
                idz_do_kroku(2)
                st.rerun()
                
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("⬅ Wróć do początku"):
            idz_do_kroku(0)
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    # EKRAN 2: EDUKACJA I ROZWIĄZANIE
    elif st.session_state.krok == 2:
        prob = st.session_state.wybrany_problem
        dane = PROBLEMY[prob]
        
        st.markdown("<div class='mobile-container'>", unsafe_allow_html=True)
        st.markdown(f"<div class='main-title'>{dane['ikona']} Zrozum swoje ciało</div>", unsafe_allow_html=True)
        
        st.markdown("### Dlaczego tak się dzieje?")
        st.markdown(f"<div class='diagnoza-box'><i>{dane['diagnoza']}</i></div>", unsafe_allow_html=True)
        
        st.markdown("### Moja odpowiedź na Twój problem:")
        st.markdown(f"""
            <div class='terapia-box'>
                <div class='terapia-nazwa'>{dane['terapia']}</div>
                <p style='font-size: 15px;'>{dane['opis_terapii']}</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Zobacz metamorfozy i efekty 📸"):
            idz_do_kroku(3)
            st.rerun()
            
        if st.button("⬅ Wybierz inny problem"):
            idz_do_kroku(1)
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    # EKRAN 3: MEDIA (PRZED/PO) I KONTAKT
    elif st.session_state.krok == 3:
        prob = st.session_state.wybrany_problem
        st.markdown("<div class='mobile-container'>", unsafe_allow_html=True)
        st.markdown(f"<div class='main-title'>Efekty Terapii</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='sub-title'>{PROBLEMY[prob]['terapia']}</div>", unsafe_allow_html=True)
        
        # Ładowanie zdjęć/wideo dla wybranego problemu
        safe_name = "".join([c if c.isalnum() else "_" for c in prob])
        folder_path = os.path.join(BAZA_MEDIA, safe_name)
        pliki = os.listdir(folder_path) if os.path.exists(folder_path) else []
        
        if not pliki:
            st.info("Tutaj pojawią się zdjęcia moich wspaniałych klientek przed i po terapii oraz instrukcje wideo automasażu.")
        else:
            for plik in pliki:
                sciezka = os.path.join(folder_path, plik)
                if plik.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                    st.image(sciezka, use_container_width=True, caption="Efekt po sesji")
                elif plik.lower().endswith(('.mp4', '.mov')):
                    st.video(sciezka)
        
        st.markdown("<br><hr style='border-top: 1px solid #E6DCD3;'><br>", unsafe_allow_html=True)
        st.markdown("### Zadbaj o siebie już dziś")
        st.markdown("<p style='color:#5C4D43;'>Twoje ciało zasługuje na uwolnienie. Zarezerwuj swój czas na regenerację.</p>", unsafe_allow_html=True)
        
        # Symulacja przycisku do Booksy / DM na Instagramie
        st.markdown(f"<a href='https://www.instagram.com/mr__therapy_/' target='_blank' style='display:block; text-align:center; background-color:#8B7355; color:white; padding:15px; border-radius:12px; text-decoration:none; font-weight:bold; font-size:18px;'>Napisz do mnie na IG i umów wizytę</a>", unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("⬅ Zacznij od początku"):
            idz_do_kroku(0)
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)


# --- UKRYTY PANEL TERAPEUTY (Wgrywanie plików na bocznym pasku) ---
with st.sidebar:
    st.markdown("### 🛠️ Panel Właściciela (Ukryty)")
    st.markdown("Dodaj tutaj materiały wideo i zdjęcia Przed/Po, które zobaczą klientki w Kroku 3.")
    
    with st.form("upload_beauty_form", clear_on_submit=True):
        cel_problem = st.selectbox("Przypisz media do:", list(PROBLEMY.keys()))
        pliki_upload = st.file_uploader("Wgraj zdjęcia/wideo", type=["jpg", "jpeg", "png", "mp4", "mov"], accept_multiple_files=True)
        
        if st.form_submit_button("Wgraj na serwer"):
            if pliki_upload:
                safe_name = "".join([c if c.isalnum() else "_" for c in cel_problem])
                folder_path = os.path.join(BAZA_MEDIA, safe_name)
                for f in pliki_upload:
                    with open(os.path.join(folder_path, f.name), "wb") as f_out:
                        f_out.write(f.getbuffer())
                st.success("Materiały dodane! Klientki już je widzą.")
                st.rerun()
