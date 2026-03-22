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

# --- PANEL BOCZNY (NORMY I KOSZTY) ---
with st.sidebar:
    st.header("⚙️ Normy Zakładowe")
    cel_woda = st.number_input("Cel: Max L wody na 1L mleka", value=2.5, step=0.1)
    limit_ph_min = st.number_input("Min pH zrzutu", value=6.5, step=0.1)
    limit_ph_max = st.number_input("Max pH zrzutu", value=9.0, step=0.1)
    limit_chzt = st.number_input("Max ChZT (mg/L)", value=3000, step=100)
    tolerancja_bilansu = st.number_input("Tolerancja bilansu ścieków (m³/dobę)", value=10.0, step=1.0)
    
    st.divider()
    st.header("💰 Stawki (do analizy kosztów)")
    cena_wody = st.number_input("Cena wody (PLN/m³)", value=4.50, step=0.10)
    cena_sciekow = st.number_input("Cena ścieków (PLN/m³)", value=8.20, step=0.10)

    st.divider()
    if st.button("🗑️ Wyczyść historię", use_container_width=True):
        st.session_state.historia_wody = []
        zapisz_dane([])
        st.rerun()

# --- ZAKŁADKI ---
tab1, tab2, tab3 = st.tabs(["📝 Rejestr Dobowy", "📉 Analiza - 7 Dni", "📊 Raport Miesięczny"])

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
            serwatka_m3 = st.number_input("Zrzut serwatki do ścieków (m³)", min_value=0.0, value=0.0, step=1.0)
        with c2:
            st.markdown("**☢️ Parametry Ścieków**")
            scieki_m3 = st.number_input("Ilość ścieków (m³)", min_value=0.0, value=500.0, step=10.0)
            ph_sciekow = st.slider("Średnie pH ścieków", min_value=0.0, max_value=14.0, value=7.5, step=0.1)
            chzt_sciekow = st.number_input("Wynik ChZT (mg/L)", min_value=0, value=2100, step=50)
            
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

# Funkcja do stylizacji tabel
def stylizuj_tabele(row, cel_woda, limit_chzt, limit_ph_min, limit_ph_max, tolerancja_bilansu, df_cols):
    styles = [''] * len(row)
    if row['Wskaźnik (L/L)'] > cel_woda:
        styles[df_cols.get_loc('Wskaźnik (L/L)')] = 'background-color: #ffebee; color: #b71c1c;'
    if row['ChZT'] > limit_chzt:
        styles[df_cols.get_loc('ChZT')] = 'background-color: #fff3e0; color: #e65100;'
    if not (limit_ph_min <= row['pH'] <= limit_ph_max):
        styles[df_cols.get_loc('pH')] = 'background-color: #ffebee; color: #b71c1c;'
    if abs(row['Różnica Bilansu (m³)']) > tolerancja_bilansu:
        styles[df_cols.get_loc('Różnica Bilansu (m³)')] = 'background-color: #fff9c4; color: #f57f17; font-weight:bold;'
    return styles

# Przygotowanie danych
df = pd.DataFrame()
if st.session_state.historia_wody:
    df = pd.DataFrame(st.session_state.historia_wody)
    if 'Serwatka_m3' not in df.columns: df['Serwatka_m3'] = 0.0
    df['Data'] = pd.to_datetime(df['Data'])
    df = df.sort_values('Data')
    df['Wskaźnik (L/L)'] = (df['Woda_m3'] * 1000) / df['Mleko_L'].replace(0, 1)
    df['Wskaźnik (L/L)'] = df['Wskaźnik (L/L)'].round(2)
    df['Oczekiwane Ścieki (m³)'] = df['Woda_m3'] + df['Serwatka_m3']
    df['Różnica Bilansu (m³)'] = (df['Scieki_m3'] - df['Oczekiwane Ścieki (m³)']).round(1)

# ==========================================
# ZAKŁADKA 2: ANALIZA OSTATNIE 7 DNI
# ==========================================
with tab2:
    st.subheader("Bieżąca kontrola operacyjna (Ostatnie 7 wpisów)")
    if df.empty:
        st.info("Brak danych do analizy.")
    else:
        df_7 = df.tail(7).copy()
        ost_dane = df_7.iloc[-1]
        
        col_s1, col_s2, col_s3 = st.columns(3)
        with col_s1:
            st.metric("Dzisiejszy Wskaźnik Wody", f"{ost_dane['Wskaźnik (L/L)']} L/L", 
                      delta=f"{round(ost_dane['Wskaźnik (L/L)'] - cel_woda, 2)} od celu", delta_color="inverse")
        with col_s2:
            st.metric("Dzisiejszy zrzut serwatki", f"{ost_dane['Serwatka_m3']} m³")
        with col_s3:
            bilans = ost_dane['Różnica Bilansu (m³)']
            if abs(bilans) <= tolerancja_bilansu:
                st.metric("Bilans wodno-ściekowy", f"{bilans} m³", "W normie", delta_color="normal")
            else:
                st.metric("Bilans wodno-ściekowy", f"{bilans} m³", "BŁĄD POMIAROWY/WYCIEK", delta_color="inverse")
            
        st.divider()
        c_wyk1, c_wyk2 = st.columns(2)
        with c_wyk1:
            st.markdown("**Wskaźnik (L wody / 1L mleka) - 7 Dni**")
            st.line_chart(df_7[['Data', 'Wskaźnik (L/L)']].set_index('Data'), color="#1f77b4")
        with c_wyk2:
            st.markdown("**Zanieczyszczenie ChZT (mg/L) - 7 Dni**")
            st.bar_chart(df_7[['Data', 'ChZT']].set_index('Data'), color="#ff7f0e")

        st.markdown("#### 📋 Szczegółowe dane z 7 dni")
        cols_to_show = ['Data', 'Woda_m3', 'Serwatka_m3', 'Scieki_m3', 'Różnica Bilansu (m³)', 'Wskaźnik (L/L)', 'pH', 'ChZT']
        df_7_wyswietl = df_7[cols_to_show].sort_values('Data', ascending=False).copy()
        df_7_wyswietl['Data'] = df_7_wyswietl['Data'].dt.strftime('%Y-%m-%d')
        
        # Rozbita, bezpieczna linijka do stylowania tabeli
        styled_df_7 = df_7_wyswietl.style.apply(
            lambda row: stylizuj_tabele(row, cel_woda, limit_chzt, limit_ph_min, limit_ph_max, tolerancja_bilansu, df_7_wyswietl.columns), 
            axis=1
        )
        st.dataframe(styled_df_7, use_container_width=True, hide_index=True)

# ==========================================
# ZAKŁADKA 3: ROZBUDOWANY RAPORT MIESIĘCZNY
# ==========================================
with tab3:
    st.subheader("📊 Zaawansowany Raport Miesięczny")
    
    if df.empty:
        st.info("Brak danych do wygenerowania raportu.")
    else:
        df['Miesiąc'] = df['Data'].dt.strftime('%Y-%m')
        lista_miesiecy = sorted(df['Miesiąc'].unique(), reverse=True)
        wybrany_miesiac = st.selectbox("Wybierz miesiąc do analizy:", lista_miesiecy)
        df_mc = df[df['Miesiąc'] == wybrany_miesiac].copy()
        
        # --- OBLICZENIA MIESIĘCZNE ---
        liczba_dni = len(df_mc)
        suma_wody = df_mc['Woda_m3'].sum()
        suma_mleka = df_mc['Mleko_L'].sum()
        suma_sciekow = df_mc['Scieki_m3'].sum()
        suma_serwatki = df_mc['Serwatka_m3'].sum()
        
        # Finanse
        koszt_wody = suma_wody * cena_wody
        koszt_sciekow = suma_sciekow * cena_sciekow
        koszt_total = koszt_wody + koszt_sciekow
        koszt_na_1000l = (koszt_total / (suma_mleka / 1000)) if suma_mleka > 0 else 0
        
        # Wskaźniki i Zgodność (Compliance)
        sredni_wskaznik_mc = (suma_wody * 1000) / suma_mleka if suma_mleka > 0 else 0
        
        przekroczenia_ph = len(df_mc[(df_mc['pH'] < limit_ph_min) | (df_mc['pH'] > limit_ph_max)])
        przekroczenia_chzt = len(df_mc[df_mc['ChZT'] > limit_chzt])
        
        suma_roznic_bilansu = df_mc['Różnica Bilansu (m³)'].sum() # Niezbilansowana woda w miesiącu

        st.markdown(f"### Raport z wyników dla: **{wybrany_miesiac}** (zarejestrowano {liczba_dni} dni)")
        
        # --- SEKCJA 1: WOLUMENY ---
        st.markdown("#### 📦 Wolumeny Produkcyjne")
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Przerobione Mleko", f"{suma_mleka:,.0f} L".replace(',', ' '))
        k2.metric("Pobrana Woda", f"{suma_wody:,.0f} m³".replace(',', ' '))
        k3.metric("Zrzut Serwatki", f"{suma_serwatki:,.0f} m³".replace(',', ' '))
        k4.metric("Oddane Ścieki", f"{suma_sciekow:,.0f} m³".replace(',', ' '))
        
        st.divider()
        
        # --- SEKCJA 2: FINANSE ---
        st.markdown("#### 💰 Szacowane Koszty Mediów")
        f1, f2, f3 = st.columns(3)
        f1.metric("Koszt Wody (szacunek)", f"{koszt_wody:,.2f} PLN".replace(',', ' '))
        f2.metric("Koszt Ścieków (szacunek)", f"{koszt_sciekow:,.2f} PLN".replace(',', ' '))
        f3.metric("Koszt mediów na 1000L mleka", f"{koszt_na_1000l:,.2f} PLN".replace(',', ' '), "Wskaźnik efektywności", delta_color="off")
        
        st.divider()
        
        # --- SEKCJA 3: COMPLIANCE I JAKOŚĆ ---
        st.markdown("#### 🛡️ Zgodność Środowiskowa i Wycieki")
        c1, c2, c3, c4 = st.columns(4)
        
        delta_mc = sredni_wskaznik_mc - cel_woda
        if sredni_wskaznik_mc <= cel_woda:
            c1.metric("Średni Wskaźnik Wody", f"{sredni_wskaznik_mc:.2f} L/L", "Norma zachowana", delta_color="normal")
        else:
            c1.metric("Średni Wskaźnik Wody", f"{sredni_wskaznik_mc:.2f} L/L", f"Przekroczenie o {delta_mc:.2f}", delta_color="inverse")
            
        c2.metric("Przekroczenia pH", f"{przekroczenia_ph} dni", "Ryzyko kar!" if przekroczenia_ph > 0 else "Brak naruszeń", delta_color="inverse" if przekroczenia_ph > 0 else "normal")
        c3.metric("Przekroczenia ChZT", f"{przekroczenia_chzt} dni", "Zrzuty białka!" if przekroczenia_chzt > 0 else "Czysto", delta_color="inverse" if przekroczenia_chzt > 0 else "normal")
        
        if abs(suma_roznic_bilansu) > (tolerancja_bilansu * 5): 
            c4.metric("Niezbilansowane ścieki", f"{suma_roznic_bilansu:,.1f} m³".replace(',', ' '), "Potencjalny wyciek / awaria", delta_color="inverse")
        else:
            c4.metric("Niezbilansowane ścieki", f"{suma_roznic_bilansu:,.1f} m³".replace(',', ' '), "W normie pomiarowej", delta_color="normal")

        # --- SEKCJA 4: WYKRESY MIESIĘCZNE ---
        st.markdown("#### 📉 Wykres KPI na przestrzeni miesiąca")
        st.line_chart(df_mc[['Data', 'Wskaźnik (L/L)']].set_index('Data'), color="#1f77b4")

        # --- SEKCJA 5: TABELA ---
        st.markdown("#### 📋 Szczegółowe dane dzienne")
        cols_to_show = ['Data', 'Woda_m3', 'Serwatka_m3', 'Scieki_m3', 'Różnica Bilansu (m³)', 'Wskaźnik (L/L)', 'pH', 'ChZT']
        df_mc_wyswietl = df_mc[cols_to_show].sort_values('Data', ascending=False).copy()
        df_mc_wyswietl['Data'] = df_mc_wyswietl['Data'].dt.strftime('%Y-%m-%d')
        
        # Rozbita, bezpieczna linijka do stylowania tabeli
        styled_df_mc = df_mc_wyswietl.style.apply(
            lambda row: stylizuj_tabele(row, cel_woda, limit_chzt, limit_ph_min, limit_ph_max, tolerancja_bilansu, df_mc_wyswietl.columns), 
            axis=1
        )
        st.dataframe(styled_df_mc, use_container_width=True, hide_index=True)
