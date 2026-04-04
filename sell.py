import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, END, FLAT, BOTH, X, Y, LEFT, RIGHT, W, EW, BOTTOM, NW
import sqlite3
from datetime import date
import pandas as pd
import dashboard
import sell_chatbot

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
C_PURPLE  = "#b44fff"

# ─── Reusable helpers ─────────────────────────────────────────────────────────
def styled_entry(parent, textvariable=None, width=28, readonly=False):
    state_bg = "#1a1f2e" if readonly else C_INPUT
    return tk.Entry(parent, textvariable=textvariable, width=width,
                    bg=state_bg, fg=C_TEXT, insertbackground=C_TEXT,
                    relief=FLAT, font=("Segoe UI", 10),
                    highlightthickness=1,
                    highlightbackground=C_BORDER,
                    highlightcolor=C_ACCENT,
                    state="readonly" if readonly else "normal",
                    readonlybackground=state_bg)

def action_button(parent, text, color, command, width=11):
    return tk.Button(parent, text=text, width=width,
                     font=("Segoe UI", 10, "bold"),
                     bg=color, fg=C_BG,
                     activebackground=C_HOVER, activeforeground=C_BG,
                     relief=FLAT, padx=8, pady=6,
                     cursor="hand2", command=command)

def styled_combo(parent, textvariable, values, width=27):
    style = ttk.Style()
    style.configure("Dark.TCombobox",
                    fieldbackground=C_INPUT, background=C_INPUT,
                    foreground=C_TEXT, arrowcolor=C_ACCENT,
                    borderwidth=0, font=("Segoe UI", 10))
    style.map("Dark.TCombobox",
              fieldbackground=[("readonly", C_INPUT)],
              foreground=[("readonly", C_TEXT)])
    return ttk.Combobox(parent, textvariable=textvariable,
                        values=values, state="readonly",
                        width=width, style="Dark.TCombobox",
                        font=("Segoe UI", 10))

def kpi_card(parent, label, color):
    frm = tk.Frame(parent, bg=C_CARD,
                   highlightbackground=C_BORDER, highlightthickness=1)
    tk.Frame(frm, bg=color, height=3).pack(fill=X)
    tk.Label(frm, text=label, font=("Segoe UI", 8),
             bg=C_CARD, fg=C_MUTED).pack(anchor=W, padx=10, pady=(6, 0))
    val = tk.Label(frm, text="---", font=("Segoe UI", 15, "bold"),
                   bg=C_CARD, fg=C_TEXT)
    val.pack(anchor=W, padx=10, pady=(2, 8))
    return frm, val


sell_id = None


def open_sell():
    global sell_id

    conn   = sqlite3.connect("ERP_Billing.db")
    cursor = conn.cursor()

    root = tk.Tk()
    root.title("ERP Billing System - Sell Management")
    root.state("zoomed")
    root.configure(bg=C_BG)

    # Variables
    bill_no_var      = tk.StringVar()
    buyer_id_var     = tk.StringVar()
    user_id_var      = tk.StringVar()
    sell_date_var    = tk.StringVar(value=date.today().strftime("%Y-%m-%d"))
    product_id_var   = tk.StringVar()
    qty_var          = tk.StringVar()
    price_var        = tk.StringVar()
    gst_rate_var     = tk.StringVar()
    gst_amount_var   = tk.StringVar()
    total_amount_var = tk.StringVar()
    payment_term_var = tk.StringVar()

    # =========================================================
    # FUNCTIONS
    # =========================================================

    def calculate_amount(*args):
        try:
            qty      = float(qty_var.get())
            price    = float(price_var.get())
            gst      = float(gst_rate_var.get())
            subtotal = qty * price
            gst_amt  = subtotal * gst / 100
            total    = subtotal + gst_amt
            gst_amount_var.set(round(gst_amt, 2))
            total_amount_var.set(round(total, 2))
        except Exception:
            pass

    def clear_sell():
        global sell_id
        sell_id = None
        bill_no_var.set("")
        buyer_id_var.set("")
        user_id_var.set("")
        sell_date_var.set(date.today().strftime("%Y-%m-%d"))
        product_id_var.set("")
        qty_var.set("")
        price_var.set("")
        gst_rate_var.set("")
        gst_amount_var.set("")
        total_amount_var.set("")
        payment_term_var.set("")
        remark_text.delete("1.0", END)

    def fetch_data():
        tree.delete(*tree.get_children())
        cursor.execute("SELECT * FROM sell")
        rows = cursor.fetchall()
        for idx, row in enumerate(rows):
            tag = "odd" if idx % 2 == 0 else "even"
            tree.insert("", END, values=row, tags=(tag,))
        sell_summary()

    def save_sell():
        if not bill_no_var.get() or not product_id_var.get():
            messagebox.showerror("ERP Billing", "Bill Number & Product are required!")
            return
        cursor.execute("""
            INSERT INTO sell (
                bill_number, buyer_id, user_id, sell_date,
                product_id, product_quantity, product_price,
                product_gst_rate, gst_amount, total_amount,
                payment_term, remark
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            bill_no_var.get(), buyer_id_var.get(), user_id_var.get(),
            sell_date_var.get(), product_id_var.get(),
            qty_var.get(), price_var.get(), gst_rate_var.get(),
            gst_amount_var.get(), total_amount_var.get(),
            payment_term_var.get(),
            remark_text.get("1.0", END).strip()
        ))
        conn.commit()
        messagebox.showinfo("ERP Billing", "Sell Saved Successfully")
        fetch_data()
        clear_sell()

    def on_select(event):
        global sell_id
        selected = tree.focus()
        if not selected:
            return
        data = tree.item(selected)["values"]
        sell_id = data[0]
        bill_no_var.set(data[1])
        buyer_id_var.set(data[2])
        user_id_var.set(data[3])
        sell_date_var.set(data[4])
        product_id_var.set(data[5])
        qty_var.set(data[6])
        price_var.set(data[7])
        gst_rate_var.set(data[8])
        gst_amount_var.set(data[9])
        total_amount_var.set(data[10])
        payment_term_var.set(data[11])
        remark_text.delete("1.0", END)
        remark_text.insert(END, data[12])

    def on_update():
        global sell_id
        if not sell_id:
            messagebox.showerror("ERP Billing", "Please select a record to update!")
            return
        cursor.execute("""
            UPDATE sell SET
                bill_number=?, buyer_id=?, user_id=?, sell_date=?,
                product_id=?, product_quantity=?, product_price=?,
                product_gst_rate=?, gst_amount=?, total_amount=?,
                payment_term=?, remark=?
            WHERE sell_id=?
        """, (
            bill_no_var.get(), buyer_id_var.get(), user_id_var.get(),
            sell_date_var.get(), product_id_var.get(),
            qty_var.get(), price_var.get(), gst_rate_var.get(),
            gst_amount_var.get(), total_amount_var.get(),
            payment_term_var.get(),
            remark_text.get("1.0", END).strip(),
            sell_id
        ))
        conn.commit()
        messagebox.showinfo("ERP Billing", "Record Updated Successfully")
        fetch_data()
        clear_sell()

    def on_delete():
        global sell_id
        if not sell_id:
            messagebox.showerror("ERP Billing", "Please select a record to delete!")
            return
        if messagebox.askyesno("ERP Billing", "Are you sure you want to delete this record?"):
            cursor.execute("DELETE FROM sell WHERE sell_id=?", (sell_id,))
            conn.commit()
            messagebox.showinfo("ERP Billing", "Record Deleted")
            fetch_data()
            clear_sell()

    def sell_summary():
        def safe(q):
            cursor.execute(q)
            v = cursor.fetchone()[0]
            return v if v is not None else 0

        kpi_records_val.config(text=str(safe("SELECT COUNT(sell_id) FROM sell")))
        kpi_qty_val.config(text=str(safe("SELECT SUM(product_quantity) FROM sell")))
        amt = safe("SELECT SUM(total_amount) FROM sell")
        kpi_total_val.config(text=f"Rs.{amt:,.2f}")
        gst = safe("SELECT SUM(gst_amount) FROM sell")
        kpi_gst_val.config(text=f"Rs.{gst:,.2f}")
        max_a = safe("SELECT MAX(total_amount) FROM sell")
        kpi_max_val.config(text=f"Rs.{max_a:,.2f}")
        min_a = safe("SELECT MIN(total_amount) FROM sell")
        kpi_min_val.config(text=f"Rs.{min_a:,.2f}")

    def data_analysis():
        df = pd.read_sql_query("""
            SELECT s.sell_id, s.buyer_id, s.product_id,
                   s.product_quantity, s.product_price, s.total_amount,
                   p.product_name, p.product_category,
                   b.buyer_company_name
            FROM sell s
            LEFT JOIN product p ON s.product_id = p.product_id
            LEFT JOIN buyer b   ON s.buyer_id   = b.buyer_id
        """, conn)

        if df.empty:
            messagebox.showinfo("ERP", "No data available for analysis.")
            return

        grouped_product   = df.groupby("product_name")["product_quantity"].sum().round(2)
        grouped_buyer_qty = df.groupby("buyer_company_name")["product_quantity"].sum().round(2)
        grouped_amount    = df.groupby("buyer_company_name")["total_amount"].sum().round(2)
        highest_price_row = df.loc[df["product_price"].idxmax()]
        lowest_price_row  = df.loc[df["product_price"].idxmin()]

        data  = "╔══════════════════════════════════════╗\n"
        data += "║          ERP SALES ANALYSIS          ║\n"
        data += "╚══════════════════════════════════════╝\n\n"
        data += "PRODUCT SALES ANALYSIS\n"
        data += "-" * 46 + "\n"
        data += f"Top Selling Product         : {grouped_product.idxmax()}\n"
        data += f"Total Quantity Sold         : {grouped_product.max()}\n\n"
        data += f"Least Selling Product       : {grouped_product.idxmin()}\n"
        data += f"Total Quantity Sold         : {grouped_product.min()}\n\n"
        data += "BUYER PURCHASE ANALYSIS\n"
        data += "-" * 46 + "\n"
        data += f"Top Buying Party            : {grouped_buyer_qty.idxmax()}\n"
        data += f"Total Quantity Purchased    : {grouped_buyer_qty.max()}\n\n"
        data += f"Least Buying Party          : {grouped_buyer_qty.idxmin()}\n"
        data += f"Total Quantity Purchased    : {grouped_buyer_qty.min()}\n\n"
        data += "BUYER BUSINESS VALUE\n"
        data += "-" * 46 + "\n"
        data += f"Most Valuable Buyer         : {grouped_amount.idxmax()}\n"
        data += f"Total Purchase Value        : Rs. {grouped_amount.max():,.2f}\n\n"
        data += f"Least Valuable Buyer        : {grouped_amount.idxmin()}\n"
        data += f"Total Purchase Value        : Rs. {grouped_amount.min():,.2f}\n\n"
        data += "PRODUCT PRICE ANALYSIS\n"
        data += "-" * 46 + "\n"
        data += f"Highest Price Product       : {highest_price_row['product_name']}\n"
        data += f"Price                       : Rs. {highest_price_row['product_price']:,.2f}\n\n"
        data += f"Lowest Price Product        : {lowest_price_row['product_name']}\n"
        data += f"Price                       : Rs. {lowest_price_row['product_price']:,.2f}\n"
        data += "=" * 46

        messagebox.showinfo("ERP - Sales Analysis", data)

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
        response = sell_chatbot.chatbot_response(msg)
        add_message("bot", response)

    def move_back():
        root.destroy()
        dashboard.open_dashboard()

    # =========================================================
    # TREEVIEW STYLE
    # =========================================================
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

    # =========================================================
    # HEADER
    # =========================================================
    header = tk.Frame(root, bg=C_HEADER, height=64)
    header.pack(fill=X)
    header.pack_propagate(False)

    dot = tk.Canvas(header, width=36, height=36, bg=C_HEADER, highlightthickness=0)
    dot.pack(side=LEFT, padx=(20, 6), pady=14)
    dot.create_oval(4, 4, 32, 32, fill=C_ACCENT, outline="")

    tk.Label(header, text="ERP Billing System",
             font=("Segoe UI", 18, "bold"),
             bg=C_HEADER, fg=C_TEXT).pack(side=LEFT, pady=14)
    tk.Label(header, text="Sell Management",
             font=("Segoe UI", 11),
             bg=C_HEADER, fg=C_MUTED).pack(side=LEFT, padx=(8, 0), pady=17)

    action_button(header, "<- Dashboard", C_ACCENT2, move_back, width=14).pack(
        side=RIGHT, padx=20, pady=14)

    # =========================================================
    # KPI ROW
    # =========================================================
    kpi_row = tk.Frame(root, bg=C_BG)
    kpi_row.pack(fill=X, padx=16, pady=(14, 0))

    kpi_cfgs = [
        ("Total Records",    C_ACCENT),
        ("Total Qty Sold",   C_ACCENT2),
        ("Total Revenue",    C_ACCENT3),
        ("Total GST",        C_PURPLE),
        ("Max Bill",         C_ACCENT4),
        ("Min Bill",         C_HOVER),
    ]

    kpi_vals = []
    for i, (lbl, col) in enumerate(kpi_cfgs):
        frm, val_lbl = kpi_card(kpi_row, lbl, col)
        frm.grid(row=0, column=i, padx=5, pady=4, sticky="nsew")
        kpi_row.columnconfigure(i, weight=1)
        kpi_vals.append(val_lbl)

    (kpi_records_val, kpi_qty_val, kpi_total_val,
     kpi_gst_val, kpi_max_val, kpi_min_val) = kpi_vals

    # =========================================================
    # MAIN LAYOUT
    # =========================================================
    main_frame = tk.Frame(root, bg=C_BG)
    main_frame.pack(fill=BOTH, expand=True, padx=16, pady=14)

    # LEFT: Form card
    form_card = tk.Frame(main_frame, bg=C_CARD,
                         highlightbackground=C_BORDER, highlightthickness=1)
    form_card.pack(side=LEFT, fill=Y, padx=(0, 10), ipadx=16, ipady=10)

    tk.Frame(form_card, bg=C_ACCENT, height=3).pack(fill=X)
    tk.Label(form_card, text="Sell Details",
             font=("Segoe UI", 13, "bold"),
             bg=C_CARD, fg=C_TEXT).pack(pady=(14, 4), padx=16, anchor=W)
    tk.Frame(form_card, bg=C_BORDER, height=1).pack(fill=X, padx=16, pady=(0, 10))

    form_inner = tk.Frame(form_card, bg=C_CARD)
    form_inner.pack(padx=16)

    cursor.execute("SELECT product_id, product_name FROM product")
    product_dict      = {pid: pname for pid, pname in cursor.fetchall()}
    product_name_list = list(set(product_dict.values()))

    cursor.execute("SELECT buyer_id, buyer_company_name FROM buyer")
    buyer_dict      = {bid: bname for bid, bname in cursor.fetchall()}
    buyer_name_list = list(set(buyer_dict.values()))

    field_cfgs = [
        ("Bill Number *",  "entry", bill_no_var,      None,               False),
        ("Buyer",          "combo", buyer_id_var,     buyer_name_list,    False),
        ("User",           "entry", user_id_var,      None,               False),
        ("Sell Date",      "entry", sell_date_var,    None,               False),
        ("Product *",      "combo", product_id_var,   product_name_list,  False),
        ("Quantity",       "entry", qty_var,           None,              False),
        ("Price",          "entry", price_var,         None,              False),
        ("GST Rate (%)",   "entry", gst_rate_var,      None,              False),
        ("GST Amount",     "entry", gst_amount_var,    None,              True),
        ("Total Amount",   "entry", total_amount_var,  None,              True),
        ("Payment Term",   "entry", payment_term_var,  None,              False),
    ]

    for i, (label, ftype, var, vals, ro) in enumerate(field_cfgs):
        tk.Label(form_inner, text=label,
                 font=("Segoe UI", 9),
                 bg=C_CARD, fg=C_MUTED).grid(row=i*2, column=0,
                                              sticky=W, pady=(6, 0))
        if ftype == "combo":
            w = styled_combo(form_inner, var, vals)
        else:
            w = styled_entry(form_inner, textvariable=var, readonly=ro)
        w.grid(row=i*2+1, column=0, sticky=EW, pady=(2, 0))

    qty_var.trace("w", calculate_amount)
    price_var.trace("w", calculate_amount)
    gst_rate_var.trace("w", calculate_amount)

    tk.Label(form_inner, text="Remark",
             font=("Segoe UI", 9),
             bg=C_CARD, fg=C_MUTED).grid(row=22, column=0, sticky=NW, pady=(8, 0))
    remark_text = tk.Text(form_inner, width=28, height=3,
                          font=("Segoe UI", 10),
                          bg=C_INPUT, fg=C_TEXT,
                          insertbackground=C_TEXT,
                          relief=FLAT,
                          highlightthickness=1,
                          highlightbackground=C_BORDER,
                          highlightcolor=C_ACCENT)
    remark_text.grid(row=23, column=0, sticky=EW, pady=(2, 0))

    tk.Frame(form_card, bg=C_BORDER, height=1).pack(fill=X, padx=16, pady=(14, 8))
    btn_grid = tk.Frame(form_card, bg=C_CARD)
    btn_grid.pack(padx=16, pady=(0, 10))

    btn_cfg = [
        ("Save",     C_ACCENT,  save_sell,     0, 0),
        ("Update",   C_ACCENT2, on_update,     0, 1),
        ("Delete",   C_ACCENT4, on_delete,     0, 2),
        ("Clear",    C_MUTED,   clear_sell,    1, 0),
        ("Analysis", C_ACCENT3, data_analysis, 1, 1),
    ]
    for text, color, cmd, r, c in btn_cfg:
        action_button(btn_grid, text, color, cmd, width=11).grid(
            row=r, column=c, padx=4, pady=4)

    # RIGHT COLUMN: Table + Chatbot
    right_col = tk.Frame(main_frame, bg=C_BG)
    right_col.pack(side=RIGHT, fill=BOTH, expand=True)

    # Table card
    table_card = tk.Frame(right_col, bg=C_CARD,
                          highlightbackground=C_BORDER, highlightthickness=1)
    table_card.pack(fill=BOTH, expand=True, pady=(0, 10))

    tk.Frame(table_card, bg=C_ACCENT2, height=3).pack(fill=X)
    tk.Label(table_card, text="Sell Records",
             font=("Segoe UI", 13, "bold"),
             bg=C_CARD, fg=C_TEXT).pack(anchor=W, padx=16, pady=(12, 4))
    tk.Frame(table_card, bg=C_BORDER, height=1).pack(fill=X, padx=16, pady=(0, 6))

    tree_wrap = tk.Frame(table_card, bg=C_CARD)
    tree_wrap.pack(fill=BOTH, expand=True, padx=10, pady=(0, 10))

    columns = ("ID", "Bill", "Buyer", "User", "Date", "Product",
               "Qty", "Price", "GST%", "GST Amt", "Total", "Payment", "Remark")
    tree = ttk.Treeview(tree_wrap, columns=columns,
                        show="headings", style="Dark.Treeview")

    col_widths = {"ID": 40, "Bill": 80, "Buyer": 100, "User": 65,
                  "Date": 90, "Product": 95, "Qty": 50, "Price": 70,
                  "GST%": 50, "GST Amt": 75, "Total": 85,
                  "Payment": 80, "Remark": 110}
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=col_widths.get(col, 80), anchor=W)

    tree.tag_configure("odd",  background="#1a2234")
    tree.tag_configure("even", background=C_CARD)

    vsb = ttk.Scrollbar(tree_wrap, orient="vertical",   command=tree.yview)
    hsb = ttk.Scrollbar(tree_wrap, orient="horizontal", command=tree.xview)
    tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
    vsb.pack(side=RIGHT, fill=Y)
    hsb.pack(side=BOTTOM, fill=X)
    tree.pack(fill=BOTH, expand=True)
    tree.bind("<<TreeviewSelect>>", on_select)

    # Chatbot card
    chat_card = tk.Frame(right_col, bg=C_CARD,
                         highlightbackground=C_BORDER, highlightthickness=1)
    chat_card.pack(fill=X)

    tk.Frame(chat_card, bg=C_ACCENT3, height=3).pack(fill=X)
    tk.Label(chat_card, text="ERP AI Assistant - Mitra",
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

    action_button(chat_input_row, "Send", C_ACCENT,
                  chatbot_response, width=10).pack(side=RIGHT)

    # FOOTER
    footer = tk.Frame(root, bg=C_HEADER, height=30)
    footer.pack(fill=X, side=BOTTOM)
    footer.pack_propagate(False)
    tk.Label(footer,
             text="Developed by Mahendra Suthar  -  ERP Billing System",
             font=("Segoe UI", 8),
             bg=C_HEADER, fg=C_MUTED).pack(pady=7)

    # INITIAL LOAD
    fetch_data()
    root.mainloop()