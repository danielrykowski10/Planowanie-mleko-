import streamlit as st
import pandas as pd
import random
from datetime import datetime

# --- KONFIGURACJA STRONY ---
st.set_page_config(page_title="Akademia Odkrywcy", page_icon="🎓")

# --- INICJALIZACJA DANYCH (SESSION STATE) ---
if 'historia' not in st.session_state:
    st.session_state.historia = []
if 'zadanie' not in st.session_state:
    # Generujemy pierwsze zadanie
    a, b = random.randint(1, 20), random.randint(1, 20)
    st.session_state.zadanie = {"pytanie": f"{a} + {b}", "wynik": a + b}

# --- PASEK BOCZNY (NAWIGACJA) ---
st.sidebar.title("🚀 Menu")
tryb = st.sidebar.radio("Wybierz sekcję:", ["Nauka (Dziecko)", "Panel Rodzica"])

# --- SEKCJA DLA DZIECKA ---
if tryb == "Nauka (Dziecko)":
    st.title("🌟 Czas na wyzwanie!")
    st.subheader(f"Ile to jest: {st.session_state.zadanie['pytanie']}?")

    with st.form(key='quiz_form', clear_on_submit=True):
        odp = st.number_input("Wpisz wynik:", step=1, value=0)
        submit = st.form_submit_button("Sprawdź! ✅")

        if submit:
            poprawny = st.session_state.zadanie['wynik']
            if odp == poprawny:
                st.balloons()
                st.success("Genialnie! To poprawna odpowiedź!")
            else:
                st.error("Ojej, tym razem się nie udało. Spróbuj kolejnego!")
                # Zapisujemy błąd dla rodzica
                st.session_state.historia.append({
                    "Czas": datetime.now().strftime("%H:%M:%S"),
                    "Przedmiot": "Matematyka",
                    "Zadanie": st.session_state.zadanie['pytanie'],
                    "Twoja odpowiedź": odp,
                    "Poprawna": poprawny
                })
            
            # Losujemy nowe zadanie po kliknięciu
            a, b = random.randint(1, 20), random.randint(1, 20)
            st.session_state.zadanie = {"pytanie": f"{a} + {b}", "wynik": a + b}
            st.info("Nowe zadanie przygotowane powyżej!")

# --- PANEL RODZICA ---
else:
    st.title("🔑 Panel Rodzica")
    st.write("Tutaj możesz sprawdzić, z czym Twoje dziecko miało trudności.")

    if not st.session_state.historia:
        st.write("✅ Na razie brak błędów. Świetna robota!")
    else:
        df = pd.DataFrame(st.session_state.historia)
        st.dataframe(df, use_container_width=True)
        
        # Prosty wykres błędów
        st.subheader("Analiza trudności")
        st.bar_chart(df['Zadanie'].value_counts())
        
        if st.button("Wyczyść historię"):
            st.session_state.historia = []
            st.rerun()
