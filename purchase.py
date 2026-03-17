import tkinter as tk
from tkinter import *
from tkinter import ttk, messagebox
import sqlite3
from datetime import date
import pandas as pd
import dashboard

purchase_id = None

def open_purchase():
    global purchase_id

    conn = sqlite3.connect("ERP_Billing.db")
    cursor = conn.cursor()

    root = tk.Tk()
    root.title("Purchase Management Dashboard")
    root.state("zoomed")
    root.configure(bg="#f0f2f5")

    # ---------- Styling ----------
    style = ttk.Style()
    style.theme_use("clam")

    style.configure("TLabel", font=("Segoe UI", 11), background="#f0f2f5")
    style.configure("TButton", font=("Segoe UI", 10, "bold"), padding=8)
    style.configure("Treeview", font=("Segoe UI", 10), rowheight=28)
    style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))

    # ---------- Variables ----------
    bill_var = StringVar()
    seller_id_var = StringVar()
    user_id_var = StringVar()
    purchase_date_var = StringVar(value=date.today().strftime("%Y-%m-%d"))
    product_id_var = StringVar()
    quantity_var = StringVar()
    price_var = StringVar()
    gst_rate_var = StringVar()
    gst_amount_var = StringVar()
    total_amount_var = StringVar()

    # ---------- Functions ----------
    # ---------- Calculate Amount ----------
    def calculate_amount(*args):
        try:
            qty = float(quantity_var.get())
            price = float(price_var.get())
            gst = float(gst_rate_var.get())

            amount = qty * price
            gst_amt = amount * gst / 100
            total = amount + gst_amt

            gst_amount_var.set(round(gst_amt, 2))
            total_amount_var.set(round(total, 2))
        except:
            pass

    def save_purchase():
        if bill_var.get() == "" or product_id_var.get() == "":
            messagebox.showerror("ERP Billing", "Bill Number & Product required")
            return

        cursor.execute("""
            INSERT INTO purchase (
                bill_number, seller_id, user_id, purchase_date,
                product_id, product_quantity, product_price,
                product_gst_rate, gst_amount, total_amount, remark
            )
            VALUES (?,?,?,?,?,?,?,?,?,?,?)
        """, (
            bill_var.get(),
            seller_id_var.get(),
            user_id_var.get(),
            purchase_date_var.get(),
            product_id_var.get(),
            quantity_var.get(),
            price_var.get(),
            gst_rate_var.get(),
            gst_amount_var.get(),
            total_amount_var.get(),
            remark_text.get("1.0", END).strip()
        ))

        conn.commit()
        fetch_data()
        clear_purchase()
        purchase_summary()
        messagebox.showinfo("ERP Billing", "Purchase saved successfully")

    def clear_purchase():
        global purchase_id
        purchase_id = None
        bill_var.set("")
        seller_id_var.set("")
        user_id_var.set("")
        product_id_var.set("")
        quantity_var.set("")
        price_var.set("")
        gst_rate_var.set("")
        gst_amount_var.set("")
        total_amount_var.set("")
        remark_text.delete("1.0", END)

    def fetch_data():
        tree.delete(*tree.get_children())
        cursor.execute("SELECT * FROM purchase")
        rows = cursor.fetchall()
        for row in rows:
            tree.insert("", END, values=row)

    def on_select(event):
        global purchase_id
        selected = tree.focus()
        if selected:
            data = tree.item(selected)["values"]
            purchase_id = data[0]

            bill_var.set(data[1])
            seller_id_var.set(data[2])
            user_id_var.set(data[3])
            purchase_date_var.set(data[4])
            product_id_var.set(data[5])
            quantity_var.set(data[6])
            price_var.set(data[7])
            gst_rate_var.set(data[8])
            gst_amount_var.set(data[9])
            total_amount_var.set(data[10])

            remark_text.delete("1.0", END)
            remark_text.insert(END, data[11])

    def on_update():
        global purchase_id
        if not purchase_id:
            messagebox.showerror("ERP Billing", "Select record to update")
            return

        cursor.execute("""
            UPDATE purchase SET
                bill_number=?, seller_id=?, user_id=?, purchase_date=?,
                product_id=?, product_quantity=?, product_price=?,
                product_gst_rate=?, gst_amount=?, total_amount=?, remark=?
            WHERE purchase_id=?
        """, (
            bill_var.get(),
            seller_id_var.get(),
            user_id_var.get(),
            purchase_date_var.get(),
            product_id_var.get(),
            quantity_var.get(),
            price_var.get(),
            gst_rate_var.get(),
            gst_amount_var.get(),
            total_amount_var.get(),
            remark_text.get("1.0", END).strip(),
            purchase_id
        ))

        conn.commit()
        fetch_data()
        clear_purchase()
        purchase_summary()

    def on_delete():
        global purchase_id
        if not purchase_id:
            messagebox.showerror("ERP Billing", "Select record to delete")
            return

        cursor.execute("DELETE FROM purchase WHERE purchase_id=?", (purchase_id,))
        conn.commit()

        fetch_data()
        clear_purchase()
        purchase_summary()

    # ---------- Data Analysis ----------
    def data_analysis():
        df = pd.read_sql_query("""
        SELECT s.purchase_id,
               s.seller_id,
               s.product_id,
               s.product_quantity,
               s.product_price,
               s.total_amount,
               p.product_name,
               p.product_category,
               sel.seller_company_name
        FROM purchase as s
        LEFT JOIN product p ON s.product_id = p.product_id
        LEFT JOIN seller sel ON s.seller_id = sel.seller_id
    """, conn)

        if df.empty:
            messagebox.showinfo("ERP", "No data available for analysis.")
            return
        
        data = ""
        
        # ------------------------------------------------
        # Product Quantity Analysis
        # ------------------------------------------------
        grouped_product = df.groupby("product_name")["product_quantity"].sum().round(2)
        
        top_product = grouped_product.idxmax()
        top_product_qty = grouped_product.max()
        
        least_product = grouped_product.idxmin()
        least_product_qty = grouped_product.min()
        
        # ------------------------------------------------
        # Seller Quantity Analysis
        # ------------------------------------------------
        grouped_seller_qty = df.groupby("seller_company_name")["product_quantity"].sum().round(2)
        
        top_seller = grouped_seller_qty.idxmax()
        top_seller_qty = grouped_seller_qty.max()
        
        least_seller = grouped_seller_qty.idxmin()
        least_seller_qty = grouped_seller_qty.min()
        
        # ------------------------------------------------
        # Seller Profit Analysis
        # ------------------------------------------------
        grouped_profit = df.groupby("seller_company_name")["total_amount"].sum().round(2)
        
        profit_seller = grouped_profit.idxmax()
        profit_amount = grouped_profit.max()
        
        loss_seller = grouped_profit.idxmin()
        loss_amount = grouped_profit.min()
        
        # ------------------------------------------------
        # Price Analysis
        # ------------------------------------------------
        highest_price_row = df.loc[df["product_price"].idxmax()]
        lowest_price_row = df.loc[df["product_price"].idxmin()]
        
        
        # =================================================
        # FORMAT OUTPUT
        # =================================================
        data += "╔══════════════════════════════════════╗\n"
        data += "║        ERP PURCHASE ANALYSIS         ║\n"
        data += "╚══════════════════════════════════════╝\n\n"
        
        
        # ---------- Product Quantity ----------
        data += "PRODUCT QUANTITY ANALYSIS\n"
        data += "------------------------------------------------\n"
        data += f"Top Product (Most Purchased)   : {top_product}\n"
        data += f"Total Quantity                 : {top_product_qty}\n\n"
        
        data += f"Least Purchased Product        : {least_product}\n"
        data += f"Total Quantity                 : {least_product_qty}\n\n"
        
        
        # ---------- Seller Quantity ----------
        data += "SELLER SUPPLY ANALYSIS\n"
        data += "------------------------------------------------\n"
        data += f"Top Seller (Highest Supply)    : {top_seller}\n"
        data += f"Total Quantity Supplied        : {top_seller_qty}\n\n"
        
        data += f"Least Seller (Lowest Supply)   : {least_seller}\n"
        data += f"Total Quantity Supplied        : {least_seller_qty}\n\n"
        
        
        # ---------- Profit Analysis ----------
        data += "SELLER PROFIT ANALYSIS\n"
        data += "------------------------------------------------\n"
        data += f"Most Profitable Seller         : {profit_seller}\n"
        data += f"Total Business Value           : ₹ {profit_amount}\n\n"
        
        data += f"Least Profitable Seller        : {loss_seller}\n"
        data += f"Total Business Value           : ₹ {loss_amount}\n\n"
        
        
        # ---------- Price Analysis ----------
        data += "PRODUCT PRICE ANALYSIS\n"
        data += "------------------------------------------------\n"
        data += f"Highest Price Product          : {highest_price_row['product_name']}\n"
        data += f"Price                          : ₹ {highest_price_row['product_price']}\n\n"
        
        data += f"Lowest Price Product           : {lowest_price_row['product_name']}\n"
        data += f"Price                          : ₹ {lowest_price_row['product_price']}\n\n"
        
        data += "=========================================="
        
        # ---------- Show Result ----------
        messagebox.showinfo("ERP Data Analysis", data)

    # ---------- Summary Data  ----------
    def purchase_summary():
        cursor.execute("SELECT * FROM purchase")
        rows = cursor.fetchall()

        if not rows:
            total_purchase_label.config(text="Total Purchase Records : 0")
            return

        import pandas as pd

        df = pd.read_sql_query("SELECT * FROM purchase", conn)

        # ---- Calculations ----
        total_records = len(df)

        total_quantity = df["product_quantity"].sum()
        min_quantity = df["product_quantity"].min()
        max_quantity = df["product_quantity"].max()

        total_price = df["product_price"].sum()
        min_price = df["product_price"].min()
        max_price = df["product_price"].max()

        total_amount = df["total_amount"].sum()
        min_amount = df["total_amount"].min()
        max_amount = df["total_amount"].max()

        # ---- Update Labels ----
        total_purchase_label.config(text=f"Total Purchase Records : {total_records}")

        total_quantity_label.config(text=f"Total Quantity Purchased : {total_quantity}")
        min_quantity_label.config(text=f"Minimum Quantity (Single Purchase) : {min_quantity}")
        max_quantity_label.config(text=f"Maximum Quantity (Single Purchase) : {max_quantity}")

        total_price_label.config(text=f"Total Purchase Price : ₹ {round(total_price,2)}")
        min_price_label.config(text=f"Lowest Purchase Price : ₹ {round(min_price,2)}")
        max_price_label.config(text=f"Highest Purchase Price : ₹ {round(max_price,2)}")

        total_amount_label.config(text=f"Total Purchase Amount : ₹ {round(total_amount,2)}")
        min_amount_label.config(text=f"Lowest Purchase Amount : ₹ {round(min_amount,2)}")
        max_amount_label.config(text=f"Highest Purchase Amount : ₹ {round(max_amount,2)}")

    def move_back():
        root.destroy()
        dashboard.open_dashboard()

    # ---------- Header ----------
    header = Frame(root, bg="#1f6aa5", height=70)
    header.pack(fill=X)

    Label(header,
          text="Purchase Management Dashboard",
          font=("Segoe UI", 22, "bold"),
          bg="#1f6aa5",
          fg="white").pack(pady=15)

    # ---------- Main Frame ----------
    main_frame = Frame(root, bg="#f0f2f5")
    main_frame.pack(fill=BOTH, expand=True, padx=20, pady=20)

    # ---------- Left Form ----------
    form_frame = Frame(main_frame, bg="white")
    form_frame.pack(side=LEFT, fill=Y, padx=10, ipadx=15, ipady=15)

    Label(form_frame,
          text="Purchase Details",
          font=("Segoe UI", 14, "bold"),
          bg="white").grid(row=0, columnspan=2, pady=15)

      # ---------- Product name list ----------
    cursor.execute("SELECT product_id, product_name FROM product")
    product_data = cursor.fetchall()

    product_dict = {proid:pro_name for proid, pro_name in product_data}
    product_name_list = list(set(product_dict.values()))

    # ---------- Seller name list ----------
    cursor.execute("SELECT seller_id, seller_company_name FROM seller")
    seller_data = cursor.fetchall()

    seller_dict = {sid:s_name for sid, s_name in seller_data}
    seller_name_list = list(set(seller_dict.values()))

    labels = [
        "Bill Number", "Seller", "User",
        "Purchase Date", "Product",
        "Quantity", "Price", "GST Rate",
        "GST Amount", "Total Amount"
    ]

    for i, text in enumerate(labels):
        ttk.Label(form_frame, text=text).grid(row=i+1, column=0, sticky=W, pady=8)

    ttk.Entry(form_frame, textvariable=bill_var, width=30).grid(row=1, column=1)
    ttk.Combobox(form_frame, textvariable=seller_id_var, values=seller_name_list, state="readonly", width=27).grid(row=2, column=1)
    ttk.Entry(form_frame, textvariable=user_id_var, width=30).grid(row=3, column=1)
    ttk.Entry(form_frame, textvariable=purchase_date_var, width=30).grid(row=4, column=1)
    ttk.Combobox(form_frame, textvariable=product_id_var, values=product_name_list, state="readonly", width=27).grid(row=5, column=1)
    ttk.Entry(form_frame, textvariable=quantity_var, width=30).grid(row=6, column=1)
    ttk.Entry(form_frame, textvariable=price_var, width=30).grid(row=7, column=1)
    ttk.Entry(form_frame, textvariable=gst_rate_var, width=30).grid(row=8, column=1)
    ttk.Entry(form_frame, textvariable=gst_amount_var, width=30, state="readonly").grid(row=9, column=1)
    ttk.Entry(form_frame, textvariable=total_amount_var, width=30, state="readonly").grid(row=10, column=1)

    ttk.Label(form_frame, text="Remark").grid(row=11, column=0, sticky=NW)
    remark_text = Text(form_frame, width=23, height=4, font=("Segoe UI", 10))
    remark_text.grid(row=11, column=1)

    quantity_var.trace("w", calculate_amount)
    price_var.trace("w", calculate_amount)
    gst_rate_var.trace("w", calculate_amount)

    # ---------- Buttons ----------
    button_frame = Frame(form_frame, bg="white")
    button_frame.grid(row=12, columnspan=2, pady=20)

    ttk.Button(button_frame, text="Save", command=save_purchase).grid(row=0, column=0, padx=5)
    ttk.Button(button_frame, text="Update", command=on_update).grid(row=0, column=1, padx=5)
    ttk.Button(button_frame, text="Delete", command=on_delete).grid(row=0, column=2, padx=5)
    ttk.Button(button_frame, text="Clear", command=clear_purchase).grid(row=0, column=3, padx=5)
    ttk.Button(button_frame, text="Analysis", command=data_analysis).grid(row=0, column=4, padx=5)
    ttk.Button(button_frame, text="Back", command=move_back).grid(row=0, column=5, padx=5)


    # ---------- Right Frame (Treeview) ----------
    data_frame = Frame(main_frame, bg="white")
    data_frame.pack(side=RIGHT, fill=BOTH, expand=True, padx=10)

    Label(data_frame,
          text="Purchase Records",
          font=("Segoe UI", 14, "bold"),
          bg="white").pack(pady=10)

    columns = ("ID","Bill","Seller","User","Date","Product","Qty","Price","GST%","GST Amt","Total","Remark")
    tree = ttk.Treeview(data_frame, columns=columns, show="headings")

    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=100)

    tree.pack(fill=BOTH, expand=True)

    scrollbar = ttk.Scrollbar(data_frame, orient=VERTICAL, command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side=RIGHT, fill=Y)

    tree.bind("<<TreeviewSelect>>", on_select)

    # ---------- Summary ----------
    summary_frame = Frame(root, bg="#f0f2f5")
    summary_frame.pack(pady=10)

    total_purchase_label = tk.Label(
        summary_frame,
        font=("Segoe UI", 11, "bold"),
        bg="#f0f2f5"
    )
    total_purchase_label.pack(anchor="w", pady=2)

    total_quantity_label = tk.Label(
        summary_frame,
        font=("Segoe UI", 11, "bold"),
        bg="#f0f2f5"
    )
    total_quantity_label.pack(anchor="w", pady=2)

    min_quantity_label = tk.Label(
        summary_frame,
        font=("Segoe UI", 11, "bold"),
        bg="#f0f2f5"
    )
    min_quantity_label.pack(anchor="w", pady=2)

    max_quantity_label = tk.Label(
        summary_frame,
        font=("Segoe UI", 11, "bold"),
        bg="#f0f2f5"
    )
    max_quantity_label.pack(anchor="w", pady=2)

    total_price_label = tk.Label(
        summary_frame,
        font=("Segoe UI", 11, "bold"),
        bg="#f0f2f5"
    )
    total_price_label.pack(anchor="w", pady=2)

    min_price_label = tk.Label(
        summary_frame,
        font=("Segoe UI", 11, "bold"),
        bg="#f0f2f5"
    )
    min_price_label.pack(anchor="w", pady=2)

    max_price_label = tk.Label(
        summary_frame,
        font=("Segoe UI", 11, "bold"),
        bg="#f0f2f5"
    )
    max_price_label.pack(anchor="w", pady=2)

    total_amount_label = tk.Label(
        summary_frame,
        font=("Segoe UI", 11, "bold"),
        bg="#f0f2f5"
    )
    total_amount_label.pack(anchor="w", pady=2)

    min_amount_label = tk.Label(
        summary_frame,
        font=("Segoe UI", 11, "bold"),
        bg="#f0f2f5"
    )
    min_amount_label.pack(anchor="w", pady=2)

    max_amount_label = tk.Label(
        summary_frame,
        font=("Segoe UI", 11, "bold"),
        bg="#f0f2f5"
    )
    max_amount_label.pack(anchor="w", pady=2)

    fetch_data()
    purchase_summary()

    root.mainloop()