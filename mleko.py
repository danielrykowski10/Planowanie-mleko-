# --- DODAJ TO DO SIDEBARA ---
tryb = st.sidebar.radio("Wybierz sekcję:", ["Nauka (Dziecko)", "Gimnastyka Twarzy 💆‍♀️", "Panel Rodzica"])

# --- NOWA SEKCJA: GIMNASTYKA TWARZY ---
if tryb == "Gimnastyka Twarzy 💆‍♀️":
    st.title("💆‍♀️ Wyzwanie Pięknej Buzia")
    st.write("Wykonaj te ćwiczenia, aby Twoja buzia była rozluźniona i zdrowa!")

    cwiczenia = [
        {"nazwa": "Balonik 🎈", "opis": "Nadmij mocno policzki i trzymaj powietrze przez 5 sekund!"},
        {"nazwa": "Ziewający Lew 🦁", "opis": "Otwórz buzię bardzo szeroko i wystaw język najdalej jak potrafisz."},
        {"nazwa": "Rybka 🐠", "opis": "Wciągnij policzki do środka i spróbuj 'cmoknąć' jak rybka."},
        {"nazwa": "Wycieraczki 🚗", "opis": "Przesuwaj język wewnątrz buzi od jednego policzka do drugiego."}
    ]

    wybrane = random.choice(cwiczenia)
    
    st.info(f"### Dzisiejsze ćwiczenie: **{wybrane['nazwa']}**")
    st.write(wybrane['opis'])
    
    if st.button("Zrobione! ⭐"):
        st.balloons()
        st.success("Brawo! Twoje mięśnie twarzy Ci dziękują!")
        # Zapisujemy sukces do panelu rodzica
        st.session_state.historia.append({
            "Czas": datetime.now().strftime("%H:%M:%S"),
            "Przedmiot": "Terapia Manualna",
            "Zadanie": wybrane['nazwa'],
            "Twoja odpowiedź": "Wykonano",
            "Poprawna": "TAK"
        })
