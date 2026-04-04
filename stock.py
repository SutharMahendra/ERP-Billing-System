import tkinter as tk
from tkinter import ttk, scrolledtext, END, FLAT, BOTH, X, Y, LEFT, RIGHT, W, BOTTOM
import sqlite3
import pandas as pd
from rapidfuzz import process
import re
import erp_chatbot
import dashboard

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
def action_button(parent, text, color, command, width=11):
    return tk.Button(parent, text=text, width=width,
                     font=("Segoe UI", 10, "bold"),
                     bg=color, fg=C_BG,
                     activebackground=C_HOVER, activeforeground=C_BG,
                     relief=FLAT, padx=8, pady=6,
                     cursor="hand2", command=command)

def kpi_card(parent, label, color):
    frm = tk.Frame(parent, bg=C_CARD,
                   highlightbackground=C_BORDER, highlightthickness=1)
    tk.Frame(frm, bg=color, height=3).pack(fill=X)
    tk.Label(frm, text=label, font=("Segoe UI", 8),
             bg=C_CARD, fg=C_MUTED).pack(anchor=W, padx=10, pady=(6, 0))
    val = tk.Label(frm, text="---", font=("Segoe UI", 16, "bold"),
                   bg=C_CARD, fg=C_TEXT)
    val.pack(anchor=W, padx=10, pady=(2, 8))
    return frm, val

# ─── DB connection ────────────────────────────────────────────────────────────
conn   = sqlite3.connect("ERP_Billing.db")
cursor = conn.cursor()

STOCK_QUERY = """
    SELECT
        pro.product_id,
        pro.product_name,
        IFNULL(SUM(pur.product_quantity), 0) AS total_purchase,
        IFNULL(SUM(s.product_quantity),   0) AS total_sell,
        IFNULL(SUM(pur.product_quantity), 0)
            - IFNULL(SUM(s.product_quantity), 0) AS current_stock
    FROM product pro
    LEFT JOIN purchase pur ON pro.product_id = pur.product_id
    LEFT JOIN sell s       ON pro.product_id = s.product_id
    GROUP BY pro.product_id, pro.product_name
"""


def open_stock():

    stock_win = tk.Tk()
    stock_win.title("ERP Billing System – Stock Management")
    stock_win.state("zoomed")
    stock_win.configure(bg=C_BG)

    # ═══════════════════════════════════════════════════════════════════════
    # FUNCTIONS
    # ═══════════════════════════════════════════════════════════════════════

    def get_stock_df():
        return pd.read_sql_query(STOCK_QUERY, conn)

    def load_data():
        for row in tree.get_children():
            tree.delete(row)
        cursor.execute(STOCK_QUERY)
        rows = cursor.fetchall()
        for idx, row in enumerate(rows):
            # Color-code low stock rows
            stock_qty = row[4]
            if stock_qty <= 0:
                tag = "zero"
            elif stock_qty < 50:
                tag = "low"
            else:
                tag = "odd" if idx % 2 == 0 else "even"
            tree.insert("", END, values=row, tags=(tag,))
        update_kpis()

    def update_kpis():
        df = get_stock_df()
        if df.empty:
            return
        kpi_products_val.config(text=str(len(df)))
        kpi_purchase_val.config(text=str(int(df["total_purchase"].sum())))
        kpi_sell_val.config(text=str(int(df["total_sell"].sum())))
        kpi_stock_val.config(text=str(int(df["current_stock"].sum())))
        low = (df["current_stock"] < 50).sum()
        kpi_low_val.config(text=str(int(low)),
                           fg=C_ACCENT4 if low > 0 else C_ACCENT)

    def move_back():
        stock_win.destroy()
        dashboard.open_dashboard()

    def add_chat_message(sender, message):
        chat_display.tag_config("user_tag",
                                font=("Segoe UI", 10, "bold"),
                                foreground=C_ACCENT2)
        chat_display.tag_config("bot_tag",
                                font=("Segoe UI", 10, "bold"),
                                foreground=C_ACCENT)
        chat_display.tag_config("divider_tag",
                                foreground=C_BORDER)
        chat_display.config(state="normal")
        if sender == "user":
            chat_display.insert(END, "\nYou:\n", "user_tag")
        else:
            chat_display.insert(END, "\nMitra:\n", "bot_tag")
        chat_display.insert(END, f"{message}\n")
        chat_display.insert(END, "─" * 50 + "\n", "divider_tag")
        chat_display.config(state="disabled")
        chat_display.yview(END)

    def chatbot_response():
        user_input = entry_chat.get().strip()
        if not user_input:
            return

        add_chat_message("user", user_input)
        entry_chat.delete(0, END)

        df = get_stock_df()
        ui_lower = user_input.lower()

        labels = [
            "count", "list", "search_product",
            "total_purchase", "total_sell", "total_stock",
            "max_purchase", "max_sell", "max_stock",
            "min_purchase", "min_sell", "min_stock",
            "find_purchase", "find_sell", "find_stock",
            "low_stock"
        ]

        try:
            prediction = erp_chatbot.predict_label(ui_lower, labels)
        except Exception:
            prediction = ""

        response = "Sorry, I didn't understand the question. Try asking about stock, purchases, or sales."

        if prediction == "count":
            response = f"Total products in system: {len(df)}"

        elif prediction == "list":
            names = df["product_name"].tolist()
            response = "Products in stock:\n" + "\n".join(
                f"  {i}. {n}" for i, n in enumerate(names, 1))

        elif prediction == "search_product":
            product_names = df["product_name"].tolist()
            match = process.extractOne(ui_lower, product_names)
            if match:
                row = df[df["product_name"] == match[0]].iloc[0]
                response = (f"Product  : {row['product_name']}\n"
                            f"Purchased: {row['total_purchase']}\n"
                            f"Sold     : {row['total_sell']}\n"
                            f"In Stock : {row['current_stock']}")
            else:
                response = "Product not found."

        elif prediction == "total_purchase":
            response = f"Total purchased quantity: {int(df['total_purchase'].sum())}"

        elif prediction == "total_sell":
            response = f"Total sold quantity: {int(df['total_sell'].sum())}"

        elif prediction == "total_stock":
            response = f"Total stock quantity: {int(df['current_stock'].sum())}"

        elif prediction == "max_purchase":
            r = df.loc[df["total_purchase"].idxmax()]
            response = f"Highest purchased: {r['product_name']} ({int(r['total_purchase'])} units)"

        elif prediction == "max_sell":
            r = df.loc[df["total_sell"].idxmax()]
            response = f"Highest sold: {r['product_name']} ({int(r['total_sell'])} units)"

        elif prediction == "max_stock":
            r = df.loc[df["current_stock"].idxmax()]
            response = f"Highest stock: {r['product_name']} ({int(r['current_stock'])} units)"

        elif prediction == "min_purchase":
            r = df.loc[df["total_purchase"].idxmin()]
            response = f"Least purchased: {r['product_name']} ({int(r['total_purchase'])} units)"

        elif prediction == "min_sell":
            r = df.loc[df["total_sell"].idxmin()]
            response = f"Least sold: {r['product_name']} ({int(r['total_sell'])} units)"

        elif prediction == "min_stock":
            r = df.loc[df["current_stock"].idxmin()]
            response = f"Least stock: {r['product_name']} ({int(r['current_stock'])} units)"

        elif prediction == "find_purchase":
            numbers = re.findall(r'\d+', ui_lower)
            if numbers:
                qty    = int(numbers[0])
                result = df[df["total_purchase"] == qty]
                if not result.empty:
                    names = result["product_name"].tolist()
                    response = (f"Products with purchase qty {qty}:\n" +
                                "\n".join(f"  {i}. {n}" for i, n in enumerate(names, 1)) +
                                f"\n\nTotal: {len(names)}")
                else:
                    response = f"No product found with purchase quantity {qty}."

        elif prediction == "find_sell":
            numbers = re.findall(r'\d+', ui_lower)
            if numbers:
                qty    = int(numbers[0])
                result = df[df["total_sell"] == qty]
                if not result.empty:
                    names = result["product_name"].tolist()
                    response = (f"Products with sell qty {qty}:\n" +
                                "\n".join(f"  {i}. {n}" for i, n in enumerate(names, 1)) +
                                f"\n\nTotal: {len(names)}")
                else:
                    response = f"No product found with sell quantity {qty}."

        elif prediction == "find_stock":
            numbers = re.findall(r'\d+', ui_lower)
            if numbers:
                qty    = int(numbers[0])
                result = df[df["current_stock"] == qty]
                if not result.empty:
                    names = result["product_name"].tolist()
                    response = (f"Products with stock qty {qty}:\n" +
                                "\n".join(f"  {i}. {n}" for i, n in enumerate(names, 1)) +
                                f"\n\nTotal: {len(names)}")
                else:
                    response = f"No product found with stock quantity {qty}."

        elif prediction == "low_stock":
            low_df = df[df["current_stock"] < 50]
            if not low_df.empty:
                lines = [f"  • {r['product_name']}  (Stock: {int(r['current_stock'])})"
                         for _, r in low_df.iterrows()]
                response = "⚠️ Low stock products:\n\n" + "\n".join(lines)
            else:
                response = "✅ All products have sufficient stock (≥ 50 units)."

        add_chat_message("bot", response)

    # ═══════════════════════════════════════════════════════════════════════
    # TREEVIEW STYLE
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
    header = tk.Frame(stock_win, bg=C_HEADER, height=64)
    header.pack(fill=X)
    header.pack_propagate(False)

    dot = tk.Canvas(header, width=36, height=36, bg=C_HEADER, highlightthickness=0)
    dot.pack(side=LEFT, padx=(20, 6), pady=14)
    dot.create_oval(4, 4, 32, 32, fill=C_ACCENT, outline="")

    tk.Label(header, text="ERP Billing System",
             font=("Segoe UI", 18, "bold"),
             bg=C_HEADER, fg=C_TEXT).pack(side=LEFT, pady=14)
    tk.Label(header, text="Stock Management",
             font=("Segoe UI", 11),
             bg=C_HEADER, fg=C_MUTED).pack(side=LEFT, padx=(8, 0), pady=17)

    action_button(header, "Refresh", C_ACCENT3, load_data, width=10).pack(
        side=RIGHT, padx=(6, 10), pady=14)
    action_button(header, "<- Dashboard", C_ACCENT2, move_back, width=14).pack(
        side=RIGHT, padx=(20, 0), pady=14)

    # ═══════════════════════════════════════════════════════════════════════
    # KPI ROW
    # ═══════════════════════════════════════════════════════════════════════
    kpi_row = tk.Frame(stock_win, bg=C_BG)
    kpi_row.pack(fill=X, padx=16, pady=(14, 0))

    kpi_cfgs = [
        ("Total Products",   C_ACCENT),
        ("Total Purchased",  C_ACCENT2),
        ("Total Sold",       C_ACCENT3),
        ("Current Stock",    C_PURPLE),
        ("Low Stock Items",  C_ACCENT4),
    ]

    kpi_vals = []
    for i, (lbl, col) in enumerate(kpi_cfgs):
        frm, val_lbl = kpi_card(kpi_row, lbl, col)
        frm.grid(row=0, column=i, padx=6, pady=4, sticky="nsew")
        kpi_row.columnconfigure(i, weight=1)
        kpi_vals.append(val_lbl)

    (kpi_products_val, kpi_purchase_val, kpi_sell_val,
     kpi_stock_val, kpi_low_val) = kpi_vals

    # ═══════════════════════════════════════════════════════════════════════
    # MAIN LAYOUT
    # ═══════════════════════════════════════════════════════════════════════
    main_frame = tk.Frame(stock_win, bg=C_BG)
    main_frame.pack(fill=BOTH, expand=True, padx=16, pady=14)

    # ── LEFT: Stock table card ────────────────────────────────────────────
    table_card = tk.Frame(main_frame, bg=C_CARD,
                          highlightbackground=C_BORDER, highlightthickness=1)
    table_card.pack(side=LEFT, fill=BOTH, expand=True, padx=(0, 10))

    tk.Frame(table_card, bg=C_ACCENT, height=3).pack(fill=X)

    table_hdr = tk.Frame(table_card, bg=C_CARD)
    table_hdr.pack(fill=X, padx=16, pady=(12, 4))
    tk.Label(table_hdr, text="Product Stock Overview",
             font=("Segoe UI", 13, "bold"),
             bg=C_CARD, fg=C_TEXT).pack(side=LEFT)

    # Legend
    legend = tk.Frame(table_hdr, bg=C_CARD)
    legend.pack(side=RIGHT)
    for color, label in [(C_ACCENT4, "Zero stock"), (C_ACCENT3, "Low stock (<50)")]:
        dot2 = tk.Canvas(legend, width=10, height=10, bg=C_CARD, highlightthickness=0)
        dot2.pack(side=LEFT, padx=(8, 2))
        dot2.create_oval(0, 0, 10, 10, fill=color, outline="")
        tk.Label(legend, text=label, font=("Segoe UI", 8),
                 bg=C_CARD, fg=C_MUTED).pack(side=LEFT)

    tk.Frame(table_card, bg=C_BORDER, height=1).pack(fill=X, padx=16, pady=(0, 6))

    tree_wrap = tk.Frame(table_card, bg=C_CARD)
    tree_wrap.pack(fill=BOTH, expand=True, padx=10, pady=(0, 10))

    columns = ("ID", "Product Name", "Total Purchase", "Total Sell", "Current Stock")
    tree = ttk.Treeview(tree_wrap, columns=columns,
                        show="headings", style="Dark.Treeview")

    col_widths = {"ID": 55, "Product Name": 200, "Total Purchase": 140,
                  "Total Sell": 120, "Current Stock": 130}
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=col_widths.get(col, 130), anchor="center")

    # Row color tags
    tree.tag_configure("odd",  background="#1a2234")
    tree.tag_configure("even", background=C_CARD)
    tree.tag_configure("low",  background="#2b2010", foreground=C_ACCENT3)
    tree.tag_configure("zero", background="#2b1010", foreground=C_ACCENT4)

    vsb = ttk.Scrollbar(tree_wrap, orient="vertical",   command=tree.yview)
    hsb = ttk.Scrollbar(tree_wrap, orient="horizontal", command=tree.xview)
    tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
    vsb.pack(side=RIGHT, fill=Y)
    hsb.pack(side=BOTTOM, fill=X)
    tree.pack(fill=BOTH, expand=True)

    # ── RIGHT: Chatbot card ───────────────────────────────────────────────
    chat_card = tk.Frame(main_frame, bg=C_CARD,
                         highlightbackground=C_BORDER, highlightthickness=1,
                         width=380)
    chat_card.pack(side=RIGHT, fill=BOTH)
    chat_card.pack_propagate(False)

    tk.Frame(chat_card, bg=C_ACCENT3, height=3).pack(fill=X)

    chat_hdr = tk.Frame(chat_card, bg=C_CARD)
    chat_hdr.pack(fill=X, padx=16, pady=(12, 4))
    tk.Label(chat_hdr, text="ERP AI Assistant – Mitra",
             font=("Segoe UI", 12, "bold"),
             bg=C_CARD, fg=C_TEXT).pack(side=LEFT)

    tk.Frame(chat_card, bg=C_BORDER, height=1).pack(fill=X, padx=16, pady=(0, 6))

    # Quick-ask chips
    chip_row = tk.Frame(chat_card, bg=C_CARD)
    chip_row.pack(fill=X, padx=12, pady=(0, 6))
    tk.Label(chip_row, text="Quick ask:",
             font=("Segoe UI", 8), bg=C_CARD, fg=C_MUTED).pack(side=LEFT)

    quick_asks = ["Low stock", "Total stock", "List all"]
    for qa in quick_asks:
        btn = tk.Button(chip_row, text=qa,
                        font=("Segoe UI", 8), bg=C_BORDER,
                        fg=C_TEXT, relief=FLAT, padx=6, pady=2,
                        cursor="hand2",
                        command=lambda q=qa: (entry_chat.delete(0, END),
                                              entry_chat.insert(0, q),
                                              chatbot_response()))
        btn.pack(side=LEFT, padx=(6, 0))

    chat_display = scrolledtext.ScrolledText(
        chat_card,
        font=("Segoe UI", 10), wrap="word",
        relief=FLAT, bg=C_INPUT, fg=C_TEXT,
        insertbackground=C_TEXT, bd=0, padx=8, pady=8
    )
    chat_display.pack(fill=BOTH, expand=True, padx=12, pady=(0, 6))
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

    action_button(chat_input_row, "Ask", C_ACCENT,
                  chatbot_response, width=8).pack(side=RIGHT)

    # ═══════════════════════════════════════════════════════════════════════
    # FOOTER
    # ═══════════════════════════════════════════════════════════════════════
    footer = tk.Frame(stock_win, bg=C_HEADER, height=30)
    footer.pack(fill=X, side=BOTTOM)
    footer.pack_propagate(False)
    tk.Label(footer,
             text="Developed by Mahendra Suthar  ·  ERP Billing System",
             font=("Segoe UI", 8),
             bg=C_HEADER, fg=C_MUTED).pack(pady=7)

    # ═══════════════════════════════════════════════════════════════════════
    # INITIAL LOAD
    # ═══════════════════════════════════════════════════════════════════════
    load_data()
    stock_win.mainloop()