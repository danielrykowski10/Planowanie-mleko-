import streamlit as st
import pandas as pd
import datetime
import json
import os

# --- KONFIGURACJA STRONY ---
st.set_page_config(page_title="Monitor Wody i Ścieków", layout="wide")

# --- BAZA DANYCH ---
PLIK_WODA = "dane_woda_scieki.json"

def wczytaj_dane():
    if os.path.exists(PLIK_WODA):
        try:
            with open(PLIK_WODA, "r", encoding="utf-8") as f:
                dane = json.load(f)
                # Zabezpieczenie dla starszych wpisów bez serwatki
                for wpis in dane:
                    if "Serwatka_m3" not in wpis:
                        wpis["Serwatka_m3"] = 0.0
                return dane
        except:
            return []
    return []

def zapisz_dane(dane):
    with open(PLIK_WODA, "w", encoding="utf-8") as f:
        json.dump(dane, f, ensure_ascii=False, indent=4)

if 'historia_wody' not in st.session_state:
    st.session_state.historia_wody = wczytaj_dane()

# --- STYLIZACJA ---
st.markdown("""
    <style>
        .metric-box { background-color: #f8f9fa; border: 1px solid #ddd; border-radius: 8px; padding: 15px; text-align: center; }
        .metric-title { font-size: 14px; color: #666; text-transform: uppercase; font-weight: bold;}
        .metric-value { font-size: 24px; color: #1f77b4; font-weight: bold; margin-top: 5px;}
    </style>
""", unsafe_allow_html=True)

st.title("💧 System Monitoringu: Woda i Ścieki")

# --- PANEL BOCZNY (NORMY) ---
with st.sidebar:
    st.header("⚙️ Normy Zakładowe")
    cel_woda = st.number_input("Cel: Max L wody na 1L mleka", value=2.5, step=0.1)
    limit_ph_min = st.number_input("Min pH zrzutu", value=6.5, step=0.1)
    limit_ph_max = st.number_input("Max pH zrzutu", value=9.0, step=0.1)
    limit_chzt = st.number_input("Max ChZT (mg/L)", value=3000, step=100)
    tolerancja_bilansu = st.number_input("Tolerancja bilansu ścieków (m³)", value=10.0, step=1.0, help="Dopuszczalna różnica między wodą+serwatką a ściekami")
    
    st.divider()
    if st.button("🗑️ Wyczyść historię", use_container_width=True):
        st.session_state.historia_wody = []
        zapisz_dane([])
        st.rerun()

# --- ZAKŁADKI ---
tab1, tab2 = st.tabs(["📝 Rejestr Dobowy", "📈 Analiza Kierownicza"])

# ==========================================
# ZAKŁADKA 1: WPROWADZANIE DANYCH
# ==========================================
with tab1:
    st.subheader("Wprowadź dane z minionej doby")
    
    with st.form("formularz_dobowy", clear_on_submit=True):
        data_wpisu = st.date_input("Data raportu", datetime.date.today())
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**🚰 Zużycie i Produkcja**")
            woda_m3 = st.number_input("Zużycie wody (m³)", min_value=0.0, value=500.0, step=10.0)
            mleko_l = st.number_input("Przerobione mleko (L)", min_value=0, value=250000, step=5000)
            serwatka_m3 = st.number_input("Zrzut serwatki do ścieków (m³)", min_value=0.0, value=0.0, step=1.0, help="Ilość serwatki, która trafiła do kanalizacji")
        with c2:
            st.markdown("**☢️ Parametry Ścieków**")
            scieki_m3 = st.number_input("Ilość ścieków wg przepływomierza (m³)", min_value=0.0, value=500.0, step=10.0)
            ph_sciekow = st.slider("Średnie pH ścieków", min_value=0.0, max_value=14.0, value=7.5, step=0.1)
            chzt_sciekow = st.number_input("Wynik ChZT (mg/L)", min_value=0, value=2100, step=50)
            
        st.info("💡 **Zasada bilansu:** Ilość wody (m³) + Zrzut serwatki (m³) powinny w przybliżeniu równać się Ilości ścieków (m³).")
            
        zapisz_btn = st.form_submit_button("💾 ZAPISZ WYNIKI DO BAZY", type="primary")
        
        if zapisz_btn:
            dane_data = data_wpisu.strftime("%Y-%m-%d")
            istniejacy_indeks = next((i for i, v in enumerate(st.session_state.historia_wody) if v["Data"] == dane_data), None)
            
            nowy_wpis = {
                "Data": dane_data,
                "Woda_m3": woda_m3,
                "Mleko_L": mleko_l,
                "Serwatka_m3": serwatka_m3,
                "Scieki_m3": scieki_m3,
                "pH": ph_sciekow,
                "ChZT": chzt_sciekow
            }
            
            if istniejacy_indeks is not None:
                st.session_state.historia_wody[istniejacy_indeks] = nowy_wpis
                st.success(f"Zaktualizowano dane dla dnia {dane_data}")
            else:
                st.session_state.historia_wody.append(nowy_wpis)
                st.success(f"Dodano nowy raport dla dnia {dane_data}")
                
            zapisz_dane(st.session_state.historia_wody)
            st.rerun()

# ==========================================
# ZAKŁADKA 2: ANALIZA DLA KIEROWNIKA
# ==========================================
with tab2:
    st.subheader("Pulpit Analityczny Głównego Technologa / Kierownika")
    
    if not st.session_state.historia_wody:
        st.info("Brak danych do analizy. Wprowadź pierwsze wyniki w zakładce 'Rejestr Dobowy'.")
    else:
        df = pd.DataFrame(st.session_state.historia_wody)
        # Zabezpieczenie dla starych danych
        if 'Serwatka_m3' not in df.columns:
            df['Serwatka_m3'] = 0.0
            
        df['Data'] = pd.to_datetime(df['Data'])
        df = df.sort_values('Data')
        
        # Obliczenia analityczne
        df['Wskaźnik (L/L)'] = (df['Woda_m3'] * 1000) / df['Mleko_L'].replace(0, 1) # Unikamy dzielenia przez zero
        df['Wskaźnik (L/L)'] = df['Wskaźnik (L/L)'].round(2)
        
        # OBLICZENIE BILANSU ŚCIEKÓW
        df['Oczekiwane Ścieki (m³)'] = df['Woda_m3'] + df['Serwatka_m3']
        df['Różnica Bilansu (m³)'] = (df['Scieki_m3'] - df['Oczekiwane Ścieki (m³)']).round(1)
        
        # --- SZYBKIE STATYSTYKI ---
        ost_dane = df.iloc[-1]
        srednia_woda = df['Wskaźnik (L/L)'].mean()
        
        col_s1, col_s2, col_s3 = st.columns(3)
        with col_s1:
            st.metric("Ostatni wskaźnik wody", f"{ost_dane['Wskaźnik (L/L)']} L/L", 
                      delta=f"{round(ost_dane['Wskaźnik (L/L)'] - cel_woda, 2)} od celu", 
                      delta_color="inverse")
        with col_s2:
            st.metric("Ostatni zrzut serwatki", f"{ost_dane['Serwatka_m3']} m³")
        with col_s3:
            # Kolorowanie bilansu na żywo
            bilans = ost_dane['Różnica Bilansu (m³)']
            if abs(bilans) <= tolerancja_bilansu:
                st.metric("Bilans wodno-ściekowy (Różnica)", f"{bilans} m³", "Zgodny z pomiarami", delta_color="normal")
            else:
                st.metric("Bilans wodno-ściekowy (Różnica)", f"{bilans} m³", "BŁĄD POMIAROWY / WYCIEK!", delta_color="inverse")
            
        st.divider()
        
        # --- WYKRESY TRENDÓW ---
        c_wyk1, c_wyk2 = st.columns(2)
        
        with c_wyk1:
            st.markdown("#### ⚖️ Bilans: Oczekiwane vs Rzeczywiste Ścieki")
            st.caption("Linie powinny się nakładać. Rozjazd oznacza problem z przepływomierzem lub nienotowane zrzuty/wycieki.")
            chart_data_bilans = df[['Data', 'Scieki_m3', 'Oczekiwane Ścieki (m³)']].set_index('Data')
            st.line_chart(chart_data_bilans)
            
        with c_wyk2:
            st.markdown("#### ☣️ Trend zanieczyszczeń (ChZT) vs Zrzut Serwatki")
            st.caption("Piki ChZT często pokrywają się ze zrzutami serwatki do kanalizacji.")
            # Normalizujemy serwatkę, żeby była widoczna na jednym wykresie z ChZT
            chart_data_chzt = df[['Data', 'ChZT']].set_index('Data')
            st.bar_chart(chart_data_chzt, color="#ff7f0e")
        
        # --- BAZA WYNIKÓW (TABELA) ---
        st.divider()
        st.markdown("#### 📋 Pełna historia pomiarów")
        
        # Formatowanie do wyświetlania
        cols_to_show = ['Data', 'Woda_m3', 'Serwatka_m3', 'Scieki_m3', 'Różnica Bilansu (m³)', 'Wskaźnik (L/L)', 'pH', 'ChZT']
        df_wyswietl = df[cols_to_show].sort_values('Data', ascending=False).copy()
        df_wyswietl['Data'] = df_wyswietl['Data'].dt.strftime('%Y-%m-%d')
        
        # Stylizacja tabeli (kolorowanie błędów)
        def stylizuj_tabele(row):
            styles = [''] * len(row)
            if row['Wskaźnik (L/L)'] > cel_woda:
                styles[df_wyswietl.columns.get_loc('Wskaźnik (L/L)')] = 'background-color: #ffebee; color: #b71c1c;'
            if row['ChZT'] > limit_chzt:
                styles[df_wyswietl.columns.get_loc('ChZT')] = 'background-color: #fff3e0; color: #e65100;'
            if not (limit_ph_min <= row['pH'] <= limit_ph_max):
                styles[df_wyswietl.columns.get_loc('pH')] = 'background-color: #ffebee; color: #b71c1c;'
            # Kolorowanie złego bilansu (z uwzględnieniem tolerancji np. 10m3)
            if abs(row['Różnica Bilansu (m³)']) > tolerancja_bilansu:
                styles[df_wyswietl.columns.get_loc('Różnica Bilansu (m³)')] = 'background-color: #fff9c4; color: #f57f17; font-weight:bold;'
            return styles
            
        st.dataframe(df_wyswietl.style.apply(stylizuj_tabele, axis=1), use_container_width=True, hide_index=True)
