import tkinter as tk
from tkinter import *
from tkinter import ttk, messagebox
import sqlite3
import pandas as pd
import dashboard

payment_id = None

def open_payment():

    # ---------- Database ----------
    conn = sqlite3.connect("ERP_Billing.db")
    cursor = conn.cursor()

    # ---------- Window ----------
    root = tk.Tk()
    root.title("Payment Management System")
    root.state("zoomed")

    # ---------- Variables ----------
    purchase_id_var = StringVar()
    bill_number_var = StringVar()
    payment_type_var = StringVar()
    payment_status_var = StringVar()
    amount_var = StringVar()
    payment_date_var = StringVar()

    # ---------- Functions ----------

    def save_payment_data():
        cursor.execute("""
            INSERT INTO payment (
                purchase_id, bill_number,
                payment_type, payment_status,
                amount, payment_date, remark
            )
            VALUES (?,?,?,?,?,?,?)
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
        messagebox.showinfo("ERP", "Payment Saved Successfully")
        fetch_data()
        summary_data()
        clear_data()

    def fetch_data():
        for row in tree.get_children():
            tree.delete(row)

        cursor.execute("SELECT * FROM payment")
        rows = cursor.fetchall()

        for row in rows:
            tree.insert("", END, values=row)

    def on_select(event):
        global payment_id
        selected = tree.focus()
        if selected:
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
            messagebox.showerror("ERP", "Select record to update")
            return

        cursor.execute("""
            UPDATE payment SET
                purchase_id=?,
                bill_number=?,
                payment_type=?,
                payment_status=?,
                amount=?,
                payment_date=?,
                remark=?
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
        fetch_data()
        summary_data()
        clear_data()

    def on_delete():
        global payment_id
        if not payment_id:
            messagebox.showerror("ERP", "Select record to delete")
            return

        cursor.execute("DELETE FROM payment WHERE payment_id=?", (payment_id,))
        conn.commit()
        fetch_data()
        summary_data()
        clear_data()

    def clear_data():
        purchase_id_var.set("")
        bill_number_var.set("")
        payment_type_var.set("")
        payment_status_var.set("")
        amount_var.set("")
        payment_date_var.set("")
        remark_text.delete("1.0", END)

    def summary_data():

        # ---------- total payment ----------
        cursor.execute("SELECT COUNT(payment_id) FROM payment")
        total = cursor.fetchone()[0]

        if total == None:
            total = 0 

        total_payment.config(text=f"Total Buyer : {total}")

        # ---------- total amount ----------
        cursor.execute("SELECT SUM(amount) FROM payment")
        total = cursor.fetchone()[0]

        if total == None:
            total = 0 

        total_amount.config(text=f"Total Transaction Amount : {total}")

        # ---------- Maximum amount ----------
        cursor.execute("SELECT MAX(amount) FROM payment")
        max = cursor.fetchone()[0]

        if max == None:
            max = 0 

        max_amount.config(text=f"Maximum Transaction Amount  : {max}")

        # ---------- minimum amount ----------
        cursor.execute("SELECT MIN(amount) FROM payment")
        min = cursor.fetchone()[0]

        if min == None:
            min = 0 

        min_amount.config(text=f"Minimum Transaction Amount : {min}")


    def data_analysis():
        query = """ 
        SELECT s.seller_id,
               s.seller_name,
               pay.payment_type,
               pay.payment_status,
               pay.payment_date,
               pay.amount
        FROM seller as s 
        LEFT JOIN purchase p ON s.seller_id = p.seller_id
        LEFT JOIN payment pay ON p.purchase_id = pay.purchase_id
        """

        df = pd.read_sql_query(query, conn)
        
        if df.empty:
            messagebox.showinfo("ERP", "No data available")
            return
        
        
        # ---------- Supplier Analysis ----------
        seller_total = df.groupby("seller_name")["amount"].sum().round(2)
        
        top_seller = seller_total.idxmax()
        top_amount = seller_total.max()
        
        low_seller = seller_total.idxmin()
        low_amount = seller_total.min()
        
        
        # ---------- Payment Type ----------
        payment_type_summary = df.groupby("payment_type")["amount"].sum().round(2)
        
        # ---------- Payment Status ----------
        payment_status_summary = df.groupby("payment_status")["amount"].sum().round(2)
        
        
        # ---------- FORMAT DATA ----------
        data = ""
        data += "╔══════════════════════════════════════╗\n"
        data += "║        ERP PAYMENT ANALYSIS          ║\n"
        data += "╚══════════════════════════════════════╝\n\n"
        
        
        # ---------- Supplier Section ----------
        data += "SUPPLIER PAYMENT REPORT\n"
        data += "------------------------------------------------\n"
        data += f"Maximum Payment Supplier : {top_seller}\n"
        data += f"Amount                   : ₹ {top_amount}\n\n"
        
        data += f"Minimum Payment Supplier : {low_seller}\n"
        data += f"Amount                   : ₹ {low_amount}\n\n"
        
        
        # ---------- Payment Type Table ----------
        data += "PAYMENT TYPE SUMMARY\n"
        data += "------------------------------------------------\n"
        data += f"{'Payment Type':<20}{'Total Amount'}\n"
        data += "------------------------------------------------\n"
        
        for ptype, amt in payment_type_summary.items():
            data += f"{ptype:<20}₹ {amt}\n"
        
        data += "\n"
        
        
        # ---------- Payment Status Table ----------
        data += "PAYMENT STATUS SUMMARY\n"
        data += "------------------------------------------------\n"
        data += f"{'Status':<20}{'Total Amount'}\n"
        data += "------------------------------------------------\n"
        
        for status, amt in payment_status_summary.items():
            data += f"{status:<20}₹ {amt}\n"
        
        data += "\n================================================"
        
        
        # ---------- Show Result ----------
        messagebox.showinfo("ERP Data Analysis", data)

    def move_back():
        root.destroy()
        dashboard.open_dashboard()

    
    # ---------- Styling ----------
    style = ttk.Style()
    style.theme_use("clam")

    style.configure("TLabel",
                    font=("Segoe UI", 11),
                    background="#f0f2f5")

    style.configure("TButton",
                    font=("Segoe UI", 10, "bold"),
                    padding=8)

    style.configure("Treeview",
                    font=("Segoe UI", 10),
                    rowheight=28)

    style.configure("Treeview.Heading",
                    font=("Segoe UI", 10, "bold"))

    style.configure("Custom.TEntry",
                    fieldbackground="#f9fafc")

    style.configure("Custom.TCombobox",
                    fieldbackground="#f9fafc")

    # ---------- Header ----------
    header = Frame(root, bg="#1f6aa5", height=70)
    header.pack(fill=X)

    Label(header,
          text="Payment Management Dashboard",
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
          text="Payment Details",
          font=("Segoe UI", 14, "bold"),
          bg="white").grid(row=0, columnspan=2, pady=15)

    labels = ["Purchase ID", "Bill Number", "Payment Type",
              "Payment Status", "Amount", "Payment Date", "Remark"]

    for i, text in enumerate(labels):
        ttk.Label(form_frame, text=text).grid(row=i+1, column=0, sticky=W, pady=8)

    cursor.execute("SELECT purchase_id, bill_number FROM purchase")
    purchase_data = cursor.fetchall()
    bill_dict = {pid: bill for pid, bill in purchase_data}

    ttk.Combobox(form_frame, textvariable=purchase_id_var,
                 values=list(bill_dict.keys()),
                 state="readonly", width=28,
                 style="Custom.TCombobox").grid(row=1, column=1)

    ttk.Combobox(form_frame, textvariable=bill_number_var,
                 values=list(bill_dict.values()),
                 state="readonly", width=28,
                 style="Custom.TCombobox").grid(row=2, column=1)

    ttk.Combobox(form_frame, textvariable=payment_type_var,
                 values=["Cash", "UPI", "Bank Transfer", "Cheque"],
                 state="readonly", width=28,
                 style="Custom.TCombobox").grid(row=3, column=1)

    ttk.Combobox(form_frame, textvariable=payment_status_var,
                 values=["Paid", "Pending", "Partial"],
                 state="readonly", width=28,
                 style="Custom.TCombobox").grid(row=4, column=1)

    ttk.Entry(form_frame, textvariable=amount_var,
              width=30, style="Custom.TEntry").grid(row=5, column=1)

    ttk.Entry(form_frame, textvariable=payment_date_var,
              width=30, style="Custom.TEntry").grid(row=6, column=1)

    remark_text = Text(form_frame, width=23, height=3,
                       font=("Segoe UI", 10), bg="#f9fafc")
    remark_text.grid(row=7, column=1)

    # ---------- Buttons ----------
    button_frame = Frame(form_frame, bg="white")
    button_frame.grid(row=8, columnspan=2, pady=20)

    ttk.Button(button_frame, text="Save", command=save_payment_data).grid(row=0, column=0, padx=5)
    ttk.Button(button_frame, text="Update", command=on_update).grid(row=0, column=1, padx=5)
    ttk.Button(button_frame, text="Delete", command=on_delete).grid(row=0, column=2, padx=5)
    ttk.Button(button_frame, text="Clear", command=clear_data).grid(row=0, column=3, padx=5)
    ttk.Button(button_frame, text="Analysis", command=data_analysis).grid(row=0, column=4, padx=5)
    ttk.Button(button_frame, text="Back", command=move_back).grid(row=0, column=5, padx=5)

    # ---------- Summary ----------
    total_payment = Label(form_frame, font=("Segoe UI", 10, "bold"), bg="white")
    total_payment.grid(row=9, columnspan=2, pady=3)

    total_amount = Label(form_frame, font=("Segoe UI", 10, "bold"), bg="white")
    total_amount.grid(row=10, columnspan=2, pady=3)

    max_amount = Label(form_frame, font=("Segoe UI", 10, "bold"), bg="white")
    max_amount.grid(row=11, columnspan=2, pady=3)

    min_amount = Label(form_frame, font=("Segoe UI", 10, "bold"), bg="white")
    min_amount.grid(row=12, columnspan=2, pady=3)

    # ---------- Right Frame ----------
    data_frame = Frame(main_frame, bg="white")
    data_frame.pack(side=RIGHT, fill=BOTH, expand=True, padx=10)

    Label(data_frame,
          text="Payment Records",
          font=("Segoe UI", 14, "bold"),
          bg="white").pack(pady=10)

    columns = ("ID", "Purchase ID", "Bill No", "Type",
               "Status", "Amount", "Date", "Remark")

    tree = ttk.Treeview(data_frame,
                        columns=columns,
                        show="headings")

    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=120)

    tree.pack(fill=BOTH, expand=True)

    scrollbar = ttk.Scrollbar(data_frame,
                              orient=VERTICAL,
                              command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side=RIGHT, fill=Y)

    tree.bind("<<TreeviewSelect>>", on_select)

    fetch_data()
    summary_data()

    root.mainloop()