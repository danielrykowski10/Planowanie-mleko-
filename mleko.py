import customtkinter as ctk
import json
from datetime import datetime

# Konfiguracja wyglądu
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

class AkademiaOdkrywcy(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Akademia Odkrywcy - v1.0")
        self.geometry("600x500")
        
        # Prosta "baza danych" w pamięci (warto zapisać do pliku .json)
        self.historia_bledow = []
        
        self.ekran_glowny()

    def ekran_glowny(self):
        self.wyczysc_okno()
        ctk.CTkLabel(self, text="Cześć! Co dzisiaj robimy?", font=("Arial", 24, "bold")).pack(pady=20)
        
        # Przyciski dla dziecka
        ctk.CTkButton(self, text="🧮 Matematyka", fg_color="#4CAF50", command=self.quiz_matematyczny).pack(pady=10)
        ctk.CTkButton(self, text="🇵🇱 Język Polski", fg_color="#FF5722", state="disabled").pack(pady=10) # Do rozbudowy
        ctk.CTkButton(self, text="🇬🇧 Angielski", fg_color="#2196F3", state="disabled").pack(pady=10)   # Do rozbudowy
        
        # Przycisk dla rodzica
        ctk.CTkButton(self, text="🔑 Panel Rodzica", fg_color="gray", command=self.panel_rodzica).pack(side="bottom", pady=20)

    def quiz_matematyczny(self):
        self.wyczysc_okno()
        pytanie = "Ile to jest 12 + 15?"
        poprawna = 27
        
        ctk.CTkLabel(self, text="Zadanie:", font=("Arial", 18)).pack(pady=10)
        ctk.CTkLabel(self, text=pytanie, font=("Arial", 32, "bold")).pack(pady=20)
        
        self.odp_entry = ctk.CTkEntry(self, placeholder_text="Twoja odpowiedź...")
        self.odp_entry.pack(pady=10)
        
        ctk.CTkButton(self, text="Sprawdź!", command=lambda: self.sprawdz_matme(pytanie, poprawna)).pack(pady=10)

    def sprawdz_matme(self, pytanie, poprawna):
        try:
            user_input = int(self.odp_entry.get())
            if user_input == poprawna:
                print("Brawo!")
                self.ekran_glowny()
            else:
                # Zapisywanie błędu do historii
                self.historia_bledow.append({
                    "data": datetime.now().
