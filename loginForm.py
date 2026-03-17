import sqlite3
import customtkinter as ctk
from tkinter import messagebox
import dashboard

# -------------------- Database --------------------
conn = sqlite3.connect("ERP_Billing.db")
cursor = conn.cursor()

# -------------------- App Settings --------------------
ctk.set_appearance_mode("dark")     # Modes: "light", "dark", "system"
ctk.set_default_color_theme("blue") # Themes: "blue", "green", "dark-blue"

# -------------------- Main Window --------------------
root = ctk.CTk()
root.title("ERP Login")
root.geometry("400x400")
root.resizable(False, False)

# -------------------- Login Function --------------------
def user_login():
    user_name = entry_username.get()
    password = entry_password.get()

    cursor.execute(
        "SELECT * FROM account WHERE user_name=? AND password=?",
        (user_name, password)
    )

    result = cursor.fetchone()

    if result:
        root.destroy()
        dashboard.open_dashboard()
    else:
        messagebox.showerror("Error", "Invalid Username or Password!")

# -------------------- UI Design --------------------

# Title
title_label = ctk.CTkLabel(
    root, 
    text="ERP Billing System",
    font=ctk.CTkFont(size=22, weight="bold")
)
title_label.pack(pady=20)

subtitle_label = ctk.CTkLabel(
    root,
    text="User Login",
    font=ctk.CTkFont(size=16)
)
subtitle_label.pack(pady=5)

# Username Entry
entry_username = ctk.CTkEntry(
    root,
    placeholder_text="Enter Username",
    width=250,
    height=35
)
entry_username.pack(pady=15)
entry_username.insert(ctk.END, "j")

# Password Entry
entry_password = ctk.CTkEntry(
    root,
    placeholder_text="Enter Password",
    show="*",
    width=250,
    height=35
)
entry_password.pack(pady=15)
entry_password.insert(ctk.END, "j")

# Login Button
login_button = ctk.CTkButton(
    root,
    text="Login",
    command=user_login,
    width=200,
    height=40,
    corner_radius=10
)
login_button.pack(pady=20)

# Footer
footer_label = ctk.CTkLabel(
    root,
    text="© 2026 ERP System | ITHub",
    font=ctk.CTkFont(size=10)
)
footer_label.pack(side="bottom", pady=10)

# -------------------- Run App --------------------
root.mainloop()