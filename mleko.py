import streamlit as st

# --- KONFIGURACJA STRONY ---
st.set_page_config(page_title="Bilans Mleka - Serownie", layout="wide")

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
        .warning-box {
            background-color: #fff3e0; border: 1px solid #ffcc80; border-radius: 8px; padding: 15px; text-align: center; color: #e65100; font-weight: bold;
        }
    </style>
""", unsafe_allow_html=True)

st.title("🥛 Kalkulator Zużycia Mleka & Asystent")

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

mleko_dostepne = zapas_pocz + dostawy - smietanka - bel

# --- SEKCJA 2: PLANOWANIE PRODUKCJI ---
st.divider()
st.subheader("🧀 Planowanie produkcji na serowniach")

col_ch, col_be, col_mo = st.columns(3)

with col_ch:
    st.markdown("### Cheddar")
    ch_typ = st.selectbox("Wariant Cheddar:", ["Brak produkcji", "40", "50"], index=1)
    if ch_typ != "Brak produkcji":
        ch_wary = st.slider("Liczba warów (Cheddar):", min_value=18, max_value=20, value=19)
        zuzycie_ch = ch_wary * ZUZYCIE_WAR["Cheddar"][ch_typ]
    else:
        ch_wary = 0
        zuzycie_ch = 0
    st.info(f"Zużycie: **{int(zuzycie_ch):,} L**".replace(",", " "))

with col_be:
    st.markdown("### Bertsch")
    be_typ = st.selectbox("Wariant Bertsch:", ["Brak produkcji", "30", "45", "50"], index=1)
    if be_typ != "Brak produkcji":
        be_wary = st.number_input("Liczba warów (Bertsch):", value=15, disabled=True, help="Stała liczba 15 warów")
        zuzycie_be = be_wary * ZUZYCIE_WAR["Bertsch"][be_typ]
    else:
        be_wary = 0
        zuzycie_be = 0
    st.info(f"Zużycie: **{int(zuzycie_be):,} L**".replace(",", " "))

with col_mo:
    st.markdown("### Mozzarella")
    mo_on = st.checkbox("Produkcja Mozzarelli", value=True)
    if mo_on:
        mo_wary = st.number_input("Liczba warów (Mozzarella):", value=18, disabled=True, help="Stała liczba 18 warów")
        zuzycie_mo = mo_wary * ZUZYCIE_WAR["Mozzarella"]["Standard"]
    else:
        mo_wary = 0
        zuzycie_mo = 0
    st.info(f"Zużycie: **{int(zuzycie_mo):,} L**".replace(",", " "))

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
    if zapas_koncowy > CEL_ZAPASU_MAX:
        st.markdown(f"""
            <div class="warning-box">
                <div class="metric-title" style="color:#e65100;">NADWYŻKA MLEKA (RYZYKO!)</div>
                <div class="metric-value" style="color:#e65100;">+{int(zapas_koncowy):,} L</div>
            </div>
        """.replace(",", " "), unsafe_allow_html=True)
    elif zapas_koncowy < CEL_ZAPASU_MIN:
        st.markdown(f"""
            <div class="alert-box">
                <div class="metric-title" style="color:#b71c1c;">KRYTYCZNY BRAK MLEKA</div>
                <div class="metric-value" style="color:#b71c1c;">{int(zapas_koncowy):,} L</div>
            </div>
        """.replace(",", " "), unsafe_allow_html=True)
    else:
        st.markdown(f"""
            <div class="success-box">
                <div class="metric-title" style="color:#2e7d32;">BEZPIECZNY ZAPAS (NA MINUSIE)</div>
                <div class="metric-value" style="color:#2e7d32;">{int(zapas_koncowy):,} L</div>
            </div>
        """.replace(",", " "), unsafe_allow_html=True)

# --- ASYSTENT PLANOWANIA ---
st.markdown("<br>", unsafe_allow_html=True)
if zapas_koncowy > CEL_ZAPASU_MAX:
    st.warning(f"💡 **ASYSTENT:** Zostaje Ci w silosach **{int(zapas_koncowy):,} L** mleka na plusie! W razie awarii nie będziesz miał gdzie zrzucać kolejnych dostaw. Rozważ uruchomienie dodatkowej linii, aby zejść z zapasem poniżej zera.".replace(",", " "))
elif zapas_koncowy < CEL_ZAPASU_MIN:
    przekroczenie = abs(zapas_koncowy) - abs(CEL_ZAPASU_MIN)
    st.error(f"🚨 **ASYSTENT:** Uważaj, zaplanowałeś za dużą produkcję! Jesteś na minusie o **{int(abs(zapas_koncowy)):,} L**, co przekracza limit -100 tys. o dokładnie **{int(przekroczenie):,} L**. Musisz zmniejszyć ilość warów lub wyłączyć linię.".replace(",", " "))
else:
    st.success(f"✅ **ASYSTENT:** Plan jest doskonały! Zapas końcowy wynosi **{int(zapas_koncowy):,} L**. Silosy są bezpiecznie opróżnione na wypadek awarii, a deficyt mieści się w dozwolonej normie do -100 tys. litrów.".replace(",", " "))
