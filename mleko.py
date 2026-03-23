import streamlit as st
import pandas as pd
import datetime
import json
import os

# --- KONFIGURACJA STRONY ---
st.set_page_config(page_title="Radar Kadrowy - Kontrola Nieobecności", layout="wide")

# --- PLIKI BAZY DANYCH ---
PLIK_PRACOWNICY = "dane_pracownicy.json"
PLIK_NIEOBECNOSCI = "dane_nieobecnosci.json"

def wczytaj_dane(plik):
    if os.path.exists(plik):
        try:
            with open(plik, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def zapisz_dane(plik, dane):
    with open(plik, "w", encoding="utf-8") as f:
        json.dump(dane, f, ensure_ascii=False, indent=4)

if 'pracownicy' not in st.session_state:
    st.session_state.pracownicy = wczytaj_dane(PLIK_PRACOWNICY)
if 'nieobecnosci' not in st.session_state:
    st.session_state.nieobecnosci = wczytaj_dane(PLIK_NIEOBECNOSCI)

# --- STYLIZACJA ---
st.markdown("""
    <style>
        .l4-box { background-color: #ffebee; border: 1px solid #ffcdd2; border-radius: 8px; padding: 10px; color: #b71c1c; font-weight: bold; margin-bottom: 5px;}
        .urlop-box { background-color: #e3f2fd; border: 1px solid #bbdefb; border-radius: 8px; padding: 10px; color: #1565c0; font-weight: bold; margin-bottom: 5px;}
        .uz-box { background-color: #fff3e0; border: 1px solid #ffcc80; border-radius: 8px; padding: 10px; color: #e65100; font-weight: bold; margin-bottom: 5px;}
    </style>
""", unsafe_allow_html=True)

# --- ZAKŁADKI ---
tab1, tab2, tab3 = st.tabs(["🚨 Kto dzisiaj nie pracuje?", "📅 Zgłoś Nieobecność", "👥 Baza Pracowników i Limity"])

# ==========================================
# ZAKŁADKA 1: PULPIT (KTO NIE PRACUJE)
# ==========================================
with tab1:
    st.title("🚨 Stan Osobowy na Dziś")
    dzisiaj = datetime.date.today()
    st.subheader(f"Data: {dzisiaj.strftime('%d.%m.%Y')}")
    
    if not st.session_state.nieobecnosci:
        st.success("Wszyscy w pracy! Brak zarejestrowanych nieobecności na ten moment.")
    else:
        braki_dzisiaj = []
        for n in st.session_state.nieobecnosci:
            data_od = datetime.datetime.strptime(n['Data_od'], "%Y-%m-%d").date()
            data_do = datetime.datetime.strptime(n['Data_do'], "%Y-%m-%d").date()
            if data_od <= dzisiaj <= data_do:
                braki_dzisiaj.append(n)
                
        if not braki_dzisiaj:
            st.success("✅ Komplet załogi! Nikt z zapisanych nie jest dziś na urlopie ani L4.")
        else:
            col_ser, col_apar, col_konf = st.columns(3)
            
            with col_ser: st.markdown("### 🧀 Serownia")
            with col_apar: st.markdown("### 🥛 Aparatownia")
            with col_konf: st.markdown("### 📦 Konfekcja / Magazyn")
            
            for n in braki_dzisiaj:
                # Szukamy działu pracownika
                dzial = "Inne"
                for p in st.session_state.pracownicy:
                    if p['Imie_Nazwisko'] == n['Pracownik']:
                        dzial = p['Dzial']
                        break
                
                # Formatowanie kafelka w zależności od typu
                if n['Typ'] == "L4 (Chorobowe)":
                    klasa = "l4-box"
                    ikona = "🤒"
                elif n['Typ'] in ["Urlop na żądanie (UŻ)", "Nieobecność nieusprawiedliwiona"]:
                    klasa = "uz-box"
                    ikona = "⚠️"
                else:
                    klasa = "urlop-box"
                    ikona = "🌴"
                    
                kafelek = f"<div class='{klasa}'>{ikona} {n['Pracownik']}<br><small>{n['Typ']} (do {n['Data_do']})</small></div>"
                
                if dzial == "Serownia":
                    with col_ser: st.markdown(kafelek, unsafe_allow_html=True)
                elif dzial == "Aparatownia":
                    with col_apar: st.markdown(kafelek, unsafe_allow_html=True)
                else:
                    with col_konf: st.markdown(kafelek, unsafe_allow_html=True)

# ==========================================
# ZAKŁADKA 2: REJESTRACJA NIEOBECNOŚCI
# ==========================================
with tab2:
    st.title("📅 Rejestracja Urlopów i Zwolnień")
    
    if not st.session_state.pracownicy:
        st.warning("Najpierw dodaj pracowników w zakładce 'Baza Pracowników'!")
    else:
        lista_pracownikow = [p['Imie_Nazwisko'] for p in st.session_state.pracownicy]
        
        with st.form("form_nieobecnosc", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                pracownik = st.selectbox("Pracownik", lista_pracownikow)
                typ_nieobecnosci = st.selectbox("Rodzaj nieobecności", [
                    "Urlop wypoczynkowy", 
                    "L4 (Chorobowe)", 
                    "Urlop na żądanie (UŻ)", 
                    "Urlop okolicznościowy", 
                    "Opieka nad dzieckiem",
                    "Nieobecność nieusprawiedliwiona"
                ])
                uwagi = st.text_input("Komentarz / Uwagi (opcjonalnie)")
                
            with col2:
                data_od = st.date_input("Od kiedy?", datetime.date.today())
                data_do = st.date_input("Do kiedy (włącznie)?", datetime.date.today())
                
                # Ręczne wpisanie ilości dni (bo produkcja często pracuje w weekendy/brygady)
                dni_do_sciagniecia = st.number_input("Ile DNI ROBOCZYCH ściągnąć z puli?", min_value=0, value=1, step=1, help="Ważne dla brygadówki! Jeśli pracownik miał mieć 2 dni pracujące w trakcie 7 dni L4, wpisz 2.")
                
            zapisz_urlop = st.form_submit_button("Zatwierdź nieobecność", type="primary")
            
            if zapisz_urlop:
                if data_do < data_od:
                    st.error("Data zakończenia nie może być wcześniejsza niż data rozpoczęcia!")
                else:
                    nowa_nieob = {
                        "Pracownik": pracownik,
                        "Typ": typ_nieobecnosci,
                        "Data_od": data_od.strftime("%Y-%m-%d"),
                        "Data_do": data_do.strftime("%Y-%m-%d"),
                        "Dni_robocze": dni_do_sciagniecia,
                        "Uwagi": uwagi
                    }
                    st.session_state.nieobecnosci.append(nowa_nieob)
                    zapisz_dane(PLIK_NIEOBECNOSCI, st.session_state.nieobecnosci)
                    st.success(f"Dodano nieobecność dla {pracownik}!")
                    st.rerun()

# ==========================================
# ZAKŁADKA 3: BAZA PRACOWNIKÓW
# ==========================================
with tab3:
    st.title("👥 Twój Zespół i Limity Urlopowe")
    
    with st.expander("➕ Dodaj nowego pracownika", expanded=False):
        with st.form("form_pracownik", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            with c1: imie_nazw = st.text_input("Imię i Nazwisko")
            with c2: dzial = st.selectbox("Dział / Obszar", ["Serownia", "Aparatownia", "Konfekcja", "Magazyn", "Inne"])
            with c3: pula_urlopu = st.number_input("Roczna pula urlopu (dni)", min_value=0, value=26, step=1)
            
            if st.form_submit_button("Dodaj do zespołu"):
                if imie_nazw != "":
                    st.session_state.pracownicy.append({
                        "Imie_Nazwisko": imie_nazw,
                        "Dzial": dzial,
                        "Pula_roczna": pula_urlopu
                    })
                    zapisz_dane(PLIK_PRACOWNICY, st.session_state.pracownicy)
                    st.success(f"Dodano pracownika: {imie_nazw}")
                    st.rerun()
                else:
                    st.error("Podaj imię i nazwisko!")

    if st.session_state.pracownicy:
        # Obliczanie wykorzystanego urlopu
        raport_kadrowy = []
        for p in st.session_state.pracownicy:
            wykorzystany_urlop = 0
            for n in st.session_state.nieobecnosci:
                if n['Pracownik'] == p['Imie_Nazwisko'] and n['Typ'] in ["Urlop wypoczynkowy", "Urlop na żądanie (UŻ)"]:
                    wykorzystany_urlop += n['Dni_robocze']
            
            pozostalo = p['Pula_roczna'] - wykorzystany_urlop
            
            raport_kadrowy.append({
                "Pracownik": p['Imie_Nazwisko'],
                "Dział": p['Dzial'],
                "Pula roczna": p['Pula_roczna'],
                "Wykorzystany Urlop": wykorzystany_urlop,
                "POZOSTAŁO DO WYKORZYSTANIA": pozostalo
            })
            
        df_kadry = pd.DataFrame(raport_kadrowy)
        
        # Kolorowanie na czerwono, jeśli mało urlopu
        def styl_urlop(val):
            if isinstance(val, int) and val <= 5:
                return 'background-color: #ffebee; color: #b71c1c; font-weight:bold;'
            elif isinstance(val, int) and val > 15:
                return 'background-color: #e8f5e9; color: #2e7d32;'
            return ''
            
        st.markdown("### Stan Urlopów Wypoczynkowych")
        st.dataframe(df_kadry.style.map(styl_urlop, subset=['POZOSTAŁO DO WYKORZYSTANIA']), use_container_width=True, hide_index=True)
        
        st.divider()
        st.markdown("### 📋 Historia wszystkich nieobecności")
        if st.session_state.nieobecnosci:
            df_nieob = pd.DataFrame(st.session_state.nieobecnosci)
            df_nieob = df_nieob.sort_values(by="Data_od", ascending=False)
            st.dataframe(df_nieob, use_container_width=True, hide_index=True)
            
            # Przycisk czyszczenia
            if st.button("🗑️ Wyczyść historię nieobecności"):
                st.session_state.nieobecnosci = []
                zapisz_dane(PLIK_NIEOBECNOSCI, [])
                st.rerun()
    else:
        st.info("Brak pracowników. Dodaj pierwszą osobę z zespołu powyżej.")
