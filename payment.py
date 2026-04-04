import tkinter as tk
from tkinter import ttk, messagebox, END, FLAT, BOTH, X, Y, LEFT, RIGHT, W, EW, BOTTOM
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
    """Returns a (frame, value_label) tuple."""
    frm = tk.Frame(parent, bg=C_CARD,
                   highlightbackground=C_BORDER, highlightthickness=1)
    tk.Frame(frm, bg=color, height=3).pack(fill=X)
    tk.Label(frm, text=label, font=("Segoe UI", 8),
             bg=C_CARD, fg=C_MUTED).pack(anchor=W, padx=10, pady=(6, 0))
    val = tk.Label(frm, text="—", font=("Segoe UI", 16, "bold"),
                   bg=C_CARD, fg=C_TEXT)
    val.pack(anchor=W, padx=10, pady=(2, 8))
    return frm, val


payment_id = None


def open_payment():
    global payment_id

    conn   = sqlite3.connect("ERP_Billing.db")
    cursor = conn.cursor()

    root = tk.Tk()
    root.title("ERP Billing System – Payment Management")
    root.state("zoomed")
    root.configure(bg=C_BG)

    # ── Variables ────────────────────────────────────────────────────────
    purchase_id_var     = tk.StringVar()
    bill_number_var     = tk.StringVar()
    payment_type_var    = tk.StringVar()
    payment_status_var  = tk.StringVar()
    amount_var          = tk.StringVar()
    payment_date_var    = tk.StringVar()

    # ═══════════════════════════════════════════════════════════════════════
    # FUNCTIONS
    # ═══════════════════════════════════════════════════════════════════════

    def clear_data():
        global payment_id
        payment_id = None
        purchase_id_var.set("")
        bill_number_var.set("")
        payment_type_var.set("")
        payment_status_var.set("")
        amount_var.set("")
        payment_date_var.set("")
        remark_text.delete("1.0", END)

    def fetch_data():
        for row in tree.get_children():
            tree.delete(row)
        cursor.execute("SELECT * FROM payment")
        rows = cursor.fetchall()
        for idx, row in enumerate(rows):
            tag = "odd" if idx % 2 == 0 else "even"
            tree.insert("", END, values=row, tags=(tag,))
        summary_data()

    def save_payment_data():
        cursor.execute("""
            INSERT INTO payment (
                purchase_id, bill_number, payment_type,
                payment_status, amount, payment_date, remark
            ) VALUES (?,?,?,?,?,?,?)
        """, (
            purchase_id_var.get(),
            bill_number_var.get(),
            payment_type_var.get(),
            payment_status_var.get(),
            amount_var.get(),
            payment_date_var.get(),
            remark_text.get("1.0", END).strip()
        ))
        conn.commit()
        messagebox.showinfo("ERP", "Payment Saved Successfully ✅")
        fetch_data()
        clear_data()

    def on_select(event):
        global payment_id
        selected = tree.focus()
        if not selected:
            return
        data = tree.item(selected, "values")
        payment_id = data[0]
        purchase_id_var.set(data[1])
        bill_number_var.set(data[2])
        payment_type_var.set(data[3])
        payment_status_var.set(data[4])
        amount_var.set(data[5])
        payment_date_var.set(data[6])
        remark_text.delete("1.0", END)
        remark_text.insert(END, data[7])

    def on_update():
        global payment_id
        if not payment_id:
            messagebox.showerror("ERP", "Please select a record to update!")
            return
        cursor.execute("""
            UPDATE payment SET
                purchase_id=?, bill_number=?, payment_type=?,
                payment_status=?, amount=?, payment_date=?, remark=?
            WHERE payment_id=?
        """, (
            purchase_id_var.get(),
            bill_number_var.get(),
            payment_type_var.get(),
            payment_status_var.get(),
            amount_var.get(),
            payment_date_var.get(),
            remark_text.get("1.0", END).strip(),
            payment_id
        ))
        conn.commit()
        messagebox.showinfo("ERP", "Payment Updated Successfully ✅")
        fetch_data()
        clear_data()

    def on_delete():
        global payment_id
        if not payment_id:
            messagebox.showerror("ERP", "Please select a record to delete!")
            return
        if messagebox.askyesno("ERP", "Are you sure you want to delete this record?"):
            cursor.execute("DELETE FROM payment WHERE payment_id=?", (payment_id,))
            conn.commit()
            messagebox.showinfo("ERP", "Payment Deleted ✅")
            fetch_data()
            clear_data()

    def summary_data():
        def safe(q):
            cursor.execute(q)
            v = cursor.fetchone()[0]
            return v if v is not None else 0

        kpi_total_val.config(text=str(safe("SELECT COUNT(payment_id) FROM payment")))
        amt = safe("SELECT SUM(amount) FROM payment")
        kpi_sum_val.config(text=f"₹{amt:,.2f}")
        mx = safe("SELECT MAX(amount) FROM payment")
        kpi_max_val.config(text=f"₹{mx:,.2f}")
        mn = safe("SELECT MIN(amount) FROM payment")
        kpi_min_val.config(text=f"₹{mn:,.2f}")

    def data_analysis():
        query = """
            SELECT s.seller_name, pay.payment_type,
                   pay.payment_status, pay.amount
            FROM seller s
            LEFT JOIN purchase p   ON s.seller_id   = p.seller_id
            LEFT JOIN payment pay  ON p.purchase_id = pay.purchase_id
        """
        df = pd.read_sql_query(query, conn)
        if df.empty or df["amount"].isnull().all():
            messagebox.showinfo("ERP", "No data available for analysis.")
            return

        df = df.dropna(subset=["amount"])
        seller_total          = df.groupby("seller_name")["amount"].sum().round(2)
        payment_type_summary  = df.groupby("payment_type")["amount"].sum().round(2)
        payment_status_summary= df.groupby("payment_status")["amount"].sum().round(2)

        top_seller = seller_total.idxmax()
        top_amount = seller_total.max()
        low_seller = seller_total.idxmin()
        low_amount = seller_total.min()

        data  = "╔══════════════════════════════════════╗\n"
        data += "║        ERP PAYMENT ANALYSIS          ║\n"
        data += "╚══════════════════════════════════════╝\n\n"
        data += "SUPPLIER PAYMENT REPORT\n"
        data += "─" * 42 + "\n"
        data += f"Max Payment Supplier  : {top_seller}\n"
        data += f"Amount                : ₹ {top_amount:,.2f}\n\n"
        data += f"Min Payment Supplier  : {low_seller}\n"
        data += f"Amount                : ₹ {low_amount:,.2f}\n\n"
        data += "PAYMENT TYPE SUMMARY\n"
        data += "─" * 42 + "\n"
        data += f"{'Payment Type':<22}{'Total Amount'}\n"
        data += "─" * 42 + "\n"
        for ptype, amt in payment_type_summary.items():
            data += f"{ptype:<22}₹ {amt:,.2f}\n"
        data += "\nPAYMENT STATUS SUMMARY\n"
        data += "─" * 42 + "\n"
        data += f"{'Status':<22}{'Total Amount'}\n"
        data += "─" * 42 + "\n"
        for status, amt in payment_status_summary.items():
            data += f"{status:<22}₹ {amt:,.2f}\n"
        data += "═" * 42

        messagebox.showinfo("ERP – Payment Analysis", data)

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
    tk.Label(header, text="Payment Management",
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
        ("Total Payments",      C_ACCENT),
        ("Total Amount (₹)",    C_ACCENT2),
        ("Max Transaction (₹)", C_ACCENT3),
        ("Min Transaction (₹)", C_ACCENT4),
    ]

    kpi_frames = []
    for i, (lbl, col) in enumerate(kpi_cfgs):
        frm, val_lbl = kpi_card(kpi_row, lbl, col)
        frm.grid(row=0, column=i, padx=6, pady=4, sticky="nsew")
        kpi_row.columnconfigure(i, weight=1)
        kpi_frames.append(val_lbl)

    kpi_total_val, kpi_sum_val, kpi_max_val, kpi_min_val = kpi_frames

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
    tk.Label(form_card, text="💳  Payment Details",
             font=("Segoe UI", 13, "bold"),
             bg=C_CARD, fg=C_TEXT).pack(pady=(14, 4), padx=16, anchor=W)
    tk.Frame(form_card, bg=C_BORDER, height=1).pack(fill=X, padx=16, pady=(0, 10))

    form_inner = tk.Frame(form_card, bg=C_CARD)
    form_inner.pack(padx=16)

    # Load purchase data for comboboxes
    cursor.execute("SELECT purchase_id, bill_number FROM purchase")
    purchase_data = cursor.fetchall()
    bill_dict = {str(pid): bill for pid, bill in purchase_data}

    field_cfgs = [
        ("Purchase ID",     "combo",  purchase_id_var,    list(bill_dict.keys())),
        ("Bill Number",     "combo",  bill_number_var,    list(bill_dict.values())),
        ("Payment Type",    "combo",  payment_type_var,   ["Cash", "UPI", "Bank Transfer", "Cheque"]),
        ("Payment Status",  "combo",  payment_status_var, ["Paid", "Pending", "Partial"]),
        ("Amount",          "entry",  amount_var,         None),
        ("Payment Date",    "entry",  payment_date_var,   None),
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
             bg=C_CARD, fg=C_MUTED).grid(row=12, column=0, sticky=W, pady=(8, 0))
    remark_text = tk.Text(form_inner, width=28, height=3,
                          font=("Segoe UI", 10),
                          bg=C_INPUT, fg=C_TEXT,
                          insertbackground=C_TEXT,
                          relief=FLAT,
                          highlightthickness=1,
                          highlightbackground=C_BORDER,
                          highlightcolor=C_ACCENT)
    remark_text.grid(row=13, column=0, sticky=EW, pady=(2, 0))

    # Buttons
    tk.Frame(form_card, bg=C_BORDER, height=1).pack(fill=X, padx=16, pady=(14, 8))
    btn_grid = tk.Frame(form_card, bg=C_CARD)
    btn_grid.pack(padx=16, pady=(0, 10))

    btn_cfg = [
        ("💾 Save",     C_ACCENT,  save_payment_data, 0, 0),
        ("✏️ Update",   C_ACCENT2, on_update,         0, 1),
        ("🗑 Delete",   C_ACCENT4, on_delete,         0, 2),
        ("✖ Clear",    C_MUTED,   clear_data,        1, 0),
        ("📊 Analysis", C_ACCENT3, data_analysis,     1, 1),
    ]
    for text, color, cmd, r, c in btn_cfg:
        action_button(btn_grid, text, color, cmd, width=11).grid(
            row=r, column=c, padx=4, pady=4)

    # ── RIGHT: Table card ────────────────────────────────────────────────
    table_card = tk.Frame(main_frame, bg=C_CARD,
                          highlightbackground=C_BORDER, highlightthickness=1)
    table_card.pack(side=RIGHT, fill=BOTH, expand=True)

    tk.Frame(table_card, bg=C_ACCENT2, height=3).pack(fill=X)
    tk.Label(table_card, text="📋  Payment Records",
             font=("Segoe UI", 13, "bold"),
             bg=C_CARD, fg=C_TEXT).pack(anchor=W, padx=16, pady=(12, 4))
    tk.Frame(table_card, bg=C_BORDER, height=1).pack(fill=X, padx=16, pady=(0, 6))

    tree_wrap = tk.Frame(table_card, bg=C_CARD)
    tree_wrap.pack(fill=BOTH, expand=True, padx=10, pady=(0, 10))

    columns = ("ID", "Purchase ID", "Bill No", "Type",
               "Status", "Amount", "Date", "Remark")
    tree = ttk.Treeview(tree_wrap, columns=columns,
                        show="headings", style="Dark.Treeview")

    col_widths = {"ID": 50, "Purchase ID": 90, "Bill No": 100, "Type": 110,
                  "Status": 90, "Amount": 100, "Date": 110, "Remark": 160}
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=col_widths.get(col, 100), anchor=W)

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