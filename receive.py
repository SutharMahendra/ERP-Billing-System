import tkinter as tk
from tkinter import *
from tkinter import ttk, messagebox
import sqlite3
from datetime import date
import pandas as pd
import dashboard

receive_id = None

def open_receive():
    global receive_id

    conn = sqlite3.connect("ERP_Billing.db")
    cursor = conn.cursor()

    root = tk.Tk()
    root.title("Receive Management Dashboard")
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
    sell_id_var = StringVar()
    bill_number_var = StringVar()
    receive_type_var = StringVar()
    receive_status_var = StringVar()
    amount_var = StringVar()
    receive_date_var = StringVar(value=date.today().strftime("%Y-%m-%d"))

    # ---------- Functions ----------

    def save_receive():
        if sell_id_var.get() == "":
            messagebox.showerror("ERP Billing", "Sell ID required")
            return

        cursor.execute("""
            INSERT INTO receive (
                sell_id, bill_number, receive_type,
                receive_status, amount, receive_date, remark
            )
            VALUES (?,?,?,?,?,?,?)
        """, (
            sell_id_var.get(),
            bill_number_var.get(),
            receive_type_var.get(),
            receive_status_var.get(),
            amount_var.get(),
            receive_date_var.get(),
            remark_text.get("1.0", END).strip()
        ))

        conn.commit()
        fetch_data()
        clear_receive()
        receive_summary()
        messagebox.showinfo("ERP Billing", "Receive saved successfully")

    def clear_receive():
        global receive_id
        receive_id = None

        sell_id_var.set("")
        bill_number_var.set("")
        receive_type_var.set("")
        receive_status_var.set("")
        amount_var.set("")
        receive_date_var.set(date.today().strftime("%Y-%m-%d"))
        remark_text.delete("1.0", END)

    def fetch_data():
        tree.delete(*tree.get_children())
        cursor.execute("SELECT * FROM receive")
        rows = cursor.fetchall()
        for row in rows:
            tree.insert("", END, values=row)

    def on_select(event):
        global receive_id
        selected = tree.focus()
        if selected:
            data = tree.item(selected)["values"]
            receive_id = data[0]

            sell_id_var.set(data[1])
            bill_number_var.set(data[2])
            receive_type_var.set(data[3])
            receive_status_var.set(data[4])
            amount_var.set(data[5])
            receive_date_var.set(data[6])

            remark_text.delete("1.0", END)
            remark_text.insert(END, data[7])

    def on_update():
        global receive_id
        if not receive_id:
            messagebox.showerror("ERP Billing", "Select record to update")
            return

        cursor.execute("""
            UPDATE receive SET
                sell_id=?, bill_number=?, receive_type=?,
                receive_status=?, amount=?, receive_date=?, remark=?
            WHERE receive_id=?
        """, (
            sell_id_var.get(),
            bill_number_var.get(),
            receive_type_var.get(),
            receive_status_var.get(),
            amount_var.get(),
            receive_date_var.get(),
            remark_text.get("1.0", END).strip(),
            receive_id
        ))

        conn.commit()
        fetch_data()
        clear_receive()
        receive_summary()

    def on_delete():
        global receive_id
        if not receive_id:
            messagebox.showerror("ERP Billing", "Select record to delete")
            return

        cursor.execute("DELETE FROM receive WHERE receive_id=?", (receive_id,))
        conn.commit()

        fetch_data()
        clear_receive()
        receive_summary()

    # ---------- Data Analysis ----------
    def data_analysis():
        df = pd.read_sql_query("""
        SELECT b.buyer_id,
               b.buyer_company_name,
               r.receive_type,
               r.receive_status,
               r.receive_date,
               r.amount
        FROM buyer as b
        LEFT JOIN sell s ON b.buyer_id = s.buyer_id
        LEFT JOIN receive r ON s.sell_id = r.sell_id
        """, conn)

        if df.empty:
            messagebox.showinfo("ERP", "No data available for analysis.")
            return
        
    
        # ------------------------------------------------
        # Buyer Payment Analysis
        # ------------------------------------------------
        buyer_total = df.groupby("buyer_company_name")["amount"].sum().round(2)
        
        top_buyer = buyer_total.idxmax()
        top_amount = buyer_total.max()
        
        low_buyer = buyer_total.idxmin()
        low_amount = buyer_total.min()
        
        
        # ------------------------------------------------
        # Receive Type Analysis
        # ------------------------------------------------
        receive_type_summary = df.groupby("receive_type")["amount"].sum().round(2)
        
        
        # ------------------------------------------------
        # Receive Status Analysis
        # ------------------------------------------------
        receive_status_summary = df.groupby("receive_status")["amount"].sum().round(2)
        
        
        # =================================================
        # FORMAT OUTPUT
        # =================================================
        data = ""
        data += "╔══════════════════════════════════════╗\n"
        data += "║         ERP BUYER ANALYSIS           ║\n"
        data += "╚══════════════════════════════════════╝\n\n"
        
        
        # ---------- Buyer Payment ----------
        data += "BUYER PAYMENT SUMMARY\n"
        data += "------------------------------------------------\n"
        data += f"Maximum Receive From Buyer   : {top_buyer}\n"
        data += f"Total Amount Received        : ₹ {top_amount}\n\n"
        
        data += f"Minimum Receive From Buyer   : {low_buyer}\n"
        data += f"Total Amount Received        : ₹ {low_amount}\n\n"
        
        
        # ---------- Receive Type ----------
        data += "RECEIVE TYPE ANALYSIS\n"
        data += "------------------------------------------------\n"
        data += f"{'Receive Type':<20}{'Total Amount'}\n"
        data += "------------------------------------------------\n"
        
        for rtype, amt in receive_type_summary.items():
            data += f"{rtype:<20}₹ {amt}\n"
        
        data += "\n"
        
        
        # ---------- Receive Status ----------
        data += "RECEIVE STATUS ANALYSIS\n"
        data += "------------------------------------------------\n"
        data += f"{'Status':<20}{'Total Amount'}\n"
        data += "------------------------------------------------\n"
        
        for status, amt in receive_status_summary.items():
            data += f"{status:<20}₹ {amt}\n"
        
        data += "\n=========================================="
        
        # ---------- Show Result ----------
        messagebox.showinfo("ERP Data Analysis", data)

    # ---------- Summary ----------
    def receive_summary():
        # ----------  Total Transactoins ----------
        cursor.execute("SELECT COUNT(receive_id) FROM receive")
        total = cursor.fetchone()[0]

        if total == None:
            total = 0 

        total_payment.config(text=f"Total Transactions : {total}")

        # ---------- total amount ----------
        cursor.execute("SELECT SUM(amount) FROM receive")
        total = cursor.fetchone()[0]

        if total == None:
            total = 0 

        total_amount.config(text=f"Total Transaction Amount : {total}")

        # ---------- Maximum amount ----------
        cursor.execute("SELECT MAX(amount) FROM receive")
        max = cursor.fetchone()[0]

        if max == None:
            max = 0 

        max_amount.config(text=f"Maximum Transaction Amount  : {max}")

        # ---------- minimum amount ----------
        cursor.execute("SELECT MIN(amount) FROM receive")
        min = cursor.fetchone()[0]

        if min == None:
            min = 0 

        min_amount.config(text=f"Minimum Transaction Amount : {min}")

    def move_back():
        root.destroy()
        dashboard.open_dashboard()

    # ---------- Header ----------
    header = Frame(root, bg="#1f6aa5", height=70)
    header.pack(fill=X)

    Label(header,
          text="Receive Management Dashboard",
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
          text="Receive Details",
          font=("Segoe UI", 14, "bold"),
          bg="white").grid(row=0, columnspan=2, pady=15)

    labels = [
        "Sell ID", "Bill Number", "Receive Type",
        "Receive Status", "Amount", "Receive Date"
    ]

    for i, text in enumerate(labels):
        ttk.Label(form_frame, text=text).grid(row=i+1, column=0, sticky=W, pady=8)

    # ---------- Get the data for sell id and bill no  ----------
    cursor.execute("SELECT sell_id, bill_number FROM sell")

    seller_data = cursor.fetchall()

    sell_id_dict = {sid:billno for sid, billno in seller_data}

    sell_id_list = list(set(sell_id_dict.keys()))
    bill_no_list = list(dict.fromkeys(sell_id_dict.values()))

    ttk.Combobox(form_frame, textvariable=sell_id_var,values=sell_id_list, state="readonly", width=27).grid(row=1, column=1, pady=5)
    ttk.Combobox(form_frame, textvariable=bill_number_var, values=bill_no_list, state="readonly", width=27).grid(row=2, column=1, pady=5)

    ttk.Combobox(form_frame, textvariable=receive_type_var,
                 values=["Cash", "UPI", "Bank Transfer", "Cheque"],
                 state="readonly", width=28).grid(row=3, column=1)

    ttk.Combobox(form_frame, textvariable=receive_status_var,
                 values=["Received", "Pending", "Partial"],
                 state="readonly", width=28).grid(row=4, column=1)

    ttk.Entry(form_frame, textvariable=amount_var, width=30).grid(row=5, column=1)
    ttk.Entry(form_frame, textvariable=receive_date_var, width=30).grid(row=6, column=1)

    ttk.Label(form_frame, text="Remark").grid(row=7, column=0, sticky=NW)
    remark_text = Text(form_frame, width=23, height=4, font=("Segoe UI", 10))
    remark_text.grid(row=7, column=1)

    # ---------- Buttons ----------
    button_frame = Frame(form_frame, bg="white")
    button_frame.grid(row=8, columnspan=2, pady=20)

    ttk.Button(button_frame, text="Save", command=save_receive).grid(row=0, column=0, padx=5)
    ttk.Button(button_frame, text="Update", command=on_update).grid(row=0, column=1, padx=5)
    ttk.Button(button_frame, text="Delete", command=on_delete).grid(row=0, column=2, padx=5)
    ttk.Button(button_frame, text="Clear", command=clear_receive).grid(row=0, column=3, padx=5)
    ttk.Button(button_frame, text="Analysis", command=data_analysis).grid(row=0, column=4, padx=5)
    ttk.Button(button_frame, text="Back", command=move_back).grid(row=0, column=5, padx=5)

    # ---------- Right Frame ----------
    data_frame = Frame(main_frame, bg="white")
    data_frame.pack(side=RIGHT, fill=BOTH, expand=True, padx=10)

    Label(data_frame,
          text="Receive Records",
          font=("Segoe UI", 14, "bold"),
          bg="white").pack(pady=10)

    columns = ("ID","Sell ID","Bill No","Type","Status","Amount","Date","Remark")
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

    total_payment = tk.Label(
    summary_frame,
    font=("Segoe UI", 11, "bold"),
    bg="#f0f2f5"
    )
    total_payment.pack(anchor="w", pady=2)

    total_amount = tk.Label(
        summary_frame,
        font=("Segoe UI", 11, "bold"),
        bg="#f0f2f5"
    )
    total_amount.pack(anchor="w", pady=2)

    min_amount = tk.Label(
        summary_frame,
        font=("Segoe UI", 11, "bold"),
        bg="#f0f2f5"
    )
    min_amount.pack(anchor="w", pady=2)

    max_amount = tk.Label(
        summary_frame,
        font=("Segoe UI", 11, "bold"),
        bg="#f0f2f5"
    )
    max_amount.pack(anchor="w", pady=2)

    fetch_data()
    receive_summary()

    root.mainloop()