import streamlit as st
import pandas as pd

# --- KONFIGURACJA STRONY ---
st.set_page_config(page_title="Tygodniowy Planista Mleka", layout="wide")

# --- DANE ZUŻYCIA (LITRY NA 1 WAR) ---
ZUZYCIE_WAR = {
    "Cheddar": {
        "40": 237000 / 19,
        "50": 227000 / 19
    },
    "Bertsch": {
        "30": 198000 / 15,
        "45": 184000 / 15,
        "50": 163000 / 15
    },
    "Mozzarella": {
        "Standard": 196000 / 18
    }
}

# --- LIMITY BEZPIECZEŃSTWA ---
CEL_ZAPASU_MAX = 0         # Nie chcemy mleka na plusie
CEL_ZAPASU_MIN = -100000   # Maksymalny dopuszczalny minus to -100 tys. litrów

st.title("🥛 Tygodniowy Planista Zużycia Mleka")

# --- PANEL BOCZNY (USTAWIENIA GLOBALNE) ---
with st.sidebar:
    st.header("⚙️ Start Tygodnia")
    zapas_start = st.number_input("Zapas w Poniedziałek rano (L):", value=50000, step=1000)
    
    st.markdown("---")
    st.markdown("""
    **Legenda statusów:**
    * 🟢 **OK** (od 0 do -100 tys.) - bezpieczny zapas na awarię.
    * 🟠 **NADWYŻKA** (> 0) - Odpal dodatkową linię lub zwiększ warki!
    * 🔴 **BRAK MLEKA** (< -100 tys.) - Zbyt duża produkcja, zdejmij warki!
    """)

dni_tygodnia = ["Poniedziałek", "Wtorek", "Środa", "Czwartek", "Piątek", "Sobota", "Niedziela"]

# Zmienna przechowująca zapas "przechodzący" z dnia na dzień
zapas_obecny = zapas_start
raport_tygodniowy = []

# --- PĘTLA PO DNIACH TYGODNIA ---
for i, dzien in enumerate(dni_tygodnia):
    # Domyślnie rozwijamy tylko Poniedziałek, resztę można kliknąć
    with st.expander(f"📅 {dzien} (Zapas startowy: {int(zapas_obecny):,} L)".replace(",", " "), expanded=(i==0)):
        
        st.markdown("#### 📥 Podaż mleka")
        c1, c2, c3 = st.columns(3)
        dostawy = c1.number_input("Dostawy mleka (L):", value=600000, step=1000, key=f"dost_{i}")
        smietanka = c2.number_input("Odbiór Śmietanki (L):", value=0, step=1000, key=f"smiet_{i}")
        bel = c3.number_input("Odbiór Bel (L):", value=0, step=1000, key=f"bel_{i}")
        
        mleko_dostepne = zapas_obecny + dostawy - smietanka - bel

        st.markdown("#### 🧀 Wybór aktywnych linii i warów")
        p1, p2, p3 = st.columns(3)
        
        # CHEDDAR
        with p1:
            ch_on = st.checkbox("🧀 Linia Cheddar", value=True, key=f"ch_on_{i}")
            if ch_on:
                ch_typ = st.selectbox("Wariant Cheddar:", ["40", "50"], key=f"ch_typ_{i}")
                ch_wary = st.number_input("Ilość warów (Cheddar):", min_value=0, value=19, key=f"ch_w_{i}")
                zuzycie_ch = ch_wary * ZUZYCIE_WAR["Cheddar"][ch_typ]
            else:
                zuzycie_ch = 0
                
        # BERTSCH
        with p2:
            be_on = st.checkbox("🧀 Linia Bertsch", value=True, key=f"be_on_{i}")
            if be_on:
                be_typ = st.selectbox("Wariant Bertsch:", ["30", "45", "50"], key=f"be_typ_{i}")
                be_wary = st.number_input("Ilość warów (Bertsch):", min_value=0, value=15, key=f"be_w_{i}")
                zuzycie_be = be_wary * ZUZYCIE_WAR["Bertsch"][be_typ]
            else:
                zuzycie_be = 0

        # MOZZARELLA
        with p3:
            mo_on = st.checkbox("🧀 Linia Mozzarella", value=True, key=f"mo_on_{i}")
            if mo_on:
                # Mozzarella ma tylko jeden wariant z podanych danych (Standard)
                mo_wary = st.number_input("Ilość warów (Mozzarella):", min_value=0, value=18, key=f"mo_w_{i}")
                zuzycie_mo = mo_wary * ZUZYCIE_WAR["Mozzarella"]["Standard"]
            else:
                zuzycie_mo = 0

        # OBLICZENIA DZIENNE
        zuzycie_dzis = zuzycie_ch + zuzycie_be + zuzycie_mo
        zapas_koncowy = mleko_dostepne - zuzycie_dzis

        # STATUS ZAPASU
        if zapas_koncowy > CEL_ZAPASU_MAX:
            status = "🟠 NADWYŻKA (Zwiększ produkcję)"
            color = "#e65100"
        elif zapas_koncowy < CEL_ZAPASU_MIN:
            status = "🔴 BRAK MLEKA (Zmniejsz produkcję)"
            color = "#b71c1c"
        else:
            status = "🟢 IDEALNIE (Bezpieczny minus)"
            color = "#2e7d32"

        st.markdown(f"""
            <div style="background-color:#f8f9fa; padding:10px; border-radius:5px; border-left: 5px solid {color}; margin-top:15px;">
                <span style="font-size:16px;">Zużycie całkowite w tym dniu: <b>{int(zuzycie_dzis):,} L</b></span><br>
                <span style="font-size:18px;">Przewidywany zapas na jutro: <b style="color:{color};">{int(zapas_koncowy):,} L</b> ({status})</span>
            </div>
        """.replace(",", " "), unsafe_allow_html=True)

        # DODAWANIE DO RAPORTU
        raport_tygodniowy.append({
            "Dzień": dzien,
            "Zapas rano (L)": f"{int(zapas_obecny):,}".replace(",", " "),
            "Dostawy Netto (L)": f"{int(dostawy - smietanka - bel):,}".replace(",", " "),
            "Aktywne Linie": f"{'Ch ' if ch_on else ''}{'Be ' if be_on else ''}{'Mo' if mo_on else ''}",
            "Zużycie łączne (L)": f"{int(zuzycie_dzis):,}".replace(",", " "),
            "Zapas końcowy (L)": int(zapas_koncowy), # Int dla formatowania Pandas
            "Status": status
        })

        # Przeniesienie zapasu na kolejny dzień
        zapas_obecny = zapas_koncowy

# --- TABELA PODSUMOWUJĄCA CAŁY TYDZIEŃ ---
st.divider()
st.subheader("📊 Tygodniowe podsumowanie zapasów mleka")

df_raport = pd.DataFrame(raport_tygodniowy)

# Funkcja kolorująca wiersze w tabeli na podstawie statusu
def style_status(val):
    if "NADWYŻKA" in val:
        return 'background-color: #fff3e0; color: #e65100; font-weight: bold;'
    elif "BRAK" in val:
        return 'background-color: #ffebee; color: #b71c1c; font-weight: bold;'
    elif "IDEALNIE" in val:
        return 'background-color: #e8f5e9; color: #2e7d32; font-weight: bold;'
    return ''

# Formatowanie zapasu końcowego do wyświetlenia z odstępami
df_raport['Zapas końcowy (L)'] = df_raport['Zapas końcowy (L)'].apply(lambda x: f"{x:,}".replace(",", " "))

st.dataframe(df_raport.style.applymap(style_status, subset=['Status']), use_container_width=True, hide_index=True)
