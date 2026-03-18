import tkinter as tk
from tkinter import *
from tkinter import ttk, messagebox
from tkinter import scrolledtext
import sqlite3
from datetime import date
import pandas as pd
import dashboard
import sell_chatbot

sell_id = None

def open_sell():
    global sell_id

    conn = sqlite3.connect("ERP_Billing.db")
    cursor = conn.cursor()

    root = tk.Tk()
    root.title("Sell Management Dashboard")
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
    bill_no_var = StringVar()
    buyer_id_var = StringVar()
    user_id_var = StringVar()
    sell_date_var = StringVar(value=date.today().strftime("%Y-%m-%d"))
    product_id_var = StringVar()
    qty_var = StringVar()
    price_var = StringVar()
    gst_rate_var = StringVar()
    gst_amount_var = StringVar()
    total_amount_var = StringVar()
    payment_term_var = StringVar()

    # ---------- Functions ----------

    def calculate_amount(*args):
        try:
            qty = float(qty_var.get())
            price = float(price_var.get())
            gst = float(gst_rate_var.get())

            subtotal = qty * price
            gst_amt = subtotal * gst / 100
            total = subtotal + gst_amt

            gst_amount_var.set(round(gst_amt, 2))
            total_amount_var.set(round(total, 2))
        except:
            pass

    def save_sell():
        if bill_no_var.get() == "" or product_id_var.get() == "":
            messagebox.showerror("ERP Billing", "Bill No & Product required")
            return

        cursor.execute("""
            INSERT INTO sell (
                bill_number, buyer_id, user_id, sell_date,
                product_id, product_quantity, product_price,
                product_gst_rate, gst_amount, total_amount,
                payment_term, remark
            )
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            bill_no_var.get(),
            buyer_id_var.get(),
            user_id_var.get(),
            sell_date_var.get(),
            product_id_var.get(),
            qty_var.get(),
            price_var.get(),
            gst_rate_var.get(),
            gst_amount_var.get(),
            total_amount_var.get(),
            payment_term_var.get(),
            remark_text.get("1.0", END).strip()
        ))

        conn.commit()
        fetch_data()
        clear_sell()
        messagebox.showinfo("ERP Billing", "Sell saved successfully")

    def clear_sell():
        global sell_id
        sell_id = None

        bill_no_var.set("")
        buyer_id_var.set("")
        user_id_var.set("")
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
        for row in rows:
            tree.insert("", END, values=row)

    def on_select(event):
        global sell_id
        selected = tree.focus()
        if selected:
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
            messagebox.showerror("ERP Billing", "Select record to update")
            return

        cursor.execute("""
            UPDATE sell SET
                bill_number=?, buyer_id=?, user_id=?, sell_date=?,
                product_id=?, product_quantity=?, product_price=?,
                product_gst_rate=?, gst_amount=?, total_amount=?,
                payment_term=?, remark=?
            WHERE sell_id=?
        """, (
            bill_no_var.get(),
            buyer_id_var.get(),
            user_id_var.get(),
            sell_date_var.get(),
            product_id_var.get(),
            qty_var.get(),
            price_var.get(),
            gst_rate_var.get(),
            gst_amount_var.get(),
            total_amount_var.get(),
            payment_term_var.get(),
            remark_text.get("1.0", END).strip(),
            sell_id
        ))

        conn.commit()
        fetch_data()
        clear_sell()
        

    def on_delete():
        global sell_id
        if not sell_id:
            messagebox.showerror("ERP Billing", "Select record to delete")
            return

        cursor.execute("DELETE FROM sell WHERE sell_id=?", (sell_id,))
        conn.commit()

        fetch_data()
        clear_sell()
        

    # ---------- Analysis ----------
    def data_analysis():
        df = pd.read_sql_query("""
        SELECT s.sell_id,
               s.buyer_id,
               s.product_id,
               s.product_quantity,
               s.product_price,
               s.total_amount,
               p.product_name,
               p.product_category,
               b.buyer_company_name
        FROM sell as s
        LEFT JOIN product p ON s.product_id = p.product_id
        LEFT JOIN buyer b ON s.buyer_id = b.buyer_id
    """, conn)

        if df.empty:
            messagebox.showinfo("ERP", "No data available for analysis.")
            return
        
        
        # ------------------------------------------------
        # Product Sales Analysis
        # ------------------------------------------------
        grouped_product = df.groupby("product_name")["product_quantity"].sum().round(2)
        
        top_product = grouped_product.idxmax()
        top_product_qty = grouped_product.max()
        
        least_product = grouped_product.idxmin()
        least_product_qty = grouped_product.min()
        
        
        # ------------------------------------------------
        # Buyer Quantity Analysis
        # ------------------------------------------------
        grouped_buyer_qty = df.groupby("buyer_company_name")["product_quantity"].sum().round(2)
        
        top_buyer = grouped_buyer_qty.idxmax()
        top_buyer_qty = grouped_buyer_qty.max()
        
        least_buyer = grouped_buyer_qty.idxmin()
        least_buyer_qty = grouped_buyer_qty.min()
        
        
        # ------------------------------------------------
        # Buyer Business Value
        # ------------------------------------------------
        grouped_amount = df.groupby("buyer_company_name")["total_amount"].sum().round(2)
        
        best_buyer = grouped_amount.idxmax()
        best_amount = grouped_amount.max()
        
        low_buyer = grouped_amount.idxmin()
        low_amount = grouped_amount.min()
        
        
        # ------------------------------------------------
        # Price Analysis
        # ------------------------------------------------
        highest_price_row = df.loc[df["product_price"].idxmax()]
        lowest_price_row = df.loc[df["product_price"].idxmin()]
        
        
        # =================================================
        # FORMAT OUTPUT
        # =================================================
        data = ""
        data += "╔══════════════════════════════════════╗\n"
        data += "║          ERP SALES ANALYSIS          ║\n"
        data += "╚══════════════════════════════════════╝\n\n"
        
        
        # ---------- Product Sales ----------
        data += "PRODUCT SALES ANALYSIS\n"
        data += "------------------------------------------------\n"
        data += f"Top Selling Product        : {top_product}\n"
        data += f"Total Quantity Sold        : {top_product_qty}\n\n"
        
        data += f"Least Selling Product      : {least_product}\n"
        data += f"Total Quantity Sold        : {least_product_qty}\n\n"
        
        
        # ---------- Buyer Quantity ----------
        data += "BUYER PURCHASE ANALYSIS\n"
        data += "------------------------------------------------\n"
        data += f"Top Buying Party           : {top_buyer}\n"
        data += f"Total Quantity Purchased   : {top_buyer_qty}\n\n"
        
        data += f"Least Buying Party         : {least_buyer}\n"
        data += f"Total Quantity Purchased   : {least_buyer_qty}\n\n"
        
        
        # ---------- Buyer Value ----------
        data += "BUYER BUSINESS VALUE\n"
        data += "------------------------------------------------\n"
        data += f"Most Valuable Buyer        : {best_buyer}\n"
        data += f"Total Purchase Value       : ₹ {best_amount}\n\n"
        
        data += f"Least Valuable Buyer       : {low_buyer}\n"
        data += f"Total Purchase Value       : ₹ {low_amount}\n\n"
        
        
        # ---------- Price Analysis ----------
        data += "PRODUCT PRICE ANALYSIS\n"
        data += "------------------------------------------------\n"
        data += f"Highest Price Product      : {highest_price_row['product_name']}\n"
        data += f"Price                      : ₹ {highest_price_row['product_price']}\n\n"
        
        data += f"Lowest Price Product       : {lowest_price_row['product_name']}\n"
        data += f"Price                      : ₹ {lowest_price_row['product_price']}\n\n"
        
        data += "=========================================="
        
        # ---------- Show Result ----------
        messagebox.showinfo("ERP Data Analysis", data)

    # ---------- Chatbot Response ----------
    def chatbot_response():
        response = sell_chatbot.chatbot_response(entry_chat.get())
        add_message("user",entry_chat.get())
        entry_chat.delete(0, tk.END)
        add_message("",response)

    #---- style the font of chatbot ----
    def add_message(sender, message):
        chat_display.tag_config("user_tag",
                        font=("Segoe UI", 10, "bold"),
                        foreground="#1f6aa5")

        chat_display.tag_config("bot_tag",
                            font=("Segoe UI", 10, "bold"),
                            foreground="#2e7d32")
        
        chat_display.config(state="normal")

        if sender == "user":
            chat_display.insert(END, f"             \nYou:\n", "user_tag")
            chat_display.insert(END, f"{message}\n")

        else:
            chat_display.insert(END, f"\nMitra:\n", "bot_tag")
            chat_display.insert(END, f"{message}\n")

        chat_display.insert(END, "\n")
        chat_display.config(state="disabled")
        chat_display.yview(END)

    # # ---------- Summary ----------
    # def sell_summary():
    #     df = pd.read_sql_query("SELECT * FROM sell", conn)

    #     if df.empty:
    #         total_label.config(text="Total Sell Records : 0")
    #         return

    #     total_label.config(text=f"Total Sell Records : {len(df)}")
    #     total_qty_label.config(text=f"Total Quantity : {df['product_quantity'].sum()}")
    #     total_amount_label.config(text=f"Total Amount : ₹ {round(df['total_amount'].sum(),2)}")

    def move_back():
        root.destroy()
        dashboard.open_dashboard()

    # ---------- Header ----------
    header = Frame(root, bg="#1f6aa5", height=70)
    header.pack(fill=X)

    Label(header,
          text="Sell Management Dashboard",
          font=("Segoe UI", 22, "bold"),
          bg="#1f6aa5",
          fg="white").pack(pady=15)

    # ---------- Main Layout ----------
    main_frame = Frame(root, bg="#f0f2f5")
    main_frame.pack(fill=BOTH, expand=True, padx=20, pady=20)

    # ---------- Left Form ----------
    form_frame = Frame(main_frame, bg="white")
    form_frame.pack(side=LEFT, fill=Y, padx=10, ipadx=15, ipady=15)

    Label(form_frame,
          text="Sell Details",
          font=("Segoe UI", 14, "bold"),
          bg="white").grid(row=0, columnspan=2, pady=15)

    labels = [
        "Bill Number", "Buyer", "User", "Sell Date",
        "Product", "Quantity", "Price",
        "GST Rate", "GST Amount", "Total Amount",
        "Payment Term"
    ]

    for i, text in enumerate(labels):
        ttk.Label(form_frame, text=text).grid(row=i+1, column=0, sticky=W, pady=8)

    # ---------- get the buyer name, user name, product_name ----------

    # ---------- Product name list ----------
    cursor.execute("SELECT product_id, product_name FROM product")
    product_data = cursor.fetchall()

    product_dict = {proid:pro_name for proid, pro_name in product_data}
    product_name_list = list(set(product_dict.values()))

    # ---------- Buyer name list ----------
    cursor.execute("SELECT buyer_id, buyer_company_name FROM buyer")
    buyer_data = cursor.fetchall()

    buyer_dict = {bid:b_name for bid, b_name in buyer_data}
    buyer_name_list = list(set(buyer_dict.values()))

    ttk.Entry(form_frame, textvariable=bill_no_var, width=30).grid(row=1, column=1)
    ttk.Combobox(form_frame, textvariable=buyer_id_var,values=buyer_name_list, state="readonly", width=27).grid(row=2, column=1)
    ttk.Entry(form_frame, textvariable=user_id_var, width=30).grid(row=3, column=1)
    ttk.Entry(form_frame, textvariable=sell_date_var, width=30).grid(row=4, column=1)
    ttk.Combobox(form_frame, textvariable=product_id_var,values=product_name_list, state="readonly", width=27).grid(row=5, column=1)
    ttk.Entry(form_frame, textvariable=qty_var, width=30).grid(row=6, column=1)
    ttk.Entry(form_frame, textvariable=price_var, width=30).grid(row=7, column=1)
    ttk.Entry(form_frame, textvariable=gst_rate_var, width=30).grid(row=8, column=1)
    ttk.Entry(form_frame, textvariable=gst_amount_var, width=30, state="readonly").grid(row=9, column=1)
    ttk.Entry(form_frame, textvariable=total_amount_var, width=30, state="readonly").grid(row=10, column=1)
    ttk.Entry(form_frame, textvariable=payment_term_var, width=30).grid(row=11, column=1)

    ttk.Label(form_frame, text="Remark").grid(row=12, column=0, sticky=NW)
    remark_text = Text(form_frame, width=23, height=4, font=("Segoe UI", 10))
    remark_text.grid(row=12, column=1)

    qty_var.trace("w", calculate_amount)
    price_var.trace("w", calculate_amount)
    gst_rate_var.trace("w", calculate_amount)

    # ---------- Buttons ----------
    button_frame = Frame(form_frame, bg="white")
    button_frame.grid(row=13, columnspan=2, pady=20)

    ttk.Button(button_frame, text="Save", command=save_sell).grid(row=0, column=0, padx=5)
    ttk.Button(button_frame, text="Update", command=on_update).grid(row=0, column=1, padx=5)
    ttk.Button(button_frame, text="Delete", command=on_delete).grid(row=0, column=2, padx=5)
    ttk.Button(button_frame, text="Clear", command=clear_sell).grid(row=0, column=3, padx=5)
    ttk.Button(button_frame, text="Analysis", command=data_analysis).grid(row=0, column=4, padx=5)
    ttk.Button(button_frame, text="Back", command=move_back).grid(row=0, column=5, padx=5)

    # ---------- Right Tree ----------
    data_frame = Frame(main_frame, bg="white")
    data_frame.pack(side=RIGHT, fill=BOTH, expand=True, padx=10)

    Label(data_frame,
          text="Sell Records",
          font=("Segoe UI", 14, "bold"),
          bg="white").pack(pady=10)

    columns = ("ID","Bill","Buyer","User","Date","Product","Qty","Price","GST%","GST Amt","Total","Payment","Remark")
    tree = ttk.Treeview(data_frame, columns=columns, show="headings")

    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=100)

    tree.pack(fill=BOTH, expand=True)

    scrollbar = ttk.Scrollbar(data_frame, orient=VERTICAL, command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side=RIGHT, fill=Y)

    tree.bind("<<TreeviewSelect>>", on_select)

    # # ---------- Summary ----------
    # summary_frame = Frame(root, bg="#f0f2f5")
    # summary_frame.pack(pady=10)

    # total_label = Label(summary_frame, font=("Segoe UI", 11, "bold"), bg="#f0f2f5")
    # total_label.pack()

    # total_qty_label = Label(summary_frame, font=("Segoe UI", 10), bg="#f0f2f5")
    # total_qty_label.pack()

    # total_amount_label = Label(summary_frame, font=("Segoe UI", 10), bg="#f0f2f5")
    # total_amount_label.pack()

    # =============================
    # -------- CHATBOT UI ---------
    # =============================
    # ---------- Chatbot Frame (Right Side or Bottom Section) ----------
    chat_frame = Frame(main_frame, bg="white")
    chat_frame.pack(side=BOTTOM, fill=BOTH, expand=True, padx=10, pady=10)

    # ---------- Header ----------
    chat_header = Frame(chat_frame, bg="#1f6aa5", height=40)
    chat_header.pack(fill=X)

    Label(chat_header,
          text="🤖 ERP AI Assistant",
          font=("Segoe UI", 12, "bold"),
          bg="#1f6aa5",
          fg="white").pack(pady=5)

    # ---------- Chat Display ----------
    chat_display = scrolledtext.ScrolledText(
        chat_frame,
        height=12,
        font=("Segoe UI", 10),
        wrap=WORD,
        bd=0,
        relief="flat",
        bg="#f9fafb"
    )

    chat_display.pack(fill=BOTH, expand=True, padx=10, pady=10)
    chat_display.config(state="disabled")

    # ---------- Input Section ----------
    input_frame = Frame(chat_frame, bg="white")
    input_frame.pack(fill=X, padx=10, pady=10)

    entry_chat = ttk.Entry(
        input_frame,
        font=("Segoe UI", 10),
        width=50
    )
    entry_chat.pack(side=LEFT, fill=X, expand=True, padx=(0, 10))

    ttk.Button(
        input_frame,
        text="Send",
        width=12,
        command=chatbot_response
    ).pack(side=RIGHT)

    fetch_data()
    # sell_summary()                                            

    root.mainloop()
