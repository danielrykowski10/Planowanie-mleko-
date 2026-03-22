import streamlit as st
import pandas as pd

# --- KONFIGURACJA STRONY ---
st.set_page_config(page_title="Monitor Wody i Ścieków", layout="wide")

# --- STYLIZACJA (Spójna z poprzednimi apkami) ---
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

st.title("💧 Monitor Zużycia Wody i Kontroli Ścieków")

# --- PANEL BOCZNY (USTAWIENIA NORM) ---
with st.sidebar:
    st.header("⚙️ Normy Zakładowe")
    st.markdown("Ustaw limity alarmowe dla zakładu:")
    cel_woda = st.number_input("Cel: Max L wody na 1L mleka", value=2.5, step=0.1)
    limit_ph_min = st.number_input("Min pH zrzutu", value=6.5, step=0.1)
    limit_ph_max = st.number_input("Max pH zrzutu", value=9.0, step=0.1)
    limit_chzt = st.number_input("Max ChZT (mg/L) przed oczyszczalnią", value=3000, step=100)

# --- WPROWADZANIE DANYCH ---
st.subheader("📝 Wprowadź dane z dzisiejszej doby")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🚰 Zużycie Wody i Produkcja")
    woda_m3 = st.number_input("Zużycie wody (m³ z wodomierza główn.)", value=500.0, step=10.0)
    mleko_l = st.number_input("Przerobione mleko w tej dobie (L)", value=250000, step=5000)
    
    # Przeliczenie m3 na litry
    woda_l = woda_m3 * 1000
    
    # Wyliczenie KPI (Wskaźnik wody)
    if mleko_l > 0:
        wskaznik_wody = woda_l / mleko_l
    else:
        wskaznik_wody = 0

with col2:
    st.markdown("### ☢️ Parametry Ścieków (Podczyszczalnia)")
    scieki_m3 = st.number_input("Ilość zrzuconych ścieków (m³)", value=480.0, step=10.0)
    ph_sciekow = st.slider("Średnie pH ścieków", min_value=0.0, max_value=14.0, value=7.5, step=0.1)
    chzt_sciekow = st.number_input("Wynik ChZT (mg/L)", value=2100, step=50)
    temp_sciekow = st.number_input("Temperatura ścieku (°C)", value=22.0, step=1.0)

st.divider()

# --- WIZUALIZACJA I KONTROLA KPI ---
st.subheader("📊 Raport Dobowy i Alerty")

r1, r2, r3 = st.columns(3)

# 1. KONTROLA ZUŻYCIA WODY
with r1:
    if wskaznik_wody <= cel_woda:
        st.markdown(f"""
            <div class="success-box">
                <div class="metric-title">Zużycie Wody (L wody / 1L mleka)</div>
                <div class="metric-value">{wskaznik_wody:.2f} L</div>
                <div style="font-size: 12px; margin-top:5px;">✅ Cel osiągnięty (< {cel_woda})</div>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
            <div class="alert-box">
                <div class="metric-title">Zużycie Wody (L wody / 1L mleka)</div>
                <div class="metric-value">{wskaznik_wody:.2f} L</div>
                <div style="font-size: 12px; margin-top:5px;">⚠️ Zbyt duże zużycie! (Cel: {cel_woda})</div>
            </div>
        """, unsafe_allow_html=True)

# 2. KONTROLA pH ŚCIEKÓW
with r2:
    if limit_ph_min <= ph_sciekow <= limit_ph_max:
        st.markdown(f"""
            <div class="success-box">
                <div class="metric-title">Odczyn pH Ścieków</div>
                <div class="metric-value">{ph_sciekow:.1f}</div>
                <div style="font-size: 12px; margin-top:5px;">✅ W normie zakładowej</div>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
            <div class="alert-box">
                <div class="metric-title">Odczyn pH Ścieków</div>
                <div class="metric-value">{ph_sciekow:.1f}</div>
                <div style="font-size: 12px; margin-top:5px;">🚨 RYZYKO KAR / AWARII BIOLOGII!</div>
            </div>
        """, unsafe_allow_html=True)

# 3. KONTROLA ŁADUNKU (ChZT)
with r3:
    if chzt_sciekow <= limit_chzt:
        st.markdown(f"""
            <div class="success-box">
                <div class="metric-title">Ładunek ChZT</div>
                <div class="metric-value">{chzt_sciekow} mg/L</div>
                <div style="font-size: 12px; margin-top:5px;">✅ Bezpiecznie dla oczyszczalni</div>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
            <div class="warning-box">
                <div class="metric-title">Ładunek ChZT</div>
                <div class="metric-value">{chzt_sciekow} mg/L</div>
                <div style="font-size: 12px; margin-top:5px;">⚠️ Przeciążenie! (Zrzut serwatki/mleka?)</div>
            </div>
        """, unsafe_allow_html=True)

# --- ASYSTENT GŁÓWNEGO TECHNOLOGA / KIEROWNIKA ---
st.markdown("<br>", unsafe_allow_html=True)
st.subheader("🤖 Wnioski Asystenta dla Kierownika")

wnioski = []
if wskaznik_wody > cel_woda:
    wnioski.append("💧 **STRATY WODY:** Zużywasz za dużo wody w stosunku do przerabianego mleka. Sprawdź, czy mycia CIP na linii Bertsch/Cheddar nie są wydłużone, lub czy na dziale nikt nie zostawia 'węża z wodą' w kratce.")
    
if ph_sciekow < limit_ph_min:
    wnioski.append("🧪 **ALARM KWAŚNY (pH):** Do oczyszczalni trafił zrzut mocno kwasowy. Zwróć uwagę, czy na myjce nie doszło do wycieku kwasu azotowego podczas mycia kwaśnego sprzętu.")
elif ph_sciekow > limit_ph_max:
    wnioski.append("🧪 **ALARM ZASADOWY (pH):** Do oczyszczalni trafił zrzut mocno zasadowy. Sprawdź dawkowanie ługu w stacji CIP.")

if chzt_sciekow > limit_chzt:
    wnioski.append("🧀 **STRATY SUROWCA:** Bardzo wysokie ChZT! Oznacza to, że do ścieków przedostało się dużo białka lub tłuszczu. Gdzieś na hali nastąpił duży zrzut serwatki, popłuczyny z mleka nie zostały odzyskane, lub pękł zbiornik. Natychmiast poinstruuj operatorów, żeby nie lali mleka w kratki!")

if not wnioski:
    st.success("Wszystkie parametry w normie. Oczyszczalnia pracuje stabilnie, a zużycie wody jest optymalne!")
else:
    for w in wnioski:
        st.warning(w)
