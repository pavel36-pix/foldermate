import customtkinter as ctk
from tkinter import filedialog
import os
import shutil
import time
import threading

# Setări temă
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Categorii de fișiere
CATEGORII = {
    "Imagini": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp"],
    "Documente": [".pdf", ".doc", ".docx", ".txt", ".xlsx", ".csv"],
    "Videoclipuri": [".mp4", ".avi", ".mkv", ".mov", ".wmv"],
    "Muzică": [".mp3", ".wav", ".flac", ".aac"],
    "Arhive": [".zip", ".rar", ".tar", ".gz"],
    "Programe": [".exe", ".deb", ".sh", ".AppImage"],
}

folder_ales = None
istoric_mutari = []  # Lista cu toate mutările făcute

# Fereastra principală
app = ctk.CTk()
app.title("Organizator Fișiere")
app.geometry("600x580")

# Titlu
titlu = ctk.CTkLabel(app, text="📁 Organizator Fișiere", font=ctk.CTkFont(size=24, weight="bold"))
titlu.pack(pady=30)

# Label folder ales
folder_label = ctk.CTkLabel(app, text="Niciun folder ales", font=ctk.CTkFont(size=14))
folder_label.pack(pady=10)

# Progress bar
progress = ctk.CTkProgressBar(app, width=400)
progress.pack(pady=10)
progress.set(0)

# Label rezultat
rezultat_label = ctk.CTkLabel(app, text="", font=ctk.CTkFont(size=13), wraplength=500)
rezultat_label.pack(pady=10)

# Funcție alegere folder
def alege_folder():
    global folder_ales
    folder = filedialog.askdirectory()
    if folder:
        folder_ales = folder
        folder_label.configure(text=f"📂 {folder}")
        rezultat_label.configure(text="")
        progress.set(0)
        buton_undo.configure(state="disabled")

# Funcție organizare
def organizeaza_thread():
    global istoric_mutari
    if not folder_ales:
        rezultat_label.configure(text="⚠️ Alege un folder mai întâi!")
        return

    fisiere = [f for f in os.listdir(folder_ales) if os.path.isfile(os.path.join(folder_ales, f))]
    total = len(fisiere)

    if total == 0:
        rezultat_label.configure(text="⚠️ Folderul este gol!")
        return

    istoric_mutari = []  # Resetăm istoricul
    mutat = 0

    for fisier in fisiere:
        cale_veche = os.path.join(folder_ales, fisier)
        extensie = os.path.splitext(fisier)[1].lower()

        categorie = "Altele"
        for cat, extensii in CATEGORII.items():
            if extensie in extensii:
                categorie = cat
                break

        folder_destinatie = os.path.join(folder_ales, categorie)
        os.makedirs(folder_destinatie, exist_ok=True)
        cale_noua = os.path.join(folder_destinatie, fisier)
        shutil.move(cale_veche, cale_noua)

        # Salvăm mutarea în istoric
        istoric_mutari.append((cale_noua, cale_veche))

        mutat += 1
        progress.set(mutat / total)
        rezultat_label.configure(text=f"⏳ Se organizează... {mutat}/{total}")
        time.sleep(0.05)

    rezultat_label.configure(text=f"✅ Gata! {mutat} fișiere organizate!")
    buton_undo.configure(state="normal")  # Activăm butonul Undo

def organizeaza():
    thread = threading.Thread(target=organizeaza_thread)
    thread.daemon = True
    thread.start()

# Funcție Undo
def undo():
    if not istoric_mutari:
        rezultat_label.configure(text="⚠️ Nimic de anulat!")
        return

    for cale_noua, cale_veche in reversed(istoric_mutari):
        if os.path.exists(cale_noua):
            shutil.move(cale_noua, cale_veche)

    # Șterge folderele goale
    for categorie in CATEGORII.keys():
        folder_cat = os.path.join(folder_ales, categorie)
        if os.path.exists(folder_cat) and not os.listdir(folder_cat):
            os.rmdir(folder_cat)
    folder_altele = os.path.join(folder_ales, "Altele")
    if os.path.exists(folder_altele) and not os.listdir(folder_altele):
        os.rmdir(folder_altele)

    progress.set(0)
    rezultat_label.configure(text="↩️ Anulat! Fișierele sunt înapoi la loc.")
    buton_undo.configure(state="disabled")

# Butoane
buton_alege = ctk.CTkButton(app, text="📂 Alege Folder", width=200, height=50, command=alege_folder)
buton_alege.pack(pady=10)

buton_organizeaza = ctk.CTkButton(app, text="✨ Organizează!", width=200, height=50,
                                   fg_color="green", hover_color="darkgreen",
                                   command=organizeaza)
buton_organizeaza.pack(pady=10)

buton_undo = ctk.CTkButton(app, text="↩️ Anulează", width=200, height=50,
                            fg_color="gray", hover_color="darkgray",
                            command=undo, state="disabled")
buton_undo.pack(pady=10)

# Pornește aplicația
app.mainloop()
