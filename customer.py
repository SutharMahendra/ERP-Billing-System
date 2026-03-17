import tkinter as tk
from tkinter import *
from tkinter import ttk, messagebox
import sqlite3
import pandas as pd
import dashboard
from tkinter import scrolledtext
import customer_chatbot

selected_id = None

def open_customer():

    # ---------- Database ----------
    conn = sqlite3.connect("ERP_Billing.db")
    cursor = conn.cursor()

    # ---------- Main Window ----------
    root = tk.Tk()
    root.title("ERP Billing System - Buyer Management")
    root.state("zoomed")
    root.configure(bg="#f0f2f5")

    # ---------- Variables ----------
    buyer_company_var = StringVar()
    buyer_name_var = StringVar()
    buyer_phone_var = StringVar()
    buyer_email_var = StringVar()
    buyer_city_var = StringVar()
    buyer_gst_var = StringVar()

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
    

    # ---------- Header ----------
    header = Frame(root, bg="#1f6aa5", height=70)
    header.pack(fill=X)

    Label(header,
          text="Buyer Management Dashboard",
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
          text="Buyer Details",
          font=("Segoe UI", 14, "bold"),
          bg="white").grid(row=0, columnspan=2, pady=15)

    labels = [
        "Company Name",
        "Buyer Name",
        "Phone Number",
        "Email",
        "Address",
        "City",
        "GST Number"
    ]

    for i, text in enumerate(labels):
        ttk.Label(form_frame, text=text).grid(row=i+1, column=0, sticky=W, pady=8)

    ttk.Entry(form_frame, textvariable=buyer_company_var, width=30).grid(row=1, column=1)
    ttk.Entry(form_frame, textvariable=buyer_name_var, width=30).grid(row=2, column=1)
    ttk.Entry(form_frame, textvariable=buyer_phone_var, width=30).grid(row=3, column=1)
    ttk.Entry(form_frame, textvariable=buyer_email_var, width=30).grid(row=4, column=1)

    buyer_address_text = Text(form_frame, width=23, height=3, font=("Segoe UI", 10))
    buyer_address_text.grid(row=5, column=1)

    city_list = ["Ahmedabad", "Surat", "Jaipur", "Delhi",
                 "Mumbai", "Pune", "Indore", "Other"]

    ttk.Combobox(form_frame,
                 textvariable=buyer_city_var,
                 values=city_list,
                 state="readonly",
                 width=27).grid(row=6, column=1)

    ttk.Entry(form_frame, textvariable=buyer_gst_var, width=30).grid(row=7, column=1)

    # ---------- Buttons ----------
    button_frame = Frame(form_frame, bg="white")
    button_frame.grid(row=8, columnspan=2, pady=20)

    # ---------- Right Frame ----------
    data_frame = Frame(main_frame, bg="white")
    data_frame.pack(side=RIGHT, fill=BOTH, expand=True, padx=10)

    Label(data_frame,
          text="Buyer Records",
          font=("Segoe UI", 14, "bold"),
          bg="white").pack(pady=10)

    columns = ("ID", "Company", "Name", "Phone", "Email", "Address", "City", "GST")
    tree = ttk.Treeview(data_frame, columns=columns, show="headings")

    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=120)

    tree.pack(fill=BOTH, expand=True)

    scrollbar = ttk.Scrollbar(data_frame, orient=VERTICAL, command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side=RIGHT, fill=Y)

    # ---------- Functions ----------

    def fetch_data():
        for row in tree.get_children():
            tree.delete(row)

        cursor.execute("SELECT * FROM buyer")
        rows = cursor.fetchall()

        for row in rows:
            tree.insert("", END, values=row)

        summary_data()

    def save_customer_data():
        name = buyer_name_var.get()
        phone = buyer_phone_var.get()
        address = buyer_address_text.get("1.0", tk.END).strip()

        if name == "" or phone == "" or address == "":
            messagebox.showerror("ERP System", "Please fill required fields!")
            return

        cursor.execute("""
            INSERT INTO buyer
            (buyer_company_name, buyer_name, buyer_phone_no,
             buyer_email, buyer_address, buyer_city, buyer_gst_number)
            VALUES (?,?,?,?,?,?,?)
        """, (
            buyer_company_var.get(),
            name,
            phone,
            buyer_email_var.get(),
            address,
            buyer_city_var.get(),
            buyer_gst_var.get()
        ))

        conn.commit()
        messagebox.showinfo("ERP", "Buyer Added Successfully")
        clear_data()
        fetch_data()

    def clear_data():
        global selected_id
        selected_id = None
        buyer_company_var.set("")
        buyer_name_var.set("")
        buyer_phone_var.set("")
        buyer_email_var.set("")
        buyer_city_var.set("")
        buyer_gst_var.set("")
        buyer_address_text.delete("1.0", tk.END)

    def on_select(event):
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

    def on_update():
        if selected_id is None:
            messagebox.showerror("ERP", "Select record to update!")
            return

        cursor.execute("""
            UPDATE buyer SET
            buyer_company_name=?,
            buyer_name=?,
            buyer_phone_no=?,
            buyer_email=?,
            buyer_address=?,
            buyer_city=?,
            buyer_gst_number=?
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
        messagebox.showinfo("ERP", "Record Updated Successfully")
        fetch_data()
        clear_data()

    def on_delete():
        if selected_id is None:
            messagebox.showerror("ERP", "Select record to delete!")
            return

        confirm = messagebox.askyesno("ERP", "Are you sure?")
        if confirm:
            cursor.execute("DELETE FROM buyer WHERE buyer_id=?", (selected_id,))
            conn.commit()
            messagebox.showinfo("ERP", "Record Deleted")
            fetch_data()
            clear_data()

    def summary_data():
        cursor.execute("SELECT COUNT(*) FROM buyer")
        total = cursor.fetchone()[0]
        total_label.config(text=f"Total Buyers : {total}")

    def data_analysis():
        df = pd.read_sql_query("SELECT * FROM buyer", conn)

        if df.empty:
            messagebox.showinfo("ERP", "No data available for analysis.")
            return


        # ------------------------------------------------
        # Buyer City Distribution
        # ------------------------------------------------
        grouped = df.groupby("buyer_city").size().reset_index(name="buyer_count")

        top_row = grouped.loc[grouped["buyer_count"].idxmax()]
        top_city = top_row["buyer_city"]
        top_count = top_row["buyer_count"]

        low_row = grouped.loc[grouped["buyer_count"].idxmin()]
        low_city = low_row["buyer_city"]
        low_count = low_row["buyer_count"]


        # ------------------------------------------------
        # GST / NON GST Buyers
        # ------------------------------------------------
        gst_count = df["buyer_gst_number"].notna().sum()
        non_gst_count = df["buyer_gst_number"].isna().sum()

        total_buyers = len(df)


        # =================================================
        # FORMAT OUTPUT
        # =================================================
        data = ""
        data += "╔══════════════════════════════════════╗\n"
        data += "║          ERP BUYER ANALYSIS          ║\n"
        data += "╚══════════════════════════════════════╝\n\n"


        # ---------- Buyer City ----------
        data += "BUYER CITY DISTRIBUTION\n"
        data += "------------------------------------------------\n"
        data += f"City With Most Buyers      : {top_city}\n"
        data += f"Total Buyers               : {top_count}\n\n"

        data += f"City With Least Buyers     : {low_city}\n"
        data += f"Total Buyers               : {low_count}\n\n"


        # ---------- GST Analysis ----------
        data += "GST REGISTRATION ANALYSIS\n"
        data += "------------------------------------------------\n"
        data += f"Total Buyers               : {total_buyers}\n"
        data += f"GST Registered Buyers      : {gst_count}\n"
        data += f"Non-GST Buyers             : {non_gst_count}\n\n"

        data += "=========================================="

        messagebox.showinfo("ERP SYSTEM", data)

    def move_back():
        root.destroy()
        dashboard.open_dashboard()

    def chatbot_response():
        
        response = customer_chatbot.chatbot_response(entry_chat.get())
        add_message("user",entry_chat.get())
        entry_chat.delete(0, tk.END)
        add_message("",response)


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

    # ---------- Button Placement ----------
    ttk.Button(button_frame, text="Save", width=10, command=save_customer_data).grid(row=0, column=0, padx=5, pady=5)
    ttk.Button(button_frame, text="Update", width=10, command=on_update).grid(row=0, column=1, padx=5, pady=5)
    ttk.Button(button_frame, text="Delete", width=10, command=on_delete).grid(row=0, column=2, padx=5, pady=5)
    ttk.Button(button_frame, text="Clear", width=10, command=clear_data).grid(row=1, column=0, padx=5, pady=5)
    ttk.Button(button_frame, text="Analysis", width=10, command=data_analysis).grid(row=1, column=1, padx=5, pady=5)
    ttk.Button(button_frame, text="Back", width=10, command=move_back).grid(row=1, column=2, padx=5, pady=5)

    # ---------- Summary ----------
    total_label = Label(form_frame,
                        text="",
                        font=("Segoe UI", 11, "bold"),
                        bg="white",
                        fg="#1f6aa5")
    total_label.grid(row=9, columnspan=2, pady=10)

    tree.bind("<<TreeviewSelect>>", on_select)

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

    root.mainloop()