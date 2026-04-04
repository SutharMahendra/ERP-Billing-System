import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, END, FLAT, BOTH, X, Y, LEFT, RIGHT, W, EW
import sqlite3
import pandas as pd
import dashboard
import suplier_chatbot

# ─── Color Palette (matches dashboard) ───────────────────────────────────────
C_BG      = "#0f1117"
C_CARD    = "#1c2230"
C_ACCENT  = "#00d4aa"
C_ACCENT2 = "#4f8ef7"
C_ACCENT3 = "#f7a94f"
C_ACCENT4 = "#f7604f"
C_TEXT    = "#e8eaf0"
C_MUTED   = "#7a8499"
C_HEADER  = "#12192b"
C_BORDER  = "#2a3345"
C_INPUT   = "#242d3d"
C_HOVER   = "#00b894"

# ─── Reusable widget helpers ─────────────────────────────────────────────────
def styled_entry(parent, width=28):
    return tk.Entry(parent, width=width,
                    bg=C_INPUT, fg=C_TEXT,
                    insertbackground=C_TEXT,
                    relief=FLAT, font=("Segoe UI", 10),
                    highlightthickness=1,
                    highlightbackground=C_BORDER,
                    highlightcolor=C_ACCENT)

def action_button(parent, text, color, command, width=11):
    return tk.Button(parent, text=text, width=width,
                     font=("Segoe UI", 10, "bold"),
                     bg=color, fg=C_BG,
                     activebackground=C_HOVER, activeforeground=C_BG,
                     relief=FLAT, padx=8, pady=6,
                     cursor="hand2", command=command)

# ─── Module-level DB connection ───────────────────────────────────────────────
conn   = sqlite3.connect("ERP_Billing.db")
cursor = conn.cursor()

seller_id = None


def open_suplier():
    global seller_id

    root = tk.Tk()
    root.title("ERP Billing System – Supplier Management")
    root.state("zoomed")
    root.configure(bg=C_BG)

    # ═══════════════════════════════════════════════════════════════════════
    # FUNCTIONS  (all defined before any widget references them)
    # ═══════════════════════════════════════════════════════════════════════

    def clear_data():
        global seller_id
        seller_id = None
        for e in entries.values():
            e.delete(0, tk.END)

    def fetch_data():
        for row in tree.get_children():
            tree.delete(row)
        cursor.execute("SELECT * FROM seller")
        rows = cursor.fetchall()
        for idx, row in enumerate(rows):
            tag = "odd" if idx % 2 == 0 else "even"
            tree.insert("", tk.END, values=row, tags=(tag,))
        summary_data()

    def save_data():
        values = [e.get().strip() for e in entries.values()]
        if not all(values):
            messagebox.showerror("ERP Billing", "Please fill all fields!")
            return
        cursor.execute("""
            INSERT INTO seller
            (seller_company_name, seller_name, seller_phone_no,
             seller_email, seller_address, seller_city, seller_gst_number)
            VALUES (?,?,?,?,?,?,?)
        """, values)
        conn.commit()
        messagebox.showinfo("ERP Billing", "Supplier Saved Successfully ✅")
        clear_data()
        fetch_data()

    def on_update():
        global seller_id
        if seller_id is None:
            messagebox.showerror("ERP Billing", "Please select a supplier first!")
            return
        values = [e.get().strip() for e in entries.values()]
        if not all(values):
            messagebox.showerror("ERP Billing", "Please fill all fields!")
            return
        cursor.execute("""
            UPDATE seller SET
                seller_company_name=?, seller_name=?, seller_phone_no=?,
                seller_email=?, seller_address=?, seller_city=?, seller_gst_number=?
            WHERE seller_id=?
        """, (*values, seller_id))
        conn.commit()
        messagebox.showinfo("ERP Billing", "Supplier Updated Successfully ✅")
        clear_data()
        fetch_data()

    def on_delete():
        global seller_id
        if seller_id is None:
            messagebox.showerror("ERP Billing", "Please select a supplier first!")
            return
        if messagebox.askyesno("ERP Billing", "Are you sure you want to delete this record?"):
            cursor.execute("DELETE FROM seller WHERE seller_id=?", (seller_id,))
            conn.commit()
            messagebox.showinfo("ERP Billing", "Supplier Deleted ✅")
            clear_data()
            fetch_data()

    def on_select(event):
        global seller_id
        selected = tree.focus()
        if not selected:
            return
        data = tree.item(selected)["values"]
        seller_id = data[0]
        clear_data()
        for i, key in enumerate(entries):
            entries[key].insert(0, data[i + 1])

    def summary_data():
        cursor.execute("SELECT COUNT(*) FROM seller")
        total = cursor.fetchone()[0]
        total_label.config(text=f"Total Suppliers: {total}")

    def data_analysis():
        df = pd.read_sql_query("SELECT * FROM seller", conn)
        if df.empty:
            messagebox.showinfo("ERP", "No data available for analysis.")
            return

        grouped      = df.groupby("seller_city").size().reset_index(name="seller_count")
        top_row      = grouped.loc[grouped["seller_count"].idxmax()]
        low_row      = grouped.loc[grouped["seller_count"].idxmin()]
        gst_count     = df["seller_gst_number"].notna().sum()
        non_gst_count = df["seller_gst_number"].isna().sum()
        total_sellers = len(df)

        data  = "╔══════════════════════════════════════╗\n"
        data += "║         ERP SELLER ANALYSIS          ║\n"
        data += "╚══════════════════════════════════════╝\n\n"
        data += "SELLER CITY DISTRIBUTION\n"
        data += "─" * 42 + "\n"
        data += f"City With Most Suppliers  : {top_row['seller_city']} ({top_row['seller_count']})\n"
        data += f"City With Least Suppliers : {low_row['seller_city']} ({low_row['seller_count']})\n\n"
        data += "GST REGISTRATION ANALYSIS\n"
        data += "─" * 42 + "\n"
        data += f"Total Suppliers           : {total_sellers}\n"
        data += f"GST Registered            : {gst_count}\n"
        data += f"Non-GST Suppliers         : {non_gst_count}\n"
        data += "═" * 42

        messagebox.showinfo("ERP System – Supplier Analysis", data)

    def move_back():
        root.destroy()
        dashboard.open_dashboard()

    def add_message(sender, message):
        chat_display.tag_config("user_tag",
                                font=("Segoe UI", 10, "bold"),
                                foreground=C_ACCENT2)
        chat_display.tag_config("bot_tag",
                                font=("Segoe UI", 10, "bold"),
                                foreground=C_ACCENT)
        chat_display.config(state="normal")
        if sender == "user":
            chat_display.insert(END, "\nYou:\n", "user_tag")
        else:
            chat_display.insert(END, "\nMitra:\n", "bot_tag")
        chat_display.insert(END, f"{message}\n")
        chat_display.config(state="disabled")
        chat_display.yview(END)

    def chatbot_response():
        msg = entry_chat.get().strip()
        if not msg:
            return
        add_message("user", msg)
        entry_chat.delete(0, tk.END)
        response = suplier_chatbot.chatbot_response(msg)
        add_message("bot", response)

    # ═══════════════════════════════════════════════════════════════════════
    # STYLES
    # ═══════════════════════════════════════════════════════════════════════
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Dark.Treeview",
                    background=C_CARD, foreground=C_TEXT,
                    fieldbackground=C_CARD, rowheight=30,
                    font=("Segoe UI", 10), borderwidth=0)
    style.configure("Dark.Treeview.Heading",
                    background=C_HEADER, foreground=C_ACCENT,
                    font=("Segoe UI", 10, "bold"), relief=FLAT)
    style.map("Dark.Treeview",
              background=[("selected", "#1e3a5f")],
              foreground=[("selected", C_TEXT)])

    # ═══════════════════════════════════════════════════════════════════════
    # HEADER
    # ═══════════════════════════════════════════════════════════════════════
    header = tk.Frame(root, bg=C_HEADER, height=64)
    header.pack(fill=X)
    header.pack_propagate(False)

    dot = tk.Canvas(header, width=36, height=36, bg=C_HEADER, highlightthickness=0)
    dot.pack(side=LEFT, padx=(20, 6), pady=14)
    dot.create_oval(4, 4, 32, 32, fill=C_ACCENT, outline="")

    tk.Label(header, text="ERP Billing System",
             font=("Segoe UI", 18, "bold"),
             bg=C_HEADER, fg=C_TEXT).pack(side=LEFT, pady=14)
    tk.Label(header, text="Supplier Management",
             font=("Segoe UI", 11),
             bg=C_HEADER, fg=C_MUTED).pack(side=LEFT, padx=(8, 0), pady=17)

    action_button(header, "← Dashboard", C_ACCENT2, move_back, width=14).pack(
        side=RIGHT, padx=20, pady=14)

    # ═══════════════════════════════════════════════════════════════════════
    # MAIN LAYOUT
    # ═══════════════════════════════════════════════════════════════════════
    main_frame = tk.Frame(root, bg=C_BG)
    main_frame.pack(fill=BOTH, expand=True, padx=16, pady=16)

    # ── LEFT: Form card ──────────────────────────────────────────────────
    form_card = tk.Frame(main_frame, bg=C_CARD,
                         highlightbackground=C_BORDER, highlightthickness=1)
    form_card.pack(side=LEFT, fill=Y, padx=(0, 10), ipadx=16, ipady=10)

    tk.Frame(form_card, bg=C_ACCENT, height=3).pack(fill=X)

    tk.Label(form_card, text="📦  Supplier Details",
             font=("Segoe UI", 13, "bold"),
             bg=C_CARD, fg=C_TEXT).pack(pady=(14, 4), padx=16, anchor=W)
    tk.Frame(form_card, bg=C_BORDER, height=1).pack(fill=X, padx=16, pady=(0, 10))

    form_inner = tk.Frame(form_card, bg=C_CARD)
    form_inner.pack(padx=16)

    field_labels = [
        "Company Name *",
        "Supplier Name *",
        "Phone Number *",
        "Email *",
        "Address *",
        "City *",
        "GST Number *",
    ]

    entries = {}
    for i, text in enumerate(field_labels):
        tk.Label(form_inner, text=text,
                 font=("Segoe UI", 9),
                 bg=C_CARD, fg=C_MUTED).grid(row=i * 2, column=0,
                                              sticky=W, pady=(8, 0))
        e = styled_entry(form_inner)
        e.grid(row=i * 2 + 1, column=0, sticky=EW, pady=(2, 0))
        entries[text] = e

    # ── Action Buttons ───────────────────────────────────────────────────
    tk.Frame(form_card, bg=C_BORDER, height=1).pack(fill=X, padx=16, pady=(14, 8))

    btn_grid = tk.Frame(form_card, bg=C_CARD)
    btn_grid.pack(padx=16, pady=(0, 10))

    btn_cfg = [
        ("💾 Save",      C_ACCENT,  save_data,      0, 0),
        ("✏️ Update",    C_ACCENT2, on_update,       0, 1),
        ("🗑 Delete",    C_ACCENT4, on_delete,       0, 2),
        ("✖ Clear",     C_MUTED,   clear_data,      1, 0),
        ("📊 Analysis",  C_ACCENT3, data_analysis,   1, 1),
    ]

    for text, color, cmd, r, c in btn_cfg:
        action_button(btn_grid, text, color, cmd, width=11).grid(
            row=r, column=c, padx=4, pady=4)

    total_label = tk.Label(form_card, text="",
                           font=("Segoe UI", 10, "bold"),
                           bg=C_CARD, fg=C_ACCENT)
    total_label.pack(pady=(0, 8))

    # ═══════════════════════════════════════════════════════════════════════
    # RIGHT COLUMN: Table + Chatbot
    # ═══════════════════════════════════════════════════════════════════════
    right_col = tk.Frame(main_frame, bg=C_BG)
    right_col.pack(side=RIGHT, fill=BOTH, expand=True)

    # ── Table card ───────────────────────────────────────────────────────
    table_card = tk.Frame(right_col, bg=C_CARD,
                          highlightbackground=C_BORDER, highlightthickness=1)
    table_card.pack(fill=BOTH, expand=True, pady=(0, 10))

    tk.Frame(table_card, bg=C_ACCENT2, height=3).pack(fill=X)

    tk.Label(table_card, text="📋  Supplier Records",
             font=("Segoe UI", 13, "bold"),
             bg=C_CARD, fg=C_TEXT).pack(anchor=W, padx=16, pady=(12, 4))
    tk.Frame(table_card, bg=C_BORDER, height=1).pack(fill=X, padx=16, pady=(0, 6))

    tree_wrap = tk.Frame(table_card, bg=C_CARD)
    tree_wrap.pack(fill=BOTH, expand=True, padx=10, pady=(0, 10))

    columns = ("ID", "Company", "Name", "Phone", "Email", "Address", "City", "GST")
    tree = ttk.Treeview(tree_wrap, columns=columns,
                        show="headings", style="Dark.Treeview")

    col_widths = {"ID": 50, "Company": 140, "Name": 120, "Phone": 110,
                  "Email": 150, "Address": 160, "City": 90, "GST": 130}
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=col_widths.get(col, 100), anchor=W)

    tree.tag_configure("odd",  background="#1a2234")
    tree.tag_configure("even", background=C_CARD)

    vsb = ttk.Scrollbar(tree_wrap, orient="vertical",   command=tree.yview)
    hsb = ttk.Scrollbar(tree_wrap, orient="horizontal", command=tree.xview)
    tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

    vsb.pack(side=RIGHT, fill=Y)
    hsb.pack(side="bottom", fill=X)
    tree.pack(fill=BOTH, expand=True)
    tree.bind("<<TreeviewSelect>>", on_select)

    # ── Chatbot card ─────────────────────────────────────────────────────
    chat_card = tk.Frame(right_col, bg=C_CARD,
                         highlightbackground=C_BORDER, highlightthickness=1)
    chat_card.pack(fill=X)

    tk.Frame(chat_card, bg=C_ACCENT3, height=3).pack(fill=X)

    tk.Label(chat_card, text="🤖  ERP AI Assistant  –  Mitra",
             font=("Segoe UI", 11, "bold"),
             bg=C_CARD, fg=C_TEXT).pack(anchor=W, padx=16, pady=(10, 4))
    tk.Frame(chat_card, bg=C_BORDER, height=1).pack(fill=X, padx=16, pady=(0, 6))

    chat_display = scrolledtext.ScrolledText(
        chat_card, height=9,
        font=("Segoe UI", 10), wrap="word",
        relief=FLAT, bg=C_INPUT, fg=C_TEXT,
        insertbackground=C_TEXT, bd=0, padx=8, pady=8
    )
    chat_display.pack(fill=X, padx=12, pady=(0, 6))
    chat_display.config(state="disabled")

    chat_input_row = tk.Frame(chat_card, bg=C_CARD)
    chat_input_row.pack(fill=X, padx=12, pady=(0, 12))

    entry_chat = tk.Entry(chat_input_row,
                          font=("Segoe UI", 10),
                          bg=C_INPUT, fg=C_TEXT,
                          insertbackground=C_TEXT, relief=FLAT,
                          highlightthickness=1,
                          highlightbackground=C_BORDER,
                          highlightcolor=C_ACCENT)
    entry_chat.pack(side=LEFT, fill=X, expand=True, padx=(0, 10), ipady=6)
    entry_chat.bind("<Return>", lambda e: chatbot_response())

    action_button(chat_input_row, "Send ➤", C_ACCENT,
                  chatbot_response, width=10).pack(side=RIGHT)

    # ═══════════════════════════════════════════════════════════════════════
    # FOOTER
    # ═══════════════════════════════════════════════════════════════════════
    footer = tk.Frame(root, bg=C_HEADER, height=30)
    footer.pack(fill=X, side="bottom")
    footer.pack_propagate(False)
    tk.Label(footer,
             text="Developed by Mahendra Suthar  ·  ERP Billing System",
             font=("Segoe UI", 8),
             bg=C_HEADER, fg=C_MUTED).pack(pady=7)

    # ═══════════════════════════════════════════════════════════════════════
    # INITIAL LOAD
    # ═══════════════════════════════════════════════════════════════════════
    fetch_data()
    root.mainloop()