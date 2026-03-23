import streamlit as st
import os

# --- KONFIGURACJA STRONY ---
st.set_page_config(page_title="Holistyczne Piękno | Terapia Twarzy", page_icon="🌸", layout="wide")

# --- STYLIZACJA (Estetyka SPA / Beauty) ---
st.markdown("""
    <style>
        .spa-title { color: #8a6a5c; font-family: 'Georgia', serif; text-align: center; font-size: 40px; font-weight: normal; margin-bottom: 10px; }
        .spa-subtitle { color: #a98d80; text-align: center; font-size: 20px; font-style: italic; margin-bottom: 40px; }
        .concept-box { background-color: #fdfaf6; border-left: 5px solid #d4c1b3; padding: 20px; margin-bottom: 20px; border-radius: 5px; color: #5a4a42; }
        .treatment-box { background-color: #f9f5f0; border: 1px solid #eaddd5; border-radius: 10px; padding: 20px; text-align: center; box-shadow: 2px 2px 15px rgba(0,0,0,0.05); height: 100%;}
        .problem-title { color: #8a6a5c; font-size: 24px; font-family: 'Georgia', serif; border-bottom: 1px solid #eaddd5; padding-bottom: 10px; margin-bottom: 15px;}
        h1, h2, h3 { color: #8a6a5c; font-family: 'Georgia', serif; }
    </style>
""", unsafe_allow_html=True)

# --- BAZA PROBLEMÓW I KATALOGI NA PLIKI ---
PROBLEMY = {
    "Opadający owal twarzy (tzw. chomiki)": {
        "opis": "Z wiekiem i pod wpływem grawitacji tkanki opadają. Często winne są też napięcia w obrębie dekoltu i szyi, które 'ciągną' twarz w dół.",
        "terapia": "Facemodeling i Kobido świetnie unoszą owal, pracując na głębokich strukturach mięśniowych i powięziowych, przywracając tkankom elastyczność."
    },
    "Bruksizm / Napięta żuchwa": {
        "opis": "Zaciskanie zębów w nocy to reakcja na stres. Powoduje to przerost mięśni żwaczy (twarz staje się kwadratowa) i silne bóle głowy.",
        "terapia": "Masaż transbukalny (wewnątrz ust) w ramach Facemodelingu idealnie rozluźnia żwacze, przynosząc natychmiastową ulgę i wysmuklając rysy."
    },
    "Lwia zmarszczka i napięte czoło": {
        "opis": "To nie tylko problem skóry, ale przede wszystkim spiętego mięśnia marszczącego brwi i czepca ścięgnistego na głowie.",
        "terapia": "Połączenie Head Spa (rozluźnienie głowy) i głębokich technik liftingujących rozprostowuje czoło w sposób naturalny, bez blokowania mimiki."
    },
    "Szara, zmęczona cera i obrzęki": {
        "opis": "Zastoje limfatyczne sprawiają, że twarz jest opuchnięta (szczególnie rano), a skóra niedotleniona.",
        "terapia": "Kobido i drenaż limfatyczny przyspieszają krążenie krwi i limfy. Skóra odzyskuje naturalny 'glow', a opuchlizna znika."
    },
    "Przemęczenie i stres (Potrzeba głębokiego relaksu)": {
        "opis": "Przebodźcowanie układu nerwowego odbija się na naszym wyglądzie i samopoczuciu.",
        "terapia": "Head Spa to rytuał, który przez masaż głowy, karku i aromaterapię głęboko resetuje układ nerwowy."
    }
}

# Tworzenie folderów na zdjęcia/filmy dla każdego problemu
BAZA_MEDIA = "media_spa"
os.makedirs(BAZA_MEDIA, exist_ok=True)
for p in PROBLEMY.keys():
    # Zamieniamy spacje i znaki specjalne na bezpieczne nazwy folderów
    safe_name = "".join([c if c.isalnum() else "_" for c in p])
    os.makedirs(os.path.join(BAZA_MEDIA, safe_name), exist_ok=True)

# --- STRUKTURA APLIKACJI ---
st.markdown("<div class='spa-title'>Naturalne Odmładzanie i Terapia</div>", unsafe_allow_html=True)
st.markdown("<div class='spa-subtitle'>Odkryj potęgę dotyku, która uzdrawia ciało i wycisza umysł.</div>", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["🌿 Dlaczego Terapia Manualna?", "🔍 Znajdź Swój Problem", "📸 Panel Terapeuty (Dodaj Media)"])

# ==========================================
# ZAKŁADKA 1: EDUKACJA (DLA KLIENTKI)
# ==========================================
with tab1:
    c1, c2 = st.columns([1, 1])
    with c1:
        st.markdown("""
            <div class='concept-box'>
                <h3>Czym jest Terapia Manualna Twarzy?</h3>
                <p>To znacznie więcej niż zwykły masaż relaksacyjny. To głęboka praca na <b>mięśniach, powięziach i kościach twarzoczaszki</b>.</p>
                <p>Medycyna estetyczna często jedynie "maskuje" problem (np. wypełniając zmarszczkę kwasem lub blokując mięsień botoksem). My szukamy <b>przyczyny</b>. Zmarszczki i opadanie skóry to najczęściej efekt napięć w ciele, stresu, złej postawy czy zaciskania zębów.</p>
                <p>Przez odpowiednie techniki uwalniamy te napięcia, przywracając twarzy młodość, symetrię i blask w 100% naturalny sposób.</p>
            </div>
        """, unsafe_allow_html=True)
        
    with c2:
        st.markdown("### Poznaj nasze metody:")
        t_col1, t_col2, t_col3 = st.columns(3)
        with t_col1:
            st.markdown("<div class='treatment-box'><b>💆‍♀️ Masaż Kobido</b><br><br><small>Japoński lifting twarzy. Intensywny, szybki, dający niesamowity efekt uniesienia i odżywienia tkanek.</small></div>", unsafe_allow_html=True)
        with t_col2:
            st.markdown("<div class='treatment-box'><b>👐 Facemodeling</b><br><br><small>Multiterapia łącząca osteopatię, drenaż i masaż wnętrza ust. Modeluje i rzeźbi twarz od nowa.</small></div>", unsafe_allow_html=True)
        with t_col3:
            st.markdown("<div class='treatment-box'><b>🛀 Head Spa</b><br><br><small>Głęboki relaks, pielęgnacja skóry głowy i masaż karku. Uwalnia napięcia blokujące swobodny przepływ krwi do twarzy.</small></div>", unsafe_allow_html=True)

# ==========================================
# ZAKŁADKA 2: ROZWIĄŻ SWÓJ PROBLEM
# ==========================================
with tab2:
    st.markdown("### Co sprawia Ci największy dyskomfort?")
    wybrany_problem = st.selectbox("Wybierz obszar do pracy:", list(PROBLEMY.keys()))
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col_opis, col_media = st.columns([1, 1.5])
    
    with col_opis:
        st.markdown(f"<div class='problem-title'>{wybrany_problem}</div>", unsafe_allow_html=True)
        st.markdown(f"**Skąd to się bierze?**<br>{PROBLEMY[wybrany_problem]['opis']}", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.success(f"🌿 **Nasze rozwiązanie:**\n\n{PROBLEMY[wybrany_problem]['terapia']}")
        
    with col_media:
        st.markdown("### 📸 Metamorfozy i Porady Wideo")
        
        # Pobieranie plików z folderu odpowiadającego problemowi
        safe_name = "".join([c if c.isalnum() else "_" for c in wybrany_problem])
        folder_path = os.path.join(BAZA_MEDIA, safe_name)
        
        pliki = os.listdir(folder_path) if os.path.exists(folder_path) else []
        
        if not pliki:
            st.info("Brak wgranych materiałów dla tego problemu. Terapeuta może je dodać w zakładce 'Panel Terapeuty'.")
        else:
            # Tworzymy siatkę na zdjęcia/filmy
            grid_cols = st.columns(2)
            for idx, plik in enumerate(pliki):
                sciezka_pliku = os.path.join(folder_path, plik)
                with grid_cols[idx % 2]:
                    # Rozpoznawanie obrazu vs wideo po rozszerzeniu
                    if plik.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                        st.image(sciezka_pliku, use_container_width=True, caption=plik)
                    elif plik.lower().endswith(('.mp4', '.mov')):
                        st.video(sciezka_pliku)

# ==========================================
# ZAKŁADKA 3: PANEL TERAPEUTY (WGRYWANIE ZDJĘĆ/WIDEO)
# ==========================================
with tab3:
    st.markdown("### 🛠️ Zarządzanie Bazą Wiedzy i Metamorfozami")
    st.markdown("Wybierz problem i wgraj zdjęcia z telefonu lub komputera (np. efekty Przed/Po, filmy z ćwiczeniami automasażu).")
    
    with st.form("upload_form", clear_on_submit=True):
        problem_docelowy = st.selectbox("Przypisz materiał do problemu:", list(PROBLEMY.keys()))
        wgrane_pliki = st.file_uploader("Wybierz zdjęcia lub wideo", type=["jpg", "jpeg", "png", "mp4", "mov"], accept_multiple_files=True)
        
        submit_btn = st.form_submit_button("Wgraj materiały", type="primary")
        
        if submit_btn and wgrane_pliki:
            safe_name = "".join([c if c.isalnum() else "_" for c in problem_docelowy])
            folder_path = os.path.join(BAZA_MEDIA, safe_name)
            
            for f in wgrane_pliki:
                file_path = os.path.join(folder_path, f.name)
                with open(file_path, "wb") as f_out:
                    f_out.write(f.getbuffer())
                    
            st.success(f"Pomyślnie wgrano {len(wgrane_pliki)} plik(ów) do kategorii '{problem_docelowy}'!")
            st.rerun()

    st.divider()
    st.markdown("💡 *Wskazówka: Nagraj krótkie, 15-sekundowe wideo, jak poprawnie rozmasować sobie żwacze w domu, wgraj je tutaj, a Twoje klientki będą miały do tego dostęp po wejściu na stronę!*")
