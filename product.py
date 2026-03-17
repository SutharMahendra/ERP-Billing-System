import tkinter as tk
from tkinter import *
from tkinter import ttk, messagebox
import sqlite3
import pandas as pd
import dashboard

product_id = None

def open_product():
    global product_id

    conn = sqlite3.connect("ERP_Billing.db")
    cursor = conn.cursor()

    root = tk.Tk()
    root.title("Product Management Dashboard")
    root.state("zoomed")
    root.configure(bg="#f0f2f5")

    # ---------- Styling ----------
    style = ttk.Style()
    style.theme_use("clam")

    style.configure("TLabel", font=("Segoe UI", 11), background="#f0f2f5")
    style.configure("TButton",
                    font=("Segoe UI", 10, "bold"),
                    padding=8)
    style.configure("Treeview",
                    font=("Segoe UI", 10),
                    rowheight=28)
    style.configure("Treeview.Heading",
                    font=("Segoe UI", 10, "bold"))

    # ---------- Functions ----------

    def save_product():
        name = product_name_var.get()
        price = product_price_var.get()

        if name == "" or price == "":
            messagebox.showerror("ERP Billing", "Product Name and Price are required!")
            return

        cursor.execute("""
            INSERT INTO product(
                short_name, company_name, hsn_code,
                product_name, product_price, product_gst_rate,
                primary_unit, product_category, remark
            )
            VALUES(?,?,?,?,?,?,?,?,?)
        """, (
            short_name_var.get(),
            company_name_var.get(),
            hsn_code_var.get(),
            name,
            price,
            gst_rate_var.get(),
            primary_unit_var.get(),
            category_var.get(),
            remark_text.get("1.0", END).strip()
        ))

        conn.commit()
        fetch_data()
        clear_product()
        summary_data()
        messagebox.showinfo("ERP Billing", "Product saved successfully")

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
        for row in rows:
            tree.insert("", END, values=row)

    def on_select(event):
        global product_id
        selected = tree.focus()
        if selected:
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
            messagebox.showerror("ERP Billing", "Select a product to update")
            return

        cursor.execute("""
            UPDATE product SET
                short_name=?,
                company_name=?,
                hsn_code=?,
                product_name=?,
                product_price=?,
                product_gst_rate=?,
                primary_unit=?,
                product_category=?,
                remark=?
            WHERE product_id=?
        """, (
            short_name_var.get(),
            company_name_var.get(),
            hsn_code_var.get(),
            product_name_var.get(),
            product_price_var.get(),
            gst_rate_var.get(),
            primary_unit_var.get(),
            category_var.get(),
            remark_text.get("1.0", END).strip(),
            product_id
        ))

        conn.commit()
        fetch_data()
        clear_product()
        summary_data()

    def on_delete():
        global product_id
        if not product_id:
            messagebox.showerror("ERP Billing", "Select a product to delete")
            return

        cursor.execute("DELETE FROM product WHERE product_id=?", (product_id,))
        conn.commit()

        fetch_data()
        clear_product()
        summary_data()

    def data_analysis():
        df = pd.read_sql_query("SELECT * FROM product", conn)

        if df.empty:
            messagebox.showinfo("ERP", "No data available for analysis.")
            return
        
        selected_df = df[["product_price", "product_gst_rate"]]
        
        # ---------- Calculations ----------
        avg_vals = selected_df.mean().round(2)
        max_vals = selected_df.max().round(2)
        min_vals = selected_df.min().round(2)
        median_vals = selected_df.median().round(2)
        
        total_products = len(df)
        
        group_data = df.groupby("product_category").agg(
            total_products=("product_name", "count")
        )
        
        
        # ---------- FORMAT OUTPUT ----------
        data = ""
        data += "╔══════════════════════════════════════╗\n"
        data += "║        ERP PRODUCT ANALYSIS          ║\n"
        data += "╚══════════════════════════════════════╝\n\n"
        
        
        # ---------- Basic Statistics ----------
        data += "PRODUCT PRICE & GST STATISTICS\n"
        data += "------------------------------------------------\n"
        data += f"{'Metric':<15}{'Price':<15}{'GST Rate'}\n"
        data += "------------------------------------------------\n"
        
        data += f"{'Average':<15}{avg_vals['product_price']:<15}{avg_vals['product_gst_rate']}\n"
        data += f"{'Maximum':<15}{max_vals['product_price']:<15}{max_vals['product_gst_rate']}\n"
        data += f"{'Minimum':<15}{min_vals['product_price']:<15}{min_vals['product_gst_rate']}\n"
        data += f"{'Median':<15}{median_vals['product_price']:<15}{median_vals['product_gst_rate']}\n"
        
        data += "\n"
        
        
        # ---------- Total Products ----------
        data += "TOTAL PRODUCTS IN SYSTEM\n"
        data += "------------------------------------------------\n"
        data += f"Total Products : {total_products}\n\n"
        
        
        # ---------- Category Analysis ----------
        data += "PRODUCT CATEGORY DISTRIBUTION\n"
        data += "------------------------------------------------\n"
        data += f"{'Category':<20}{'Total Products'}\n"
        data += "------------------------------------------------\n"
        
        for category, row in group_data.iterrows():
            data += f"{category:<20}{row['total_products']}\n"
        
        data += "\n=========================================="
        
        
        # ---------- Show Result ----------
        messagebox.showinfo("ERP Data Analysis", data)

    def summary_data():
        cursor.execute("SELECT COUNT(product_id) FROM product")
        total = cursor.fetchone()[0]
        total_product.config(text=f"Total Products : {total}")

    def move_back():
        root.destroy()
        dashboard.open_dashboard()

    # ---------- Header ----------
    header = Frame(root, bg="#1f6aa5", height=70)
    header.pack(fill=X)

    Label(header,
          text="Product Management Dashboard",
          font=("Segoe UI", 22, "bold"),
          bg="#1f6aa5",
          fg="white").pack(pady=15)

    # ---------- Main Frame ----------
    main_frame = Frame(root, bg="#f0f2f5")
    main_frame.pack(fill=BOTH, expand=True, padx=20, pady=20)

    # ---------- Left Frame ----------
    form_frame = Frame(main_frame, bg="white")
    form_frame.pack(side=LEFT, fill=Y, padx=10, ipadx=15, ipady=15)

    Label(form_frame,
          text="Product Details",
          font=("Segoe UI", 14, "bold"),
          bg="white").grid(row=0, columnspan=2, pady=15)

    short_name_var = StringVar()
    company_name_var = StringVar()
    hsn_code_var = StringVar()
    product_name_var = StringVar()
    product_price_var = StringVar()
    gst_rate_var = StringVar()
    primary_unit_var = StringVar()
    category_var = StringVar()

    labels = [
        "Short Name",
        "Company Name",
        "HSN Code",
        "Product Name",
        "Product Price",
        "GST Rate",
        "Primary Unit",
        "Category"
    ]

    for i, text in enumerate(labels):
        ttk.Label(form_frame, text=text).grid(row=i+1, column=0, sticky=W, pady=8)

    ttk.Entry(form_frame, textvariable=short_name_var, width=30).grid(row=1, column=1)
    ttk.Entry(form_frame, textvariable=company_name_var, width=30).grid(row=2, column=1)
    ttk.Entry(form_frame, textvariable=hsn_code_var, width=30).grid(row=3, column=1)
    ttk.Entry(form_frame, textvariable=product_name_var, width=30).grid(row=4, column=1)
    ttk.Entry(form_frame, textvariable=product_price_var, width=30).grid(row=5, column=1)

    ttk.Combobox(form_frame, textvariable=gst_rate_var,
                 values=["0", "5", "12", "18", "28"],
                 state="readonly", width=27).grid(row=6, column=1)

    ttk.Combobox(form_frame, textvariable=primary_unit_var,
                 values=["PCS", "KG", "GRAM", "LITER", "METER", "BOX"],
                 state="readonly", width=27).grid(row=7, column=1)

    ttk.Combobox(form_frame, textvariable=category_var,
                 values=["Grocery", "Electronics", "Stationery", "Clothing", "Other"],
                 state="readonly", width=27).grid(row=8, column=1)

    ttk.Label(form_frame, text="Remark").grid(row=9, column=0, sticky=NW, pady=8)
    remark_text = Text(form_frame, width=23, height=4, font=("Segoe UI", 10))
    remark_text.grid(row=9, column=1)

    # ---------- Buttons ----------
    button_frame = Frame(form_frame, bg="white")
    button_frame.grid(row=10, columnspan=2, pady=20)

    ttk.Button(button_frame, text="Save", command=save_product).grid(row=0, column=0, padx=5)
    ttk.Button(button_frame, text="Update", command=on_update).grid(row=0, column=1, padx=5)
    ttk.Button(button_frame, text="Delete", command=on_delete).grid(row=0, column=2, padx=5)
    ttk.Button(button_frame, text="Clear", command=clear_product).grid(row=0, column=3, padx=5)
    ttk.Button(button_frame, text="Analysis", command=data_analysis).grid(row=0, column=4, padx=5)
    ttk.Button(button_frame, text="Back", command=move_back).grid(row=0, column=5, padx=5)

    # ---------- Right Frame ----------
    data_frame = Frame(main_frame, bg="white")
    data_frame.pack(side=RIGHT, fill=BOTH, expand=True, padx=10)

    Label(data_frame,
          text="Product Records",
          font=("Segoe UI", 14, "bold"),
          bg="white").pack(pady=10)

    columns = ("ID", "Short", "Company", "HSN", "Name", "Price", "GST", "Unit", "Category", "Remark")
    tree = ttk.Treeview(data_frame, columns=columns, show="headings")

    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=110)

    tree.pack(fill=BOTH, expand=True)

    scrollbar = ttk.Scrollbar(data_frame, orient=VERTICAL, command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side=RIGHT, fill=Y)

    tree.bind("<<TreeviewSelect>>", on_select)

    # ---------- Summary ----------
    summary_frame = Frame(root, bg="#f0f2f5")
    summary_frame.pack(pady=10)

    total_product = Label(summary_frame,
                          text="",
                          font=("Segoe UI", 11, "bold"),
                          bg="#f0f2f5")
    total_product.pack()

    fetch_data()
    summary_data()

    root.mainloop()