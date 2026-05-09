import customtkinter as ctk
from tkinter import filedialog
import os
import shutil
import time
import threading
from PIL import Image

# Theme settings
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# File categories
CATEGORIES = {
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp"],
    "Documents": [".pdf", ".doc", ".docx", ".txt", ".xlsx", ".csv"],
    "Videos": [".mp4", ".avi", ".mkv", ".mov", ".wmv"],
    "Music": [".mp3", ".wav", ".flac", ".aac"],
    "Archives": [".zip", ".rar", ".tar", ".gz"],
    "Programs": [".exe", ".deb", ".sh", ".AppImage"],
}

selected_folder = None
move_history = []

# Main window
app = ctk.CTk()
app.title("FolderMate - File Organizer")
from PIL import ImageTk
icon = ImageTk.PhotoImage(Image.open("icon.png"))
app.iconphoto(True, icon)
app.geometry("600x580")

# Title
title = ctk.CTkLabel(app, text="📁 FolderMate", font=ctk.CTkFont(size=24, weight="bold"))
title.pack(pady=20)

subtitle = ctk.CTkLabel(app, text="Organize your files automatically", font=ctk.CTkFont(size=14))
subtitle.pack(pady=5)

# Folder label
folder_label = ctk.CTkLabel(app, text="No folder selected", font=ctk.CTkFont(size=13))
folder_label.pack(pady=10)

# Progress bar
progress = ctk.CTkProgressBar(app, width=400)
progress.pack(pady=10)
progress.set(0)

# Result label
result_label = ctk.CTkLabel(app, text="", font=ctk.CTkFont(size=13), wraplength=500)
result_label.pack(pady=10)

# Select folder function
def select_folder():
    global selected_folder
    folder = filedialog.askdirectory()
    if folder:
        selected_folder = folder
        folder_label.configure(text=f"📂 {folder}")
        result_label.configure(text="")
        progress.set(0)
        undo_button.configure(state="disabled")

# Organize function
def organize_thread():
    global move_history
    if not selected_folder:
        result_label.configure(text="⚠️ Please select a folder first!")
        return

    files = [f for f in os.listdir(selected_folder) if os.path.isfile(os.path.join(selected_folder, f))]
    total = len(files)

    if total == 0:
        result_label.configure(text="⚠️ The folder is empty!")
        return

    move_history = []
    moved = 0

    for file in files:
        old_path = os.path.join(selected_folder, file)
        extension = os.path.splitext(file)[1].lower()

        category = "Others"
        for cat, extensions in CATEGORIES.items():
            if extension in extensions:
                category = cat
                break

        dest_folder = os.path.join(selected_folder, category)
        os.makedirs(dest_folder, exist_ok=True)
        new_path = os.path.join(dest_folder, file)
        shutil.move(old_path, new_path)

        move_history.append((new_path, old_path))
        moved += 1
        progress.set(moved / total)
        result_label.configure(text=f"⏳ Organizing... {moved}/{total}")
        time.sleep(0.05)

    result_label.configure(text=f"✅ Done! {moved} files organized!")
    undo_button.configure(state="normal")

def organize():
    thread = threading.Thread(target=organize_thread)
    thread.daemon = True
    thread.start()

# Undo function
def undo():
    if not move_history:
        result_label.configure(text="⚠️ Nothing to undo!")
        return

    for new_path, old_path in reversed(move_history):
        if os.path.exists(new_path):
            shutil.move(new_path, old_path)

    for category in CATEGORIES.keys():
        cat_folder = os.path.join(selected_folder, category)
        if os.path.exists(cat_folder) and not os.listdir(cat_folder):
            os.rmdir(cat_folder)
    others_folder = os.path.join(selected_folder, "Others")
    if os.path.exists(others_folder) and not os.listdir(others_folder):
        os.rmdir(others_folder)

    progress.set(0)
    result_label.configure(text="↩️ Undone! Files restored to original location.")
    undo_button.configure(state="disabled")

# Buttons
select_button = ctk.CTkButton(app, text="📂 Select Folder", width=200, height=50, command=select_folder)
select_button.pack(pady=10)

organize_button = ctk.CTkButton(app, text="✨ Organize!", width=200, height=50,
                                 fg_color="green", hover_color="darkgreen",
                                 command=organize)
organize_button.pack(pady=10)

undo_button = ctk.CTkButton(app, text="↩️ Undo", width=200, height=50,
                             fg_color="gray", hover_color="darkgray",
                             command=undo, state="disabled")
undo_button.pack(pady=10)

# Start app
app.mainloop()
