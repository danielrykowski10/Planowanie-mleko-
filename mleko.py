import streamlit as st
import pandas as pd
import datetime
import json
import os

# --- KONFIGURACJA STRONY ---
st.set_page_config(page_title="Strażnik Uzysku", layout="wide")

# --- BAZA DANYCH ---
PLIK_UZYSKU = "dane_uzysk.json"

def wczytaj_dane():
    if os.path.exists(PLIK_UZYSKU):
        try:
            with open(PLIK_UZYSKU, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def zapisz_dane(dane):
    with open(PLIK_UZYSKU, "w", encoding="utf-8") as f:
        json.dump(dane, f, ensure_ascii=False, indent=4)

if 'historia_uzysku' not in st.session_state:
    st.session_state.historia_uzysku = wczytaj_dane()

# --- STYLIZACJA ---
st.markdown("""
    <style>
        .metric-box { background-color: #f8f9fa; border: 1px solid #ddd; border-radius: 8px; padding: 15px; text-align: center; }
        .success-box { background-color: #e8f5e9; border: 1px solid #c8e6c9; border-radius: 8px; padding: 15px; text-align: center; color: #2e7d32; font-weight: bold; margin-bottom: 10px;}
        .alert-box { background-color: #ffebee; border: 1px solid #ffcdd2; border-radius: 8px; padding: 15px; text-align: center; color: #b71c1c; font-weight: bold; margin-bottom: 10px;}
        .warning-box { background-color: #fff3e0; border: 1px solid #ffcc80; border-radius: 8px; padding: 15px; text-align: center; color: #e65100; font-weight: bold; margin-bottom: 10px;}
    </style>
""", unsafe_allow_html=True)

# --- ZAKŁADKI ---
tab1, tab2 = st.tabs(["📝 Rejestr Warki (Aparatownia & Serownia)", "📈 Analiza Uzysków dla Kierownika"])

# --- NORMY ZAKŁADOWE (Domyślne cele: ile L mleka na 1 kg sera) ---
CELE_UZYSKU = {
    "Gouda": 10.0,
    "Cheddar": 9.8,
    "Mozzarella": 9.5
}

# ==========================================
# ZAKŁADKA 1: WPROWADZANIE DANYCH
# ==========================================
with tab1:
    st.title("🧀 Rejestr Produkcyjny (Warka)")
    
    with st.form("formularz_warki", clear_on_submit=True):
        col_podstawowe, col_aparatownia, col_serownia = st.columns(3)
        
        with col_podstawowe:
            st.markdown("### 📋 Identyfikacja")
            data_warki = st.date_input("Data produkcji", datetime.date.today())
            nr_warki = st.text_input("Numer warki / kotła", placeholder="np. W-01/26")
            rodzaj_sera = st.selectbox("Rodzaj sera", ["Gouda", "Cheddar", "Mozzarella"])
            
        with col_aparatownia:
            st.markdown("### 🥛 Dane: Aparatownia")
            mleko_l = st.number_input("Zalane mleko (LITRY)", min_value=0, value=10000, step=500)
            tluszcz = st.number_input("Tłuszcz w mleku (%)", min_value=0.0, max_value=10.0, value=3.20, step=0.05)
            bialko = st.number_input("Białko w mleku (%)", min_value=0.0, max_value=10.0, value=3.30, step=0.05)
            
        with col_serownia:
            st.markdown("### ⚖️ Dane: Serownia")
            ser_kg = st.number_input("Uzyskany ser (KG)", min_value=0.0, value=1000.0, step=10.0)
            wilgotnosc = st.number_input("Wilgotność sera (%)", min_value=0.0, max_value=60.0, value=43.0, step=0.5)
            
        zapisz_btn = st.form_submit_button("💾 ZAPISZ WARKĘ", type="primary")
        
        if zapisz_btn:
            if nr_warki == "":
                st.error("Podaj numer warki!")
            elif ser_kg == 0 or mleko_l == 0:
                st.error("Ilość mleka i sera musi być większa od 0!")
            else:
                dane_data = data_warki.strftime("%Y-%m-%d")
                nowy_wpis = {
                    "Data": dane_data,
                    "Warka": nr_warki,
                    "Ser": rodzaj_sera,
                    "Mleko_L": mleko_l,
                    "Tluszcz_%": tluszcz,
                    "Bialko_%": bialko,
                    "Ser_kg": ser_kg,
                    "Wilgotnosc_%": wilgotnosc
                }
                
                # Dodajemy lub aktualizujemy
                istniejacy_indeks = next((i for i, v in enumerate(st.session_state.historia_uzysku) if v["Data"] == dane_data and v["Warka"] == nr_warki), None)
                if istniejacy_indeks is not None:
                    st.session_state.historia_uzysku[istniejacy_indeks] = nowy_wpis
                    st.success(f"Zaktualizowano warkę {nr_warki}.")
                else:
                    st.session_state.historia_uzysku.append(nowy_wpis)
                    st.success(f"Dodano warkę {nr_warki}.")
                    
                zapisz_dane(st.session_state.historia_uzysku)
                st.rerun()

# ==========================================
# ZAKŁADKA 2: ANALIZA DLA KIEROWNIKA
# ==========================================
with tab2:
    st.title("📊 Panel Kontroli Uzysków")
    
    with st.sidebar:
        st.header("⚙️ Cele Uzysku (L/kg)")
        cel_gouda = st.number_input("Cel Gouda (L/kg)", value=CELE_UZYSKU["Gouda"], step=0.1)
        cel_cheddar = st.number_input("Cel Cheddar (L/kg)", value=CELE_UZYSKU["Cheddar"], step=0.1)
        cel_mozzarella = st.number_input("Cel Mozzarella (L/kg)", value=CELE_UZYSKU["Mozzarella"], step=0.1)
        CELE_UZYSKU = {"Gouda": cel_gouda, "Cheddar": cel_cheddar, "Mozzarella": cel_mozzarella}
    
    if not st.session_state.historia_uzysku:
        st.info("Brak danych do analizy. Dodaj warkę w pierwszej zakładce.")
    else:
        df = pd.DataFrame(st.session_state.historia_uzysku)
        
        # OBLICZANIE KLUCZOWEGO WSKAŹNIKA (KPI)
        df['Uzysk (L/kg)'] = (df['Mleko_L'] / df['Ser_kg']).round(2)
        df['Cel (L/kg)'] = df['Ser'].map(CELE_UZYSKU)
        df['Odchylenie (L/kg)'] = (df['Uzysk (L/kg)'] - df['Cel (L/kg)']).round(2)
        
        # Najnowsza warka do szybkiego podglądu
        ost = df.iloc[-1]
        
        st.subheader(f"Ostatnia warka: {ost['Warka']} ({ost['Ser']}) z dnia {ost['Data']}")
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Mleko pobrane", f"{ost['Mleko_L']} L")
        c2.metric("Ser wyprodukowany", f"{ost['Ser_kg']} kg")
        
        # Kolorowanie delty uzysku (im mniejsze L/kg tym lepiej, więc odwracamy kolory)
        delta_uzysk = ost['Odchylenie (L/kg)']
        c3.metric("Rzeczywiste zużycie", f"{ost['Uzysk (L/kg)']} L/kg", delta=f"{delta_uzysk} od celu", delta_color="inverse")
        
        # Szacowana strata/zysk mleka na tej jednej warce
        strata_mleka = delta_uzysk * ost['Ser_kg']
        if strata_mleka > 0:
            c4.metric("Strata mleka na warce", f"-{abs(strata_mleka):.0f} L", "Straty wyłapane", delta_color="inverse")
        else:
            c4.metric("Zaoszczędzone mleko", f"+{abs(strata_mleka):.0f} L", "Zysk ponad normę", delta_color="normal")

        # --- ASYSTENT AI DLA KIEROWNIKA ---
        st.markdown("<br>", unsafe_allow_html=True)
        
        if delta_uzysk > 0.2: # Znacząca strata
            st.markdown(f"""
                <div class="alert-box">
                    🚨 ALARM UZYSKU! Zmarnowaliście ok. {abs(strata_mleka):.0f} litrów mleka na tej warce w stosunku do normy!
                </div>
            """, unsafe_allow_html=True)
            
            st.markdown("**🤖 Wnioski Asystenta Technologa:**")
            if ost['Tluszcz_%'] > 3.2 and ost['Ser'] == "Mozzarella":
                st.warning("⚠️ **Podejrzenie: Tłuszcz w serwatce.** Mleko było bogate w tłuszcz, a uzysk Mozzarelli spadł. Prawdopodobnie skrzep był cięty za wcześnie lub za szybko mieszany. Sprawdź wyniki tłuszczu w wirówce serwatkowej na WPC!")
            if ost['Wilgotnosc_%'] < 40.0:
                st.warning("⚠️ **Podejrzenie: Ser przepracowany (zbyt suchy).** Wilgotność spadła poniżej normy. Sprzedajecie za dużo suchej masy, a za mało wody. Zrewidujcie czas dosuszania ziarna w kotle.")
        elif delta_uzysk < -0.1:
            st.markdown(f"""
                <div class="success-box">
                    ✅ WZOROWY UZYSK! Oszczędność {abs(strata_mleka):.0f} litrów mleka na jednej warce. 
                </div>
            """, unsafe_allow_html=True)
            if ost['Wilgotnosc_%'] > 45.0 and ost['Ser'] == "Gouda":
                st.info("💡 **Uwaga do jakości:** Świetny wynik ilościowy, ale wilgotność Goudy jest wysoka. Zwróćcie uwagę, czy ser nie będzie 'płakał' w dojrzewalni lub czy nie zakwasi się za mocno pod prasami.")
        else:
            st.markdown("<div class='success-box'>✅ Proces stabilny. Zużycie mleka zgadza się z normą zakładową.</div>", unsafe_allow_html=True)

        st.divider()

        # --- WYKRESY I HISTORIA ---
        st.subheader("📉 Trendy Zużycia Mleka na 1 kg Sera")
        
        # Filtrujemy dane do wykresów, żeby rozdzielić sery
        pivot_df = df.pivot(index='Data', columns='Ser', values='Uzysk (L/kg)')
        st.line_chart(pivot_df)
        
        st.markdown("#### 📋 Pełen Rejestr Warek")
        cols_to_show = ['Data', 'Warka', 'Ser', 'Mleko_L', 'Tluszcz_%', 'Bialko_%', 'Ser_kg', 'Wilgotnosc_%', 'Uzysk (L/kg)', 'Odchylenie (L/kg)']
        df_wyswietl = df[cols_to_show].sort_values(by=['Data', 'Warka'], ascending=[False, False])
        
        # Stylizacja tabeli (kolorowanie odchyleń)
        def stylizuj_odchylenie(val):
            color = '#ffebee' if val > 0.1 else ('#e8f5e9' if val < 0 else '')
            text_color = '#b71c1c' if val > 0.1 else ('#2e7d32' if val < 0 else '')
            if color:
                return f'background-color: {color}; color: {text_color}; font-weight: bold;'
            return ''
            
        styled_df = df_wyswietl.style.applymap(stylizuj_odchylenie, subset=['Odchylenie (L/kg)'])
        st.dataframe(styled_df, use_container_width=True, hide_index=True)
