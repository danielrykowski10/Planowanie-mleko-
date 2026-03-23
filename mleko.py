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
                if n['Typ'] == "L
            
        styled_df = df_wyswietl.style.applymap(stylizuj_odchylenie, subset=['Odchylenie (L/kg)'])
        st.dataframe(styled_df, use_container_width=True, hide_index=True)
