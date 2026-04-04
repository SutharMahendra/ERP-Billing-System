import tkinter as tk
from tkinter import messagebox
import sqlite3
import dashboard

# ─── Color Palette (matches dashboard) ───────────────────────────────────────
C_BG      = "#0f1117"
C_CARD    = "#1c2230"
C_ACCENT  = "#00d4aa"
C_ACCENT2 = "#4f8ef7"
C_TEXT    = "#e8eaf0"
C_MUTED   = "#7a8499"
C_HEADER  = "#12192b"
C_BORDER  = "#2a3345"
C_INPUT   = "#242d3d"
C_HOVER   = "#00b894"
C_ERROR   = "#f7604f"

# ─── Database ─────────────────────────────────────────────────────────────────
conn   = sqlite3.connect("ERP_Billing.db")
cursor = conn.cursor()

# ═══════════════════════════════════════════════════════════════════════════════
# FUNCTION
# ═══════════════════════════════════════════════════════════════════════════════

def user_login():
    user_name = entry_username.get().strip()
    password  = entry_password.get().strip()

    if not user_name or not password:
        shake_window()
        status_label.config(text="Please enter username and password.", fg=C_ERROR)
        return

    cursor.execute(
        "SELECT * FROM account WHERE user_name=? AND password=?",
        (user_name, password)
    )
    result = cursor.fetchone()

    if result:
        root.destroy()
        dashboard.open_dashboard()
    else:
        shake_window()
        status_label.config(text="Invalid username or password.", fg=C_ERROR)
        entry_password.delete(0, tk.END)
        entry_password.focus()

def shake_window():
    """Horizontal shake animation on failed login."""
    x0 = root.winfo_x()
    y0 = root.winfo_y()
    offsets = [10, -10, 8, -8, 5, -5, 2, -2, 0]

    def step(i=0):
        if i < len(offsets):
            root.geometry(f"+{x0 + offsets[i]}+{y0}")
            root.after(30, step, i + 1)

    step()

def toggle_password():
    if entry_password.cget("show") == "*":
        entry_password.config(show="")
        eye_btn.config(text="🙈")
    else:
        entry_password.config(show="*")
        eye_btn.config(text="👁")

def on_entry_focus_in(entry, placeholder):
    if entry.get() == placeholder:
        entry.delete(0, tk.END)
        entry.config(fg=C_TEXT)

def on_entry_focus_out(entry, placeholder):
    if entry.get().strip() == "":
        entry.insert(0, placeholder)
        entry.config(fg=C_MUTED)

def on_hover_in(btn, color):
    btn.config(bg=color)

def on_hover_out(btn, color):
    btn.config(bg=color)

# ═══════════════════════════════════════════════════════════════════════════════
# WINDOW
# ═══════════════════════════════════════════════════════════════════════════════
root = tk.Tk()
root.title("ERP Billing System – Login")
root.resizable(False, False)
root.configure(bg=C_BG)

# Center window
W, H = 420, 520
root.update_idletasks()
sw = root.winfo_screenwidth()
sh = root.winfo_screenheight()
root.geometry(f"{W}x{H}+{(sw - W)//2}+{(sh - H)//2}")

# ═══════════════════════════════════════════════════════════════════════════════
# GUI
# ═══════════════════════════════════════════════════════════════════════════════

# ── Top accent bar ────────────────────────────────────────────────────────────
tk.Frame(root, bg=C_ACCENT, height=4).pack(fill=tk.X)

# ── Logo / brand block ────────────────────────────────────────────────────────
brand_frame = tk.Frame(root, bg=C_BG)
brand_frame.pack(pady=(36, 0))

dot_canvas = tk.Canvas(brand_frame, width=48, height=48,
                       bg=C_BG, highlightthickness=0)
dot_canvas.pack()
dot_canvas.create_oval(4, 4, 44, 44, fill=C_ACCENT, outline="")
dot_canvas.create_text(24, 24, text="E", fill=C_BG,
                       font=("Segoe UI", 20, "bold"))

tk.Label(root, text="ERP Billing System",
         font=("Segoe UI", 20, "bold"),
         bg=C_BG, fg=C_TEXT).pack(pady=(12, 2))

tk.Label(root, text="Sign in to your account",
         font=("Segoe UI", 10),
         bg=C_BG, fg=C_MUTED).pack()

# ── Card ──────────────────────────────────────────────────────────────────────
card = tk.Frame(root, bg=C_CARD,
                highlightbackground=C_BORDER, highlightthickness=1)
card.pack(padx=40, pady=28, fill=tk.X)

tk.Frame(card, bg=C_ACCENT2, height=3).pack(fill=tk.X)

inner = tk.Frame(card, bg=C_CARD)
inner.pack(padx=28, pady=(20, 24), fill=tk.X)

# Username
tk.Label(inner, text="Username",
         font=("Segoe UI", 9), bg=C_CARD, fg=C_MUTED).pack(anchor=tk.W)

entry_username = tk.Entry(inner, width=30,
                          bg=C_INPUT, fg=C_MUTED,
                          insertbackground=C_TEXT,
                          relief=tk.FLAT, font=("Segoe UI", 11),
                          highlightthickness=1,
                          highlightbackground=C_BORDER,
                          highlightcolor=C_ACCENT)
entry_username.pack(fill=tk.X, ipady=8, pady=(4, 16))
entry_username.insert(0, "Enter username")
entry_username.bind("<FocusIn>",  lambda e: on_entry_focus_in(entry_username,  "Enter username"))
entry_username.bind("<FocusOut>", lambda e: on_entry_focus_out(entry_username, "Enter username"))

# Password row
tk.Label(inner, text="Password",
         font=("Segoe UI", 9), bg=C_CARD, fg=C_MUTED).pack(anchor=tk.W)

pwd_row = tk.Frame(inner, bg=C_CARD)
pwd_row.pack(fill=tk.X, pady=(4, 0))

entry_password = tk.Entry(pwd_row,
                          show="*",
                          bg=C_INPUT, fg=C_TEXT,
                          insertbackground=C_TEXT,
                          relief=tk.FLAT, font=("Segoe UI", 11),
                          highlightthickness=1,
                          highlightbackground=C_BORDER,
                          highlightcolor=C_ACCENT)
entry_password.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=8)
entry_password.bind("<Return>", lambda e: user_login())

eye_btn = tk.Button(pwd_row, text="👁",
                    bg=C_INPUT, fg=C_MUTED,
                    relief=tk.FLAT, font=("Segoe UI", 11),
                    activebackground=C_INPUT, activeforeground=C_TEXT,
                    cursor="hand2", command=toggle_password,
                    padx=8)
eye_btn.pack(side=tk.RIGHT)

# Status / error label
status_label = tk.Label(inner, text="",
                         font=("Segoe UI", 9),
                         bg=C_CARD, fg=C_ERROR)
status_label.pack(anchor=tk.W, pady=(8, 0))

# Login button
tk.Frame(inner, bg=C_CARD, height=6).pack()

login_btn = tk.Button(inner,
                      text="Login  →",
                      font=("Segoe UI", 12, "bold"),
                      bg=C_ACCENT, fg=C_BG,
                      activebackground=C_HOVER, activeforeground=C_BG,
                      relief=tk.FLAT, cursor="hand2",
                      pady=10,
                      command=user_login)
login_btn.pack(fill=tk.X)
login_btn.bind("<Enter>", lambda e: login_btn.config(bg=C_HOVER))
login_btn.bind("<Leave>", lambda e: login_btn.config(bg=C_ACCENT))

# ── Footer ────────────────────────────────────────────────────────────────────
tk.Label(root, text="© 2026 ERP System  ·  ITHub  ·  Mahendra Suthar",
         font=("Segoe UI", 8),
         bg=C_BG, fg=C_MUTED).pack(side=tk.BOTTOM, pady=12)

# ── Pre-fill for dev convenience (remove in production) ──────────────────────
entry_username.delete(0, tk.END)
entry_username.config(fg=C_TEXT)
entry_username.insert(0, "j")

entry_password.insert(0, "j")

# ═══════════════════════════════════════════════════════════════════════════════
root.mainloop()