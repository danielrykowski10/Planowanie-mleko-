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

# --- PANEL BOCZNY (NORMY) ---
with st.sidebar:
    st.header("⚙️ Normy Zakładowe")
    cel_woda = st.number_input("Cel: Max L wody na 1L mleka", value=2.5, step=0.1)
    limit_ph_min = st.number_input("Min pH zrzutu", value=6.5, step=0.1)
    limit_ph_max = st.number_input("Max pH zrzutu", value=9.0, step=0.1)
    limit_chzt = st.number_input("Max ChZT (mg/L)", value=3000, step=100)
    tolerancja_bilansu = st.number_input("Tolerancja bilansu ścieków (m³)", value=10.0, step=1.0)
    
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
            
        st.info("💡 **Bilans:** Woda (m³) + Zrzut serwatki (m³) ≈ Ilość ścieków (m³).")
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

# Funkcja pomocnicza do stylizacji tabel (wspólna dla tab2 i tab3)
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

# Wspólne przygotowanie danych jeśli istnieją
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
        # Bierzemy tylko 7 ostatnich rekordów
        df_7 = df.tail(7).copy()
        
        ost_dane = df_7.iloc[-1]
        
        col_s1, col_s2, col_s3 = st.columns(3)
        with col_s1:
            st.metric("Dzisiejszy Wskaźnik Wody", f"{ost_dane['Wskaźnik (L/L)']} L/L", 
                      delta=f"{round(ost_dane['Wskaźnik (L/L)'] - cel_woda, 2)} od celu", 
                      delta_color="inverse")
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
            
        st.markdown("**Tabela 7-dniowa**")
        cols_to_show = ['Data', 'Woda_m3', 'Serwatka_m3', 'Scieki_m3', 'Różnica Bilansu (m³)', 'Wskaźnik (L/L)', 'pH', 'ChZT']
        df_7_wyswietl = df_7[cols_to_show].sort_values('Data', ascending=False).copy()
        df_7_wyswietl['Data'] = df_7_wyswietl['Data'].dt.strftime('%Y-%m-%d')
        st.dataframe(df_7_wyswietl.style.apply(lambda row: stylizuj_tabele(row, cel_woda, limit_chzt, limit_ph_min, limit_ph_max, tolerancja_bilansu, df_7_wyswietl.columns), axis=1), use_container_width=True, hide_index=True)

# ==========================================
# ZAKŁADKA 3: RAPORT MIESIĘCZNY
# ==========================================
with tab3:
    st.subheader("Raport i Podsumowanie Miesięczne")
    
    if df.empty:
        st.info("Brak danych do wygenerowania raportu.")
    else:
        # Dodanie kolumny Miesiąc-Rok (np. 2026-03)
        df['Miesiąc'] = df['Data'].dt.strftime('%Y-%m')
        lista_miesiecy = sorted(df['Miesiąc'].unique(), reverse=True)
        
        wybrany_miesiac = st.selectbox("Wybierz miesiąc do analizy:", lista_miesiecy)
        
        # Filtrujemy dane dla wybranego miesiąca
        df_mc = df[df['Miesiąc'] == wybrany_miesiac].copy()
        
        # OBLICZENIA MIESIĘCZNE (SUMY I ŚREDNIE)
        suma_wody = df_mc['Woda_m3'].sum()
        suma_mleka = df_mc['Mleko_L'].sum()
        suma_sciekow = df_mc['Scieki_m3'].sum()
        suma_serwatki = df_mc['Serwatka_m3'].sum()
        
        # Rzeczywisty, zagregowany wskaźnik dla całego miesiąca
        sredni_wskaznik_mc = (suma_wody * 1000) / suma_mleka if suma_mleka > 0 else 0
        srednie_ph = df_mc['pH'].mean()
        max_chzt = df_mc['ChZT'].max()
        
        st.markdown(f"### Podsumowanie dla: {wybrany_miesiac}")
        
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Łączne zużycie wody", f"{suma_wody:,.0f} m³".replace(',', ' '))
        k2.metric("Łącznie przerobione mleko", f"{suma_mleka:,.0f} L".replace(',', ' '))
        k3.metric("Łączny zrzut ścieków", f"{suma_sciekow:,.0f} m³".replace(',', ' '))
        k4.metric("Łączny zrzut serwatki", f"{suma_serwatki:,.0f} m³".replace(',', ' '))
        
        st.divider()
        
        # Wyniki jakościowe miesiąca
        q1, q2, q3 = st.columns(3)
        
        # Ocena Wskaźnika miesięcznego
        delta_mc = sredni_wskaznik_mc - cel_woda
        if sredni_wskaznik_mc <= cel_woda:
            q1.metric("KPI: Średni wskaźnik wody", f"{sredni_wskaznik_mc:.2f} L/L", "W normie miesiąca", delta_color="normal")
        else:
            q1.metric("KPI: Średni wskaźnik wody", f"{sredni_wskaznik_mc:.2f} L/L", f"{delta_mc:.2f} POWYŻEJ CELU", delta_color="inverse")
            
        q2.metric("Średnie pH ścieków", f"{srednie_ph:.1f}")
        q3.metric("Najwyższe ChZT w miesiącu", f"{max_chzt} mg/L")

        st.markdown("#### ⚖️ Bilans wodno-ściekowy miesiąca")
        st.bar_chart(df_mc[['Data', 'Scieki_m3', 'Oczekiwane Ścieki (m³)']].set_index('Data'))

        st.markdown(f"#### 📋 Rejestr dni w miesiącu ({wybrany_miesiac})")
        cols_to_show = ['Data', 'Woda_m3', 'Serwatka_m3', 'Scieki_m3', 'Różnica Bilansu (m³)', 'Wskaźnik (L/L)', 'pH', 'ChZT']
        df_mc_wyswietl = df_mc[cols_to_show].sort_values('Data', ascending=False).copy()
        df_mc_wyswietl['Data'] = df_mc_wyswietl['Data'].dt.strftime('%Y-%m-%d')
        st.dataframe(df_mc_wyswietl.style.apply(lambda row: stylizuj_tabele(row, cel_woda, limit_chzt, limit_ph_min, limit_ph_max, tolerancja_bilansu, df_mc_wyswietl.columns), axis=1), use_container_width=True, hide_index=True)
