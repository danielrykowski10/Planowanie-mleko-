import streamlit as st
import pandas as pd
import datetime
import json
import os

# --- KONFIGURACJA STRONY ---
st.set_page_config(page_title="Strażnik Uzysku - Partie", layout="wide")

# --- BAZA DANYCH ---
PLIK_UZYSKU = "dane_uzysk_partie.json"

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
tab1, tab2 = st.tabs(["📝 Rejestr Partii (Aparatownia & Serownia)", "📈 Analiza Uzysków dla Kierownika"])

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
    st.title("🧀 Rejestr Produkcyjny (Cała Partia)")
    
    with st.form("formularz_partii", clear_on_submit=True):
        col_podstawowe, col_aparatownia, col_serownia = st.columns(3)
        
        with col_podstawowe:
            st.markdown("### 📋 Identyfikacja Partii")
            data_partii = st.date_input("Data produkcji", datetime.date.today())
            nr_partii = st.text_input("Numer partii / zmiany", placeholder="np. P-01/26")
            rodzaj_sera = st.selectbox("Rodzaj sera", ["Gouda", "Cheddar", "Mozzarella"])
            ilosc_warek = st.number_input("Ilość warek w tej partii", min_value=1, value=10, step=1)
            
        with col_aparatownia:
            st.markdown("### 🥛 Dane: Aparatownia")
            mleko_tys_l = st.number_input("Całe pobrane mleko (w tys. litrów)", min_value=0.0, value=100.0, step=5.0, help="Wpisz np. 100 dla 100 000 litrów")
            tluszcz = st.number_input("Średni tłuszcz w mleku (%)", min_value=0.0, max_value=10.0, value=3.20, step=0.05)
            bialko = st.number_input("Średnie białko w mleku (%)", min_value=0.0, max_value=10.0, value=3.30, step=0.05)
            
        with col_serownia:
            st.markdown("### ⚖️ Dane: Serownia")
            ser_kg = st.number_input("Łączny uzyskany ser (KG)", min_value=0.0, value=10000.0, step=100.0)
            wilgotnosc = st.number_input("Średnia wilgotność sera (%)", min_value=0.0, max_value=60.0, value=43.0, step=0.5)
            
        zapisz_btn = st.form_submit_button("💾 ZAPISZ PARTIĘ", type="primary")
        
        if zapisz_btn:
            if nr_partii == "":
                st.error("Podaj numer partii!")
            elif ser_kg == 0 or mleko_tys_l == 0:
                st.error("Ilość mleka i sera musi być większa od 0!")
            else:
                dane_data = data_partii.strftime("%Y-%m-%d")
                mleko_l_rzeczywiste = mleko_tys_l * 1000
                
                nowy_wpis = {
                    "Data": dane_data,
                    "Partia": nr_partii,
                    "Ser": rodzaj_sera,
                    "Ilosc_warek": ilosc_warek,
                    "Mleko_L": mleko_l_rzeczywiste,
                    "Tluszcz_%": tluszcz,
                    "Bialko_%": bialko,
                    "Ser_kg": ser_kg,
                    "Wilgotnosc_%": wilgotnosc
                }
                
                istniejacy_indeks = next((i for i, v in enumerate(st.session_state.historia_uzysku) if v["Data"] == dane_data and v["Partia"] == nr_partii), None)
                if istniejacy_indeks is not None:
                    st.session_state.historia_uzysku[istniejacy_indeks] = nowy_wpis
                    st.success(f"Zaktualizowano partię {nr_partii}.")
                else:
                    st.session_state.historia_uzysku.append(nowy_wpis)
                    st.success(f"Dodano partię {nr_partii}.")
                    
                zapisz_dane(st.session_state.historia_uzysku)
                st.rerun()

# ==========================================
# ZAKŁADKA 2: ANALIZA DLA KIEROWNIKA
# ==========================================
with tab2:
    st.title("📊 Panel Kontroli Uzysków z Całych Partii")
    
    with st.sidebar:
        st.header("⚙️ Cele Uzysku (L/kg)")
        cel_gouda = st.number_input("Cel Gouda (L/kg)", value=CELE_UZYSKU["Gouda"], step=0.1)
        cel_cheddar = st.number_input("Cel Cheddar (L/kg)", value=CELE_UZYSKU["Cheddar"], step=0.1)
        cel_mozzarella = st.number_input("Cel Mozzarella (L/kg)", value=CELE_UZYSKU["Mozzarella"], step=0.1)
        CELE_UZYSKU = {"Gouda": cel_gouda, "Cheddar": cel_cheddar, "Mozzarella": cel_mozzarella}
    
    if not st.session_state.historia_uzysku:
        st.info("Brak danych do analizy. Dodaj partię w pierwszej zakładce.")
    else:
        df = pd.DataFrame(st.session_state.historia_uzysku)
        
        # OBLICZANIE KLUCZOWYCH WSKAŹNIKÓW (KPI)
        df['Uzysk (L/kg)'] = (df['Mleko_L'] / df['Ser_kg']).round(2)
        df['Cel (L/kg)'] = df['Ser'].map(CELE_UZYSKU)
        df['Odchylenie (L/kg)'] = (df['Uzysk (L/kg)'] - df['Cel (L/kg)']).round(2)
        df['Mleko_tys_L'] = df['Mleko_L'] / 1000
        df['Srednio_ser_na_warke'] = (df['Ser_kg'] / df['Ilosc_warek']).round(1)
        
        # Najnowsza partia do szybkiego podglądu
        ost = df.iloc[-1]
        
        st.subheader(f"Ostatnia partia: {ost['Partia']} ({ost['Ser']}, {ost['Ilosc_warek']} warek) z dnia {ost['Data']}")
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Mleko pobrane (Suma)", f"{ost['Mleko_tys_L']} tys. L")
        c2.metric("Ser wyprodukowany (Suma)", f"{ost['Ser_kg']} kg", f"Śr. {ost['Srednio_ser_na_warke']} kg/warkę", delta_color="off")
        
        delta_uzysk = ost['Odchylenie (L/kg)']
        c3.metric("Średni Uzysk z Partii", f"{ost['Uzysk (L/kg)']} L/kg", delta=f"{delta_uzysk} od celu", delta_color="inverse")
        
        # Szacowana strata/zysk mleka na CAŁEJ PARTII
        strata_mleka = delta_uzysk * ost['Ser_kg']
        if strata_mleka > 0:
            c4.metric("Strata mleka na partii", f"-{abs(strata_mleka):.0f} L", "Ogromne koszty!", delta_color="inverse")
        else:
            c4.metric("Zaoszczędzone mleko", f"+{abs(strata_mleka):.0f} L", "Zysk ponad normę!", delta_color="normal")

        # --- ASYSTENT AI DLA KIEROWNIKA ---
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Bezpieczne składanie HTML dla ostrzeżeń
        if delta_uzysk > 0.2: 
            alert_html = f"<div style='background-color:#ffebee; border:1px solid #ffcdd2; border-radius:8px; padding:15px; text-align:center; color:#b71c1c; font-weight:bold; margin-bottom:10px;'>"
            alert_html += f"🚨 ALARM UZYSKU DLA CAŁEJ PARTII! Zmarnowaliście ok. {abs(strata_mleka):.0f} litrów mleka w stosunku do normy na tych {ost['Ilosc_warek']} warkach!"
            alert_html += "</div>"
            st.markdown(alert_html, unsafe_allow_html=True)
            
            st.markdown("**🤖 Wnioski Asystenta Technologa:**")
            if ost['Tluszcz_%'] > 3.2 and ost['Ser'] == "Mozzarella":
                st.warning("⚠️ **Podejrzenie: Tłuszcz w serwatce.** Mleko z aparatowni było bogate w tłuszcz, a uzysk Mozzarelli na całej zmianie spadł. Zrewiduj proces cięcia skrzepu – kruszycie ziarno i tłuszcz ucieka do serwatki!")
            if ost['Wilgotnosc_%'] < 40.0:
                st.warning("⚠️ **Podejrzenie: Ser przesuszony.** Wilgotność na partii spadła poniżej normy. Sprzedajecie za dużo białka, a za mało wody. Skróćcie czas dosuszania w kotłach.")
                
        elif delta_uzysk < -0.1:
            succ_html = f"<div style='background-color:#e8f5e9; border:1px solid #c8e6c9; border-radius:8px; padding:15px; text-align:center; color:#2e7d32; font-weight:bold; margin-bottom:10px;'>"
            succ_html += f"✅ WZOROWY UZYSK! Oszczędność {abs(strata_mleka):.0f} litrów mleka na tej partii."
            succ_html += "</div>"
            st.markdown(succ_html, unsafe_allow_html=True)
            
            if ost['Wilgotnosc_%'] > 45.0 and ost['Ser'] == "Gouda":
                st.info("💡 **Uwaga do jakości:** Świetny wynik ilościowy, ale wilgotność Goudy jest bardzo wysoka. Sprawdźcie na magazynie, czy bloki nie 'płaczą' lub nie kwaśnieją.")
        else:
            st.markdown("<div style='background-color:#e8f5e9; border:1px solid #c8e6c9; border-radius:8px; padding:15px; text-align:center; color:#2e7d32; font-weight:bold;'>✅ Proces stabilny. Zużycie mleka w partii zgadza się z normą zakładową.</div>", unsafe_allow_html=True)

        st.divider()

        # --- WYKRESY I HISTORIA ---
        st.subheader("📉 Trendy Zużycia Mleka na 1 kg Sera (Całe Partie)")
        
        pivot_df = df.pivot(index='Data', columns='Ser', values='Uzysk (L/kg)')
        st.line_chart(pivot_df)
        
        st.markdown("#### 📋 Pełen Rejestr Partii")
        cols_to_show = ['Data', 'Partia', 'Ser', 'Ilosc_warek', 'Mleko_tys_L', 'Tluszcz_%', 'Bialko_%', 'Ser_kg', 'Wilgotnosc_%', 'Uzysk (L/kg)', 'Odchylenie (L/kg)']
        df_wyswietl = df[cols_to_show].sort_values(by=['Data', 'Partia'], ascending=[False, False])
        
        # Funkcja do kolorowania odchyleń
        def stylizuj_odchylenie(val):
            color = '#ffebee' if val > 0.1 else ('#e8f5e9' if val < 0 else '')
            text_color = '#b71c1c' if val > 0.1 else ('#2e7d32' if val < 0 else '')
            if color:
                return f'background-color: {color}; color: {text_color}; font-weight: bold;'
            return ''
            
        styled_df = df_wyswietl.style.applymap(stylizuj_odchylenie, subset=['Odchylenie (L/kg)'])
        st.dataframe(styled_df, use_container_width=True, hide_index=True)
