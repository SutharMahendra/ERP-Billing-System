import tkinter as tk
from tkinter import ttk, messagebox, END, FLAT, BOTH, X, Y, LEFT, RIGHT, W, EW, BOTTOM, NW
import sqlite3
import pandas as pd
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

# ─── Reusable helpers ─────────────────────────────────────────────────────────
def styled_entry(parent, textvariable=None, width=28):
    return tk.Entry(parent, textvariable=textvariable, width=width,
                    bg=C_INPUT, fg=C_TEXT, insertbackground=C_TEXT,
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

def styled_combo(parent, textvariable, values, width=27):
    style = ttk.Style()
    style.configure("Dark.TCombobox",
                    fieldbackground=C_INPUT,
                    background=C_INPUT,
                    foreground=C_TEXT,
                    arrowcolor=C_ACCENT,
                    borderwidth=0,
                    font=("Segoe UI", 10))
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
    val = tk.Label(frm, text="—", font=("Segoe UI", 16, "bold"),
                   bg=C_CARD, fg=C_TEXT)
    val.pack(anchor=W, padx=10, pady=(2, 8))
    return frm, val


product_id = None


def open_product():
    global product_id

    conn   = sqlite3.connect("ERP_Billing.db")
    cursor = conn.cursor()

    root = tk.Tk()
    root.title("ERP Billing System – Product Management")
    root.state("zoomed")
    root.configure(bg=C_BG)

    # ── Variables ────────────────────────────────────────────────────────
    short_name_var    = tk.StringVar()
    company_name_var  = tk.StringVar()
    hsn_code_var      = tk.StringVar()
    product_name_var  = tk.StringVar()
    product_price_var = tk.StringVar()
    gst_rate_var      = tk.StringVar()
    primary_unit_var  = tk.StringVar()
    category_var      = tk.StringVar()

    # ═══════════════════════════════════════════════════════════════════════
    # FUNCTIONS
    # ═══════════════════════════════════════════════════════════════════════

    def clear_product():
        global product_id
        product_id = None
        short_name_var.set("")
        company_name_var.set("")
        hsn_code_var.set("")
        product_name_var.set("")
        product_price_var.set("")
        gst_rate_var.set("")
        primary_unit_var.set("")
        category_var.set("")
        remark_text.delete("1.0", END)

    def fetch_data():
        tree.delete(*tree.get_children())
        cursor.execute("SELECT * FROM product")
        rows = cursor.fetchall()
        for idx, row in enumerate(rows):
            tag = "odd" if idx % 2 == 0 else "even"
            tree.insert("", END, values=row, tags=(tag,))
        summary_data()

    def save_product():
        name  = product_name_var.get().strip()
        price = product_price_var.get().strip()
        if not name or not price:
            messagebox.showerror("ERP Billing", "Product Name and Price are required!")
            return
        cursor.execute("""
            INSERT INTO product (
                short_name, company_name, hsn_code,
                product_name, product_price, product_gst_rate,
                primary_unit, product_category, remark
            ) VALUES (?,?,?,?,?,?,?,?,?)
        """, (
            short_name_var.get(),
            company_name_var.get(),
            hsn_code_var.get(),
            name, price,
            gst_rate_var.get(),
            primary_unit_var.get(),
            category_var.get(),
            remark_text.get("1.0", END).strip()
        ))
        conn.commit()
        messagebox.showinfo("ERP Billing", "Product Saved Successfully ✅")
        fetch_data()
        clear_product()

    def on_select(event):
        global product_id
        selected = tree.focus()
        if not selected:
            return
        data = tree.item(selected)["values"]
        product_id = data[0]
        short_name_var.set(data[1])
        company_name_var.set(data[2])
        hsn_code_var.set(data[3])
        product_name_var.set(data[4])
        product_price_var.set(data[5])
        gst_rate_var.set(data[6])
        primary_unit_var.set(data[7])
        category_var.set(data[8])
        remark_text.delete("1.0", END)
        remark_text.insert(END, data[9])

    def on_update():
        global product_id
        if not product_id:
            messagebox.showerror("ERP Billing", "Please select a product to update!")
            return
        cursor.execute("""
            UPDATE product SET
                short_name=?, company_name=?, hsn_code=?,
                product_name=?, product_price=?, product_gst_rate=?,
                primary_unit=?, product_category=?, remark=?
            WHERE product_id=?
        """, (
            short_name_var.get(), company_name_var.get(), hsn_code_var.get(),
            product_name_var.get(), product_price_var.get(), gst_rate_var.get(),
            primary_unit_var.get(), category_var.get(),
            remark_text.get("1.0", END).strip(),
            product_id
        ))
        conn.commit()
        messagebox.showinfo("ERP Billing", "Product Updated Successfully ✅")
        fetch_data()
        clear_product()

    def on_delete():
        global product_id
        if not product_id:
            messagebox.showerror("ERP Billing", "Please select a product to delete!")
            return
        if messagebox.askyesno("ERP Billing", "Are you sure you want to delete this product?"):
            cursor.execute("DELETE FROM product WHERE product_id=?", (product_id,))
            conn.commit()
            messagebox.showinfo("ERP Billing", "Product Deleted ✅")
            fetch_data()
            clear_product()

    def summary_data():
        cursor.execute("SELECT COUNT(product_id) FROM product")
        total = cursor.fetchone()[0] or 0

        cursor.execute("SELECT AVG(product_price) FROM product")
        avg_price = cursor.fetchone()[0] or 0

        cursor.execute("SELECT MAX(product_price) FROM product")
        max_price = cursor.fetchone()[0] or 0

        cursor.execute("SELECT COUNT(DISTINCT product_category) FROM product")
        categories = cursor.fetchone()[0] or 0

        kpi_total_val.config(text=str(total))
        kpi_avg_val.config(text=f"₹{avg_price:,.2f}")
        kpi_max_val.config(text=f"₹{max_price:,.2f}")
        kpi_cat_val.config(text=str(categories))

    def data_analysis():
        df = pd.read_sql_query("SELECT * FROM product", conn)
        if df.empty:
            messagebox.showinfo("ERP", "No data available for analysis.")
            return

        selected_df  = df[["product_price", "product_gst_rate"]]
        avg_vals     = selected_df.mean().round(2)
        max_vals     = selected_df.max().round(2)
        min_vals     = selected_df.min().round(2)
        median_vals  = selected_df.median().round(2)
        total_products = len(df)

        group_data = df.groupby("product_category").agg(
            total_products=("product_name", "count")
        )

        data  = "╔══════════════════════════════════════╗\n"
        data += "║        ERP PRODUCT ANALYSIS          ║\n"
        data += "╚══════════════════════════════════════╝\n\n"
        data += "PRODUCT PRICE & GST STATISTICS\n"
        data += "─" * 46 + "\n"
        data += f"{'Metric':<15}{'Price (₹)':<18}{'GST Rate (%)'}\n"
        data += "─" * 46 + "\n"
        data += f"{'Average':<15}{avg_vals['product_price']:<18}{avg_vals['product_gst_rate']}\n"
        data += f"{'Maximum':<15}{max_vals['product_price']:<18}{max_vals['product_gst_rate']}\n"
        data += f"{'Minimum':<15}{min_vals['product_price']:<18}{min_vals['product_gst_rate']}\n"
        data += f"{'Median':<15}{median_vals['product_price']:<18}{median_vals['product_gst_rate']}\n\n"
        data += "TOTAL PRODUCTS IN SYSTEM\n"
        data += "─" * 46 + "\n"
        data += f"Total Products : {total_products}\n\n"
        data += "PRODUCT CATEGORY DISTRIBUTION\n"
        data += "─" * 46 + "\n"
        data += f"{'Category':<24}{'Total Products'}\n"
        data += "─" * 46 + "\n"
        for category, row in group_data.iterrows():
            data += f"{category:<24}{row['total_products']}\n"
        data += "═" * 46

        messagebox.showinfo("ERP – Product Analysis", data)

    def move_back():
        root.destroy()
        dashboard.open_dashboard()

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
    header = tk.Frame(root, bg=C_HEADER, height=64)
    header.pack(fill=X)
    header.pack_propagate(False)

    dot = tk.Canvas(header, width=36, height=36, bg=C_HEADER, highlightthickness=0)
    dot.pack(side=LEFT, padx=(20, 6), pady=14)
    dot.create_oval(4, 4, 32, 32, fill=C_ACCENT, outline="")

    tk.Label(header, text="ERP Billing System",
             font=("Segoe UI", 18, "bold"),
             bg=C_HEADER, fg=C_TEXT).pack(side=LEFT, pady=14)
    tk.Label(header, text="Product Management",
             font=("Segoe UI", 11),
             bg=C_HEADER, fg=C_MUTED).pack(side=LEFT, padx=(8, 0), pady=17)

    action_button(header, "← Dashboard", C_ACCENT2, move_back, width=14).pack(
        side=RIGHT, padx=20, pady=14)

    # ═══════════════════════════════════════════════════════════════════════
    # KPI ROW
    # ═══════════════════════════════════════════════════════════════════════
    kpi_row = tk.Frame(root, bg=C_BG)
    kpi_row.pack(fill=X, padx=16, pady=(14, 0))

    kpi_cfgs = [
        ("Total Products",      C_ACCENT),
        ("Avg Price (₹)",       C_ACCENT2),
        ("Max Price (₹)",       C_ACCENT3),
        ("Categories",          C_ACCENT4),
    ]

    kpi_vals = []
    for i, (lbl, col) in enumerate(kpi_cfgs):
        frm, val_lbl = kpi_card(kpi_row, lbl, col)
        frm.grid(row=0, column=i, padx=6, pady=4, sticky="nsew")
        kpi_row.columnconfigure(i, weight=1)
        kpi_vals.append(val_lbl)

    kpi_total_val, kpi_avg_val, kpi_max_val, kpi_cat_val = kpi_vals

    # ═══════════════════════════════════════════════════════════════════════
    # MAIN LAYOUT
    # ═══════════════════════════════════════════════════════════════════════
    main_frame = tk.Frame(root, bg=C_BG)
    main_frame.pack(fill=BOTH, expand=True, padx=16, pady=14)

    # ── LEFT: Form card ──────────────────────────────────────────────────
    form_card = tk.Frame(main_frame, bg=C_CARD,
                         highlightbackground=C_BORDER, highlightthickness=1)
    form_card.pack(side=LEFT, fill=Y, padx=(0, 10), ipadx=16, ipady=10)

    tk.Frame(form_card, bg=C_ACCENT, height=3).pack(fill=X)
    tk.Label(form_card, text="🏷️  Product Details",
             font=("Segoe UI", 13, "bold"),
             bg=C_CARD, fg=C_TEXT).pack(pady=(14, 4), padx=16, anchor=W)
    tk.Frame(form_card, bg=C_BORDER, height=1).pack(fill=X, padx=16, pady=(0, 10))

    form_inner = tk.Frame(form_card, bg=C_CARD)
    form_inner.pack(padx=16)

    field_cfgs = [
        ("Short Name",    "entry", short_name_var,    None),
        ("Company Name",  "entry", company_name_var,  None),
        ("HSN Code",      "entry", hsn_code_var,      None),
        ("Product Name *","entry", product_name_var,  None),
        ("Product Price *","entry",product_price_var, None),
        ("GST Rate (%)",  "combo", gst_rate_var,      ["0", "5", "12", "18", "28"]),
        ("Primary Unit",  "combo", primary_unit_var,  ["PCS", "KG", "GRAM", "LITER", "METER", "BOX"]),
        ("Category",      "combo", category_var,      ["Grocery", "Electronics", "Stationery", "Clothing", "Other"]),
    ]

    for i, (label, ftype, var, vals) in enumerate(field_cfgs):
        tk.Label(form_inner, text=label,
                 font=("Segoe UI", 9),
                 bg=C_CARD, fg=C_MUTED).grid(row=i*2, column=0,
                                              sticky=W, pady=(8, 0))
        if ftype == "combo":
            w = styled_combo(form_inner, var, vals)
        else:
            w = styled_entry(form_inner, textvariable=var)
        w.grid(row=i*2+1, column=0, sticky=EW, pady=(2, 0))

    # Remark
    tk.Label(form_inner, text="Remark",
             font=("Segoe UI", 9),
             bg=C_CARD, fg=C_MUTED).grid(row=16, column=0, sticky=NW, pady=(8, 0))
    remark_text = tk.Text(form_inner, width=28, height=3,
                          font=("Segoe UI", 10),
                          bg=C_INPUT, fg=C_TEXT,
                          insertbackground=C_TEXT,
                          relief=FLAT,
                          highlightthickness=1,
                          highlightbackground=C_BORDER,
                          highlightcolor=C_ACCENT)
    remark_text.grid(row=17, column=0, sticky=EW, pady=(2, 0))

    # Buttons
    tk.Frame(form_card, bg=C_BORDER, height=1).pack(fill=X, padx=16, pady=(14, 8))
    btn_grid = tk.Frame(form_card, bg=C_CARD)
    btn_grid.pack(padx=16, pady=(0, 10))

    btn_cfg = [
        ("💾 Save",     C_ACCENT,  save_product,   0, 0),
        ("✏️ Update",   C_ACCENT2, on_update,       0, 1),
        ("🗑 Delete",   C_ACCENT4, on_delete,       0, 2),
        ("✖ Clear",    C_MUTED,   clear_product,   1, 0),
        ("📊 Analysis", C_ACCENT3, data_analysis,   1, 1),
    ]
    for text, color, cmd, r, c in btn_cfg:
        action_button(btn_grid, text, color, cmd, width=11).grid(
            row=r, column=c, padx=4, pady=4)

    # ── RIGHT: Table card ────────────────────────────────────────────────
    table_card = tk.Frame(main_frame, bg=C_CARD,
                          highlightbackground=C_BORDER, highlightthickness=1)
    table_card.pack(side=RIGHT, fill=BOTH, expand=True)

    tk.Frame(table_card, bg=C_ACCENT2, height=3).pack(fill=X)
    tk.Label(table_card, text="📋  Product Records",
             font=("Segoe UI", 13, "bold"),
             bg=C_CARD, fg=C_TEXT).pack(anchor=W, padx=16, pady=(12, 4))
    tk.Frame(table_card, bg=C_BORDER, height=1).pack(fill=X, padx=16, pady=(0, 6))

    tree_wrap = tk.Frame(table_card, bg=C_CARD)
    tree_wrap.pack(fill=BOTH, expand=True, padx=10, pady=(0, 10))

    columns = ("ID", "Short", "Company", "HSN", "Name", "Price", "GST", "Unit", "Category", "Remark")
    tree = ttk.Treeview(tree_wrap, columns=columns,
                        show="headings", style="Dark.Treeview")

    col_widths = {"ID": 45, "Short": 70, "Company": 110, "HSN": 80,
                  "Name": 130, "Price": 80, "GST": 60,
                  "Unit": 70, "Category": 100, "Remark": 140}
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=col_widths.get(col, 90), anchor=W)

    tree.tag_configure("odd",  background="#1a2234")
    tree.tag_configure("even", background=C_CARD)

    vsb = ttk.Scrollbar(tree_wrap, orient="vertical",   command=tree.yview)
    hsb = ttk.Scrollbar(tree_wrap, orient="horizontal", command=tree.xview)
    tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

    vsb.pack(side=RIGHT, fill=Y)
    hsb.pack(side=BOTTOM, fill=X)
    tree.pack(fill=BOTH, expand=True)
    tree.bind("<<TreeviewSelect>>", on_select)

    # ═══════════════════════════════════════════════════════════════════════
    # FOOTER
    # ═══════════════════════════════════════════════════════════════════════
    footer = tk.Frame(root, bg=C_HEADER, height=30)
    footer.pack(fill=X, side=BOTTOM)
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