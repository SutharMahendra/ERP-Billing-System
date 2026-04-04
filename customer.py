import tkinter as tk
from tkinter import *
from tkinter import ttk, messagebox
import sqlite3
import pandas as pd
import dashboard
from tkinter import scrolledtext
import customer_chatbot

selected_id = None

# ─── Color Palette (matches dashboard) ───────────────────────────────────────
C_BG       = "#0f1117"
C_SIDEBAR  = "#161b22"
C_CARD     = "#1c2230"
C_ACCENT   = "#00d4aa"
C_ACCENT2  = "#4f8ef7"
C_ACCENT3  = "#f7a94f"
C_ACCENT4  = "#f7604f"
C_TEXT     = "#e8eaf0"
C_MUTED    = "#7a8499"
C_HEADER   = "#12192b"
C_BORDER   = "#2a3345"
C_INPUT    = "#242d3d"
C_HOVER    = "#00b894"

def styled_entry(parent, textvariable=None, width=28):
    e = tk.Entry(parent,
                 textvariable=textvariable,
                 width=width,
                 bg=C_INPUT,
                 fg=C_TEXT,
                 insertbackground=C_TEXT,
                 relief=FLAT,
                 font=("Segoe UI", 10),
                 highlightthickness=1,
                 highlightbackground=C_BORDER,
                 highlightcolor=C_ACCENT)
    return e

def styled_label(parent, text, bold=False, muted=False, size=10):
    fg = C_MUTED if muted else C_TEXT
    weight = "bold" if bold else "normal"
    return tk.Label(parent, text=text,
                    font=("Segoe UI", size, weight),
                    bg=C_CARD, fg=fg)

def action_button(parent, text, color, command, width=10):
    btn = tk.Button(parent,
                    text=text,
                    width=width,
                    font=("Segoe UI", 10, "bold"),
                    bg=color,
                    fg=C_BG,
                    activebackground=C_HOVER,
                    activeforeground=C_BG,
                    relief=FLAT,
                    padx=8, pady=6,
                    cursor="hand2",
                    command=command)
    return btn


def open_customer():

    conn   = sqlite3.connect("ERP_Billing.db")
    cursor = conn.cursor()

    root = tk.Tk()
    root.title("ERP Billing System – Customer Management")
    root.state("zoomed")
    root.configure(bg=C_BG)

    # ── Variables ────────────────────────────────────────────────────────
    buyer_company_var = StringVar()
    buyer_name_var    = StringVar()
    buyer_phone_var   = StringVar()
    buyer_email_var   = StringVar()
    buyer_city_var    = StringVar()
    buyer_gst_var     = StringVar()

    # ── Treeview style ───────────────────────────────────────────────────
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Dark.Treeview",
                    background=C_CARD,
                    foreground=C_TEXT,
                    fieldbackground=C_CARD,
                    rowheight=30,
                    font=("Segoe UI", 10),
                    borderwidth=0)
    style.configure("Dark.Treeview.Heading",
                    background=C_HEADER,
                    foreground=C_ACCENT,
                    font=("Segoe UI", 10, "bold"),
                    relief=FLAT)
    style.map("Dark.Treeview",
              background=[("selected", "#1e3a5f")],
              foreground=[("selected", C_TEXT)])
    style.configure("Accent.TCombobox",
                    fieldbackground=C_INPUT,
                    background=C_INPUT,
                    foreground=C_TEXT,
                    arrowcolor=C_ACCENT,
                    borderwidth=0)

    # ═══════════════════════════════════════════════════════════════════════
    # FUNCTIONS
    # ═══════════════════════════════════════════════════════════════════════

    def fetch_data():
        print("data fetch successfully")
        for row in tree.get_children():
            tree.delete(row)
        cursor.execute("SELECT * FROM buyer")
        rows = cursor.fetchall()
        for idx, row in enumerate(rows):
            tag = "odd" if idx % 2 == 0 else "even"
            tree.insert("", END, values=row, tags=(tag,))
        summary_data()

    def save_customer_data():
        print("start save data...")
        name    = buyer_name_var.get().strip()
        phone   = buyer_phone_var.get().strip()
        address = buyer_address_text.get("1.0", tk.END).strip()

        if not name or not phone or not address:
            messagebox.showerror("ERP System", "Please fill all required fields (*)!")
            return

        cursor.execute("""
            INSERT INTO buyer
            (buyer_company_name, buyer_name, buyer_phone_no,
             buyer_email, buyer_address, buyer_city, buyer_gst_number)
            VALUES (?,?,?,?,?,?,?)
        """, (
            buyer_company_var.get(),
            name, phone,
            buyer_email_var.get(),
            address,
            buyer_city_var.get(),
            buyer_gst_var.get()
        ))
        conn.commit()
        messagebox.showinfo("ERP", "Buyer Added Successfully ✅")
        clear_data()
        fetch_data()
        print("end save data...")

    def clear_data():
        print("start clear data...")
        global selected_id
        selected_id = None
        buyer_company_var.set("")
        buyer_name_var.set("")
        buyer_phone_var.set("")
        buyer_email_var.set("")
        buyer_city_var.set("")
        buyer_gst_var.set("")
        buyer_address_text.delete("1.0", tk.END)
        print("end clear data...")

    def on_select(event):
        print("start selecting row ...")
        global selected_id
        selected = tree.focus()
        if not selected:
            return
        values = tree.item(selected, "values")
        selected_id = values[0]
        buyer_company_var.set(values[1])
        buyer_name_var.set(values[2])
        buyer_phone_var.set(values[3])
        buyer_email_var.set(values[4])
        buyer_address_text.delete("1.0", tk.END)
        buyer_address_text.insert(tk.END, values[5])
        buyer_city_var.set(values[6])
        buyer_gst_var.set(values[7])
        print("end selecting row ...")

    def on_update():
        print("start update data...")
        if selected_id is None:
            messagebox.showerror("ERP", "Please select a record to update!")
            return
        cursor.execute("""
            UPDATE buyer SET
                buyer_company_name=?, buyer_name=?, buyer_phone_no=?,
                buyer_email=?, buyer_address=?, buyer_city=?, buyer_gst_number=?
            WHERE buyer_id=?
        """, (
            buyer_company_var.get(),
            buyer_name_var.get(),
            buyer_phone_var.get(),
            buyer_email_var.get(),
            buyer_address_text.get("1.0", tk.END).strip(),
            buyer_city_var.get(),
            buyer_gst_var.get(),
            selected_id
        ))
        conn.commit()
        messagebox.showinfo("ERP", "Record Updated Successfully ✅")
        fetch_data()
        clear_data()
        print("end update data...")

    def on_delete():
        print("start deleting data...")
        if selected_id is None:
            messagebox.showerror("ERP", "Please select a record to delete!")
            return
        if messagebox.askyesno("ERP", "Are you sure you want to delete this record?"):
            cursor.execute("DELETE FROM buyer WHERE buyer_id=?", (selected_id,))
            conn.commit()
            messagebox.showinfo("ERP", "Record Deleted ✅")
            fetch_data()
            clear_data()
            print("end deleting data...")

    def summary_data():
        print("start summary data...")
        cursor.execute("SELECT COUNT(*) FROM buyer")
        total = cursor.fetchone()[0]
        total_label.config(text=f"Total Buyers: {total}")
        print("end summary data...")

    def data_analysis():
        print("start analysis data...")
        df = pd.read_sql_query("SELECT * FROM buyer", conn)
        if df.empty:
            messagebox.showinfo("ERP", "No data available for analysis.")
            return

        grouped   = df.groupby("buyer_city").size().reset_index(name="buyer_count")
        top_row   = grouped.loc[grouped["buyer_count"].idxmax()]
        low_row   = grouped.loc[grouped["buyer_count"].idxmin()]
        gst_count     = df["buyer_gst_number"].notna().sum()
        non_gst_count = df["buyer_gst_number"].isna().sum()
        total_buyers  = len(df)

        data  = "╔══════════════════════════════════════╗\n"
        data += "║          ERP BUYER ANALYSIS          ║\n"
        data += "╚══════════════════════════════════════╝\n\n"
        data += "BUYER CITY DISTRIBUTION\n"
        data += "─" * 42 + "\n"
        data += f"City With Most Buyers   : {top_row['buyer_city']} ({top_row['buyer_count']})\n"
        data += f"City With Least Buyers  : {low_row['buyer_city']} ({low_row['buyer_count']})\n\n"
        data += "GST REGISTRATION ANALYSIS\n"
        data += "─" * 42 + "\n"
        data += f"Total Buyers            : {total_buyers}\n"
        data += f"GST Registered Buyers   : {gst_count}\n"
        data += f"Non-GST Buyers          : {non_gst_count}\n"
        data += "═" * 42

        messagebox.showinfo("ERP System – Buyer Analysis", data)

    def chatbot_response():
        msg = entry_chat.get().strip()
        if not msg:
            return
        add_message("user", msg)
        entry_chat.delete(0, tk.END)
        response = customer_chatbot.chatbot_response(msg)
        add_message("bot", response)

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
    # ═══════════════════════════════════════════════════════════════════════
    # HEADER
    # ═══════════════════════════════════════════════════════════════════════
    header = Frame(root, bg=C_HEADER, height=64)
    header.pack(fill=X)
    header.pack_propagate(False)

    canvas_dot = Canvas(header, width=36, height=36,
                        bg=C_HEADER, highlightthickness=0)
    canvas_dot.pack(side=LEFT, padx=(20, 6), pady=14)
    canvas_dot.create_oval(4, 4, 32, 32, fill=C_ACCENT, outline="")

    tk.Label(header, text="ERP Billing System",
             font=("Segoe UI", 18, "bold"),
             bg=C_HEADER, fg=C_TEXT).pack(side=LEFT, pady=14)
    tk.Label(header, text="Customer Management",
             font=("Segoe UI", 11),
             bg=C_HEADER, fg=C_MUTED).pack(side=LEFT, padx=(8, 0), pady=17)

    action_button(header, "← Dashboard", C_ACCENT2,
                  lambda: (root.destroy(), dashboard.open_dashboard()),
                  width=14).pack(side=RIGHT, padx=20, pady=14)

    # ═══════════════════════════════════════════════════════════════════════
    # MAIN LAYOUT
    # ═══════════════════════════════════════════════════════════════════════
    main_frame = Frame(root, bg=C_BG)
    main_frame.pack(fill=BOTH, expand=True, padx=16, pady=16)

    # ── LEFT: Form card ──────────────────────────────────────────────────
    form_card = Frame(main_frame, bg=C_CARD,
                      highlightbackground=C_BORDER, highlightthickness=1)
    form_card.pack(side=LEFT, fill=Y, padx=(0, 10), ipadx=16, ipady=10)

    Frame(form_card, bg=C_ACCENT, height=3).pack(fill=X)

    tk.Label(form_card, text="👥  Buyer Details",
             font=("Segoe UI", 13, "bold"),
             bg=C_CARD, fg=C_TEXT).pack(pady=(14, 4), padx=16, anchor=W)
    Frame(form_card, bg=C_BORDER, height=1).pack(fill=X, padx=16, pady=(0, 10))

    form_inner = Frame(form_card, bg=C_CARD)
    form_inner.pack(padx=16)

    field_rows = [
        ("Company Name",  buyer_company_var),
        ("Buyer Name *",  buyer_name_var),
        ("Phone * ",      buyer_phone_var),
        ("Email",         buyer_email_var),
        ("GST Number",    buyer_gst_var),
    ]

    entries = {}
    for i, (label, var) in enumerate(field_rows):
        tk.Label(form_inner, text=label,
                 font=("Segoe UI", 9),
                 bg=C_CARD, fg=C_MUTED).grid(row=i*2, column=0,
                                              sticky=W, pady=(8, 0))
        e = styled_entry(form_inner, textvariable=var)
        e.grid(row=i*2+1, column=0, sticky=EW, pady=(2, 0))
        entries[label] = e

    # Address
    tk.Label(form_inner, text="Address *",
             font=("Segoe UI", 9),
             bg=C_CARD, fg=C_MUTED).grid(row=10, column=0, sticky=W, pady=(8, 0))
    buyer_address_text = tk.Text(form_inner, width=28, height=3,
                                  font=("Segoe UI", 10),
                                  bg=C_INPUT, fg=C_TEXT,
                                  insertbackground=C_TEXT,
                                  relief=FLAT,
                                  highlightthickness=1,
                                  highlightbackground=C_BORDER,
                                  highlightcolor=C_ACCENT)
    buyer_address_text.grid(row=11, column=0, sticky=EW, pady=(2, 0))

    # City combobox
    tk.Label(form_inner, text="City",
             font=("Segoe UI", 9),
             bg=C_CARD, fg=C_MUTED).grid(row=12, column=0, sticky=W, pady=(8, 0))

    city_list = ["Ahmedabad", "Surat", "Jaipur", "Delhi",
                 "Mumbai", "Pune", "Indore", "Rajkot", "Other"]

    city_box = ttk.Combobox(form_inner,
                             textvariable=buyer_city_var,
                             values=city_list,
                             state="readonly",
                             width=27,
                             style="Accent.TCombobox")
    city_box.grid(row=13, column=0, sticky=EW, pady=(2, 0))

    # ── Action Buttons ───────────────────────────────────────────────────
    Frame(form_card, bg=C_BORDER, height=1).pack(fill=X, padx=16, pady=(14, 8))

    btn_grid = Frame(form_card, bg=C_CARD)
    btn_grid.pack(padx=16, pady=(0, 10))

    btn_cfg = [
        ("💾 Save",     C_ACCENT,  lambda: save_customer_data(), 0, 0),
        ("✏️ Update",   C_ACCENT2, lambda: on_update(),          0, 1),
        ("🗑 Delete",   C_ACCENT4, lambda: on_delete(),          0, 2),
        ("✖ Clear",    C_MUTED,   lambda: clear_data(),          1, 0),
        ("📊 Analysis", C_ACCENT3, lambda: data_analysis(),      1, 1),
    ]

    for text, color, cmd, r, c in btn_cfg:
        action_button(btn_grid, text, color, cmd, width=11).grid(
            row=r, column=c, padx=4, pady=4)

    # Summary label
    total_label = tk.Label(form_card, text="",
                           font=("Segoe UI", 10, "bold"),
                           bg=C_CARD, fg=C_ACCENT)
    total_label.pack(pady=(0, 8))

    # ═══════════════════════════════════════════════════════════════════════
    # RIGHT COLUMN: Table + Chatbot
    # ═══════════════════════════════════════════════════════════════════════
    right_col = Frame(main_frame, bg=C_BG)
    right_col.pack(side=RIGHT, fill=BOTH, expand=True)

    # ── Table card ───────────────────────────────────────────────────────
    table_card = Frame(right_col, bg=C_CARD,
                       highlightbackground=C_BORDER, highlightthickness=1)
    table_card.pack(fill=BOTH, expand=True, pady=(0, 10))

    Frame(table_card, bg=C_ACCENT2, height=3).pack(fill=X)

    table_hdr = Frame(table_card, bg=C_CARD)
    table_hdr.pack(fill=X, padx=16, pady=(12, 4))
    tk.Label(table_hdr, text="📋  Buyer Records",
             font=("Segoe UI", 13, "bold"),
             bg=C_CARD, fg=C_TEXT).pack(side=LEFT)

    Frame(table_card, bg=C_BORDER, height=1).pack(fill=X, padx=16, pady=(0, 6))

    tree_frame = Frame(table_card, bg=C_CARD)
    tree_frame.pack(fill=BOTH, expand=True, padx=10, pady=(0, 10))

    columns = ("ID", "Company", "Name", "Phone", "Email", "Address", "City", "GST")
    tree = ttk.Treeview(tree_frame, columns=columns,
                        show="headings", style="Dark.Treeview")

    col_widths = {"ID": 50, "Company": 140, "Name": 120, "Phone": 110,
                  "Email": 150, "Address": 160, "City": 90, "GST": 130}
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=col_widths.get(col, 100), anchor=W)

    vsb = ttk.Scrollbar(tree_frame, orient=VERTICAL, command=tree.yview)
    hsb = ttk.Scrollbar(tree_frame, orient=HORIZONTAL, command=tree.xview)
    tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

    vsb.pack(side=RIGHT, fill=Y)
    hsb.pack(side=BOTTOM, fill=X)
    tree.pack(fill=BOTH, expand=True)

    # Alternating row colours
    tree.tag_configure("odd",  background="#1a2234")
    tree.tag_configure("even", background=C_CARD)

    # ── Chatbot card ─────────────────────────────────────────────────────
    chat_card = Frame(right_col, bg=C_CARD,
                      highlightbackground=C_BORDER, highlightthickness=1)
    chat_card.pack(fill=X, pady=(0, 0))

    Frame(chat_card, bg=C_ACCENT3, height=3).pack(fill=X)

    chat_hdr = Frame(chat_card, bg=C_CARD)
    chat_hdr.pack(fill=X, padx=16, pady=(10, 4))
    tk.Label(chat_hdr, text="🤖  ERP AI Assistant  –  Mitra",
             font=("Segoe UI", 11, "bold"),
             bg=C_CARD, fg=C_TEXT).pack(side=LEFT)

    Frame(chat_card, bg=C_BORDER, height=1).pack(fill=X, padx=16, pady=(0, 6))

    chat_display = scrolledtext.ScrolledText(
        chat_card,
        height=9,
        font=("Segoe UI", 10),
        wrap=WORD,
        relief=FLAT,
        bg=C_INPUT,
        fg=C_TEXT,
        insertbackground=C_TEXT,
        bd=0,
        padx=8, pady=8
    )
    chat_display.pack(fill=X, padx=12, pady=(0, 6))
    chat_display.config(state="disabled")

    chat_input_row = Frame(chat_card, bg=C_CARD)
    chat_input_row.pack(fill=X, padx=12, pady=(0, 12))

    entry_chat = tk.Entry(chat_input_row,
                          font=("Segoe UI", 10),
                          bg=C_INPUT, fg=C_TEXT,
                          insertbackground=C_TEXT,
                          relief=FLAT,
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
    footer = Frame(root, bg=C_HEADER, height=30)
    footer.pack(fill=X, side=BOTTOM)
    footer.pack_propagate(False)
    tk.Label(footer,
             text="Developed by Mahendra Suthar  ·  ERP Billing System",
             font=("Segoe UI", 8),
             bg=C_HEADER, fg=C_MUTED).pack(pady=7)


    tree.bind("<<TreeviewSelect>>", on_select)
    fetch_data()
    root.mainloop()