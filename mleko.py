import streamlit as st

# --- KONFIGURACJA STRONY ---
st.set_page_config(page_title="Bilans Mleka - Serownie", layout="wide")

# --- DANE ZUŻYCIA (LITRY NA 1 WAR) ---
# Wyliczone na podstawie Twoich danych (całkowite zużycie / liczba warów)
ZUZYCIE_WAR = {
    "Cheddar": {
        "40": 237000 / 19,  # ok. 12473.68 l/war
        "50": 227000 / 19   # ok. 11947.37 l/war
    },
    "Bertsch": {
        "30": 198000 / 15,  # ok. 13200.00 l/war
        "45": 184000 / 15,  # ok. 12266.67 l/war
        "50": 163000 / 15   # ok. 10866.67 l/war
    },
    "Mozzarella": {
        "Standard": 196000 / 18 # ok. 10888.89 l/war
    }
}

# --- STYLIZACJA ---
st.markdown("""
    <style>
        .metric-box {
            background-color: #f8f9fa; border: 1px solid #ddd; border-radius: 8px; padding: 15px; text-align: center;
        }
        .metric-title { font-size: 14px; color: #666; text-transform: uppercase; font-weight: bold;}
        .metric-value { font-size: 24px; color: #1f77b4; font-weight: bold; margin-top: 5px;}
        .alert-box {
            background-color: #ffebee; border: 1px solid #ffcdd2; border-radius: 8px; padding: 15px; text-align: center; color: #b71c1c; font-weight: bold;
        }
        .success-box {
            background-color: #e8f5e9; border: 1px solid #c8e6c9; border-radius: 8px; padding: 15px; text-align: center; color: #2e7d32; font-weight: bold;
        }
    </style>
""", unsafe_allow_html=True)

st.title("🥛 Kalkulator Zużycia Mleka")

# --- SEKCJA 1: BILANS SUROWCA WEJŚCIOWEGO ---
st.subheader("📥 Podaż mleka")
c1, c2, c3, c4 = st.columns(4)

with c1:
    zapas_pocz = st.number_input("Zapas z wczoraj (L):", value=50000, step=1000)
with c2:
    dostawy = st.number_input("Mleko dostarczone (L):", value=600000, step=1000)
with c3:
    smietanka = st.number_input("Śmietanka (Odbiór) (L):", value=0, step=1000)
with c4:
    bel = st.number_input("Odbiór Bel (L):", value=0, step=1000)

# Obliczenie dostępnego mleka
mleko_dostepne = zapas_pocz + dostawy - smietanka - bel

# --- SEKCJA 2: PLANOWANIE PRODUKCJI ---
st.divider()
st.subheader("🧀 Planowanie produkcji na serowniach")

col_ch, col_be, col_mo = st.columns(3)

with col_ch:
    st.markdown("### Cheddar")
    ch_typ = st.selectbox("Wariant Cheddar:", ["40", "50", "Brak produkcji"])
    if ch_typ != "Brak produkcji":
        ch_wary = st.slider("Liczba warów (Cheddar):", min_value=18, max_value=20, value=19)
        zuzycie_ch = ch_wary * ZUZYCIE_WAR["Cheddar"][ch_typ]
    else:
        ch_wary = 0
        zuzycie_ch = 0
    st.info(f"Przewidywane zużycie: **{int(zuzycie_ch):,} L**".replace(",", " "))

with col_be:
    st.markdown("### Bertsch")
    be_typ = st.selectbox("Wariant Bertsch:", ["30", "45", "50", "Brak produkcji"])
    if be_typ != "Brak produkcji":
        be_wary = st.number_input("Liczba warów (Bertsch):", value=15, disabled=True, help="Stała liczba 15 warów")
        zuzycie_be = be_wary * ZUZYCIE_WAR["Bertsch"][be_typ]
    else:
        be_wary = 0
        zuzycie_be = 0
    st.info(f"Przewidywane zużycie: **{int(zuzycie_be):,} L**".replace(",", " "))

with col_mo:
    st.markdown("### Mozzarella")
    mo_on = st.checkbox("Produkcja Mozzarelli", value=True)
    if mo_on:
        mo_wary = st.number_input("Liczba warów (Mozzarella):", value=18, disabled=True, help="Stała liczba 18 warów")
        zuzycie_mo = mo_wary * ZUZYCIE_WAR["Mozzarella"]["Standard"]
    else:
        mo_wary = 0
        zuzycie_mo = 0
    st.info(f"Przewidywane zużycie: **{int(zuzycie_mo):,} L**".replace(",", " "))

# --- SEKCJA 3: PODSUMOWANIE ---
st.divider()
st.subheader("📊 Podsumowanie Dnia")

zuzycie_calkowite = zuzycie_ch + zuzycie_be + zuzycie_mo
zapas_koncowy = mleko_dostepne - zuzycie_calkowite

r1, r2, r3 = st.columns(3)

with r1:
    st.markdown(f"""
        <div class="metric-box">
            <div class="metric-title">Mleko dostępne do produkcji</div>
            <div class="metric-value">{int(mleko_dostepne):,} L</div>
        </div>
    """.replace(",", " "), unsafe_allow_html=True)

with r2:
    st.markdown(f"""
        <div class="metric-box">
            <div class="metric-title">Zaplanowane zużycie całkowite</div>
            <div class="metric-value" style="color:#d62728;">- {int(zuzycie_calkowite):,} L</div>
        </div>
    """.replace(",", " "), unsafe_allow_html=True)

with r3:
    if zapas_koncowy >= 0:
        st.markdown(f"""
            <div class="success-box">
                <div class="metric-title" style="color:#2e7d32;">Zapas na kolejny dzień (Stan końcowy)</div>
                <div class="metric-value" style="color:#2e7d32;">{int(zapas_koncowy):,} L</div>
            </div>
        """.replace(",", " "), unsafe_allow_html=True)
    else:
        st.markdown(f"""
            <div class="alert-box">
                <div class="metric-title" style="color:#b71c1c;">BRAKUJE MLEKA! (Deficyt)</div>
                <div class="metric-value" style="color:#b71c1c;">{int(zapas_koncowy):,} L</div>
            </div>
        """.replace(",", " "), unsafe_allow_html=True)
